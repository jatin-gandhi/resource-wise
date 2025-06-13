"""Intent classification agent implementation."""

from enum import Enum
from typing import Any

import structlog
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.agents.base import BaseAgent
from app.ai.agents.query.agent import QueryAgent, QueryType  # Import QueryType from query agent
from app.ai.core.config import AIConfig
from app.core.config import settings
from app.schemas.ai import QueryRequest

logger = structlog.get_logger()


class IntentType(str, Enum):
    """Types of user intents."""

    DATABASE_QUERY = "database_query"  # User wants to query/search the database
    GENERAL_CONVERSATION = "general_conversation"  # General conversation/questions
    GREETING = "greeting"  # Greetings and pleasantries
    HELP_REQUEST = "help_request"  # User asking for help/instructions
    UNKNOWN = "unknown"  # Unable to determine intent


class StandardResponse:
    """Standardized response format for all intent types."""

    def __init__(
        self,
        intent: IntentType,
        response: str,
        requires_database: bool = False,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
        **kwargs,
    ):
        self.intent = intent
        self.response = response
        self.requires_database = requires_database
        self.success = success
        self.metadata = metadata or {}
        self.error = error

        # Add any additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "intent": self.intent,
            "response": self.response,
            "requires_database": self.requires_database,
            "success": self.success,
            "metadata": self.metadata,
        }

        if self.error:
            result["error"] = self.error

        # Add any additional attributes
        for key, value in self.__dict__.items():
            if key not in result:
                result[key] = value

        return result


class IntentAgent(BaseAgent):
    """Agent for classifying user intent and routing to appropriate handlers."""

    def __init__(self, config: AIConfig | None = None):
        """Initialize the intent agent.

        Args:
            config: AI configuration settings. If None, will use default config with settings.
        """
        if config is None:
            config = AIConfig(temperature=0.1)  # Low temperature for consistent classification

        super().__init__(config)

        # Initialize LLM for intent classification
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Initialize query agent for database operations
        self.query_agent = QueryAgent(config)

        # Intent classification prompt
        self.intent_classification_prompt = PromptTemplate(
            input_variables=["user_input", "context"],
            template="""You are an intelligent intent classifier for ResourceWise, an AI-powered resource allocation system.

Your job is to analyze user input and determine their intent from these categories:

1. **DATABASE_QUERY**: User wants to search, find, or query information from the database
   - Examples: "Find all developers with Python skills", "Show me project allocations", "Who is working on the mobile app?", "What skills does John have?", "List all active projects"
   - Keywords: find, search, show, list, get, who, what, which, where, employees, projects, skills, allocations

2. **GENERAL_CONVERSATION**: General questions, discussions, or conversation not requiring database access
   - Examples: "How does resource allocation work?", "What is this system for?", "Can you explain project management?"

3. **GREETING**: Greetings, introductions, and pleasantries
   - Examples: "Hello", "Hi there", "Good morning", "How are you?"

4. **HELP_REQUEST**: User asking for help, instructions, or guidance
   - Examples: "How do I use this system?", "What can you help me with?", "Help", "What are your capabilities?"

5. **UNKNOWN**: Unable to determine clear intent or ambiguous requests

Context (previous conversation): {context}

User Input: "{user_input}"

CLASSIFICATION RULES:
- Look for keywords related to searching, finding, querying, listing, showing data
- Consider database entities: employees, projects, skills, allocations, departments, teams
- If user mentions specific names, projects, or wants to "find", "search", "show", "list" something, it's likely DATABASE_QUERY
- If asking conceptual questions about processes or explanations, it's GENERAL_CONVERSATION
- If user wants instructions or help using the system, it's HELP_REQUEST

RESPONSE FORMAT:
Return ONLY the intent category (DATABASE_QUERY, GENERAL_CONVERSATION, GREETING, HELP_REQUEST, or UNKNOWN) without any explanation.

Intent:""",
        )

        # Enhanced query extraction prompt for database queries
        self.query_extraction_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""Extract detailed query parameters from the user's database query request for ResourceWise system.

User Input: "{user_input}"

Analyze the input and extract:

1. **Query Type** (choose most appropriate):
   - resource_search: Finding employees/people, availability, capacity
   - skill_search: Finding by skills, expertise, technologies
   - department_search: Finding by department, team, organizational structure
   - analytics: Reporting, analysis, metrics, summaries, overallocation, project details

2. **Entities**: Specific names, emails, projects, skills, departments mentioned

3. **Filters**: Specific conditions, criteria, or constraints
   - emails, names, designations, project status, allocation percentages
   - availability thresholds, date ranges, skills

4. **Analysis Type**: For analytics queries
   - overallocation, team_composition, project_summary, availability_analysis

5. **Output Requirements**: Specific columns, information requested
   - project details, employee info, allocation percentages, timelines

6. **Constraints**: Limits, sorting, ordering preferences

EXAMPLES:
- "Find allocation of james.wilson@techvantage.io" → resource_search with email filter
- "Show overallocated employees" → analytics with overallocation analysis
- "Get all Software Engineers" → resource_search with designation filter
- "Projects with timelines ordered by start date" → analytics with project_summary and ordering

RESPONSE FORMAT - Return as JSON:
{{
    "query_type": "resource_search|skill_search|department_search|analytics",
    "entities": ["list", "of", "specific", "entities"],
    "filters": {{
        "email": "specific_email",
        "designation": "role_name",
        "project_status": "active|completed|planning",
        "availability_threshold": 75,
        "skills": ["python", "java"]
    }},
    "analysis_type": "overallocation|team_composition|project_summary|availability_analysis",
    "columns": ["specific", "columns", "requested"],
    "include_details": true,
    "include_assignments": true,
    "order_by": "field_name",
    "limit": 50,
    "threshold": 100
}}

JSON Response:""",
        )

        # General response prompt for non-database queries
        self.general_response_prompt = PromptTemplate(
            input_variables=["user_input", "intent_type", "context"],
            template="""You are ResourceWise AI Assistant, a helpful AI for resource allocation and project management.

User Intent: {intent_type}
User Input: "{user_input}"
Context: {context}

RESPONSE GUIDELINES:

For GREETING:
- Be friendly and welcoming
- Briefly introduce yourself as ResourceWise AI Assistant
- Ask how you can help with resource allocation or project management

For HELP_REQUEST:
- Explain your capabilities for resource allocation and project management
- Mention you can help find employees, search by skills, check project allocations, etc.
- Provide specific examples of what they can ask

For GENERAL_CONVERSATION:
- Provide helpful information about resource allocation, project management concepts
- Be informative but concise
- Relate answers back to how it applies to resource management

TONE: Professional, helpful, and friendly. Focus on resource allocation and project management domain.

Response:""",
        )

        # Initialize chains
        self.classification_chain = self.intent_classification_prompt | self.llm
        self.extraction_chain = self.query_extraction_prompt | self.llm
        self.response_chain = self.general_response_prompt | self.llm

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process user input to determine intent and route accordingly.

        Args:
            input_data: Input data containing user query
                Expected format:
                {
                    "query": "Find all developers with Python skills",
                    "session_id": "123",
                    "user_id": "456",
                    "metadata": {...}
                }

        Returns:
            Standardized dictionary containing the response based on intent
        """
        logger.info("Intent agent received request", input_data=input_data, agent_type="intent")

        try:
            # Parse and validate input data
            request = QueryRequest(**input_data)

            # Get context from metadata
            context = request.metadata or {}
            context_str = self._format_context(context)

            # Classify user intent
            intent_type = await self._classify_intent(request.query, context_str)
            logger.info(
                "Intent classified", intent=intent_type, query=request.query, agent_type="intent"
            )

            # Route based on intent
            if intent_type == IntentType.DATABASE_QUERY:
                return await self._handle_database_query(request)
            else:
                return await self._handle_general_response(request, intent_type, context_str)

        except Exception as e:
            logger.error(
                "Error processing intent", error=str(e), input_data=input_data, agent_type="intent"
            )

            error_response = StandardResponse(
                intent=IntentType.UNKNOWN,
                response="I apologize, but I encountered an error processing your request. Please try again.",
                success=False,
                error=str(e),
            )
            return error_response.to_dict()

    async def _classify_intent(self, user_input: str, context: str) -> IntentType:
        """Classify the user's intent.

        Args:
            user_input: User's input query
            context: Conversation context

        Returns:
            Classified intent type
        """
        try:
            chain_input = {"user_input": user_input, "context": context}

            result = await self.classification_chain.ainvoke(chain_input)
            intent_str = str(result.content).strip().upper()

            # Map to enum, with fallback to UNKNOWN
            intent_mapping = {
                "DATABASE_QUERY": IntentType.DATABASE_QUERY,
                "GENERAL_CONVERSATION": IntentType.GENERAL_CONVERSATION,
                "GREETING": IntentType.GREETING,
                "HELP_REQUEST": IntentType.HELP_REQUEST,
                "UNKNOWN": IntentType.UNKNOWN,
            }

            return intent_mapping.get(intent_str, IntentType.UNKNOWN)

        except Exception as e:
            logger.error("Error classifying intent", error=str(e), user_input=user_input)
            return IntentType.UNKNOWN

    async def _handle_database_query(self, request: QueryRequest) -> dict[str, Any]:
        """Handle database query intent by routing to query agent.

        Args:
            request: Original query request

        Returns:
            Standardized response with query agent result
        """
        try:
            # Extract enhanced query parameters
            query_params = await self._extract_query_parameters(request.query)

            # Prepare input for query agent in the exact format it expects
            query_input = {
                "query": request.query,
                "session_id": request.session_id,
                "user_id": request.user_id,
                "metadata": query_params,  # This contains query_type and all other parameters
            }

            # Process through query agent
            query_result = await self.query_agent.process(query_input)

            # Check if query agent returned an error
            if "error" in query_result and query_result["error"]:
                error_response = StandardResponse(
                    intent=IntentType.DATABASE_QUERY,
                    response=f"I encountered an error generating your database query: {query_result['error']}",
                    requires_database=True,
                    success=False,
                    error=query_result["error"],
                    query_type=query_params.get("query_type", "unknown"),
                )
                return error_response.to_dict()

            # Return standardized successful response
            success_response = StandardResponse(
                intent=IntentType.DATABASE_QUERY,
                response="I've successfully generated a database query for your request.",
                requires_database=True,
                success=True,
                query_result=query_result,  # Complete query agent result
                query_type=query_result.get("query_type", "unknown"),
                sql_query=query_result.get("query", ""),
                tables=query_result.get("tables", []),
                filters=query_result.get("filters", ""),
                metadata=query_params,
            )
            return success_response.to_dict()

        except Exception as e:
            logger.error("Error handling database query", error=str(e), query=request.query)

            error_response = StandardResponse(
                intent=IntentType.DATABASE_QUERY,
                response="I understand you want to query the database, but I encountered an error processing your request.",
                requires_database=True,
                success=False,
                error=str(e),
            )
            return error_response.to_dict()

    async def _handle_general_response(
        self, request: QueryRequest, intent_type: IntentType, context: str
    ) -> dict[str, Any]:
        """Handle general conversation intent.

        Args:
            request: Original query request
            intent_type: Classified intent type
            context: Conversation context

        Returns:
            Standardized general response
        """
        try:
            chain_input = {
                "user_input": request.query,
                "intent_type": intent_type.value,
                "context": context,
            }

            result = await self.response_chain.ainvoke(chain_input)
            response = str(result.content)

            success_response = StandardResponse(
                intent=intent_type, response=response, requires_database=False, success=True
            )
            return success_response.to_dict()

        except Exception as e:
            logger.error("Error generating general response", error=str(e), intent=intent_type)

            # Fallback responses based on intent
            fallback_responses = {
                IntentType.GREETING: "Hello! I'm ResourceWise AI Assistant. I can help you with resource allocation, finding employees, checking project status, and more. How can I assist you today?",
                IntentType.HELP_REQUEST: "I can help you with resource allocation and project management tasks. You can ask me to find employees by skills, check project allocations, search for team members, or get information about projects and departments. What would you like to know?",
                IntentType.GENERAL_CONVERSATION: "I'm here to help with resource allocation and project management. Please let me know what specific information you need.",
                IntentType.UNKNOWN: "I'm not sure how to help with that. I specialize in resource allocation, employee search, project management, and skill matching. Could you please rephrase your question?",
            }

            fallback_response = StandardResponse(
                intent=intent_type,
                response=fallback_responses.get(
                    intent_type, fallback_responses[IntentType.UNKNOWN]
                ),
                requires_database=False,
                success=False,
                error=str(e),
            )
            return fallback_response.to_dict()

    async def _extract_query_parameters(self, user_input: str) -> dict[str, Any]:
        """Extract enhanced query parameters from user input.

        Args:
            user_input: User's query

        Returns:
            Enhanced parameters dictionary for query agent
        """
        try:
            result = await self.extraction_chain.ainvoke({"user_input": user_input})

            # Try to parse JSON response
            import json
            import re

            try:
                content = str(result.content)

                # Strip markdown code block formatting if present
                # Pattern matches ```json\n...``` or ```\n...```
                json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
                if json_match:
                    content = json_match.group(1).strip()

                params = json.loads(content)

                # Ensure query_type is mapped to QueryType enum
                query_type_str = params.get("query_type", "resource_search")
                query_type_mapping = {
                    "resource_search": QueryType.RESOURCE_SEARCH,
                    "skill_search": QueryType.SKILL_SEARCH,
                    "department_search": QueryType.DEPARTMENT_SEARCH,
                    "analytics": QueryType.ANALYTICS,
                    "unknown": QueryType.UNKNOWN,
                }
                params["query_type"] = query_type_mapping.get(
                    query_type_str, QueryType.RESOURCE_SEARCH
                )

                # Set reasonable defaults if not specified
                if "limit" not in params:
                    params["limit"] = 50

                return params

            except json.JSONDecodeError:
                # Fallback to basic extraction with keyword analysis
                logger.warning(
                    "Failed to parse JSON from query extraction", response=str(result.content)
                )
                return self._fallback_parameter_extraction(user_input)

        except Exception as e:
            logger.error("Error extracting query parameters", error=str(e), user_input=user_input)
            return self._fallback_parameter_extraction(user_input)

    def _fallback_parameter_extraction(self, user_input: str) -> dict[str, Any]:
        """Fallback parameter extraction using keyword analysis.

        Args:
            user_input: User's query

        Returns:
            Basic parameters dictionary
        """
        lower_input = user_input.lower()

        # Determine query type based on keywords
        if any(
            keyword in lower_input
            for keyword in ["skill", "technology", "expertise", "programming"]
        ):
            query_type = QueryType.SKILL_SEARCH
        elif any(keyword in lower_input for keyword in ["department", "team", "group", "division"]):
            query_type = QueryType.DEPARTMENT_SEARCH
        elif any(
            keyword in lower_input
            for keyword in [
                "overallocation",
                "overallocated",
                "summary",
                "analysis",
                "report",
                "metrics",
                "timeline",
                "composition",
            ]
        ):
            query_type = QueryType.ANALYTICS
        else:
            query_type = QueryType.RESOURCE_SEARCH

        # Extract basic filters
        filters = {}

        # Look for email addresses
        import re

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, user_input)
        if emails:
            filters["email"] = emails[0]

        # Look for common designations
        designations = [
            "software engineer",
            "senior software engineer",
            "tech lead",
            "manager",
            "developer",
        ]
        for designation in designations:
            if designation in lower_input:
                filters["designation"] = designation.title()
                break

        # Look for project status
        if "active" in lower_input:
            filters["project_status"] = "active"
        elif "completed" in lower_input:
            filters["project_status"] = "completed"

        # Look for percentage thresholds
        percentage_matches = re.findall(r"(\d+)%", user_input)
        if percentage_matches:
            filters["availability_threshold"] = int(percentage_matches[0])

        return {"query_type": query_type, "entities": [], "filters": filters, "limit": 50}

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context for prompt inclusion.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        if not context:
            return "No previous context"

        # Extract relevant context information
        history = context.get("history", [])
        if not history:
            return "No previous conversation"

        # Format last few exchanges
        recent_context = []
        for item in history[-3:]:  # Last 3 exchanges
            if isinstance(item, dict):
                role = item.get("role", "unknown")
                content = item.get("content", "")
                recent_context.append(f"{role}: {content}")

        return " | ".join(recent_context) if recent_context else "No previous context"
