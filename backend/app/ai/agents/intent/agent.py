"""Intent classification agent implementation."""

from enum import Enum
from typing import Any

import structlog
from app.ai.agents.base import BaseAgent
from app.ai.core.config import AIConfig
from app.core.config import settings
from app.schemas.ai import QueryRequest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = structlog.get_logger()


class IntentType(str, Enum):
    """Types of user intents."""

    DATABASE_QUERY = "database_query"  # User wants to query/search the database
    RESOURCE_MATCHING = "resource_matching"  # User wants team allocation/matching
    PROJECT_INFO_REQUEST = "project_info_request"  # Follow-up for missing project details
    GENERAL_CONVERSATION = "general_conversation"  # General conversation/questions
    GREETING = "greeting"  # Greetings and pleasantries
    HELP_REQUEST = "help_request"  # User asking for help/instructions
    UNKNOWN = "unknown"  # Unable to determine intent


class IntentAgent(BaseAgent):
    """Agent for classifying user intent only. Orchestration is handled by the workflow graph."""

    def __init__(self, config: AIConfig):
        """Initialize the intent agent.

        Args:
            config: AI configuration settings. Required - contains API keys and model settings.
        """
        super().__init__(config)

        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=0.1,  # Low temperature for consistent classification
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Intent classification prompt
        self.intent_classification_prompt = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""You are an intelligent intent classifier for ResourceWise, an AI-powered resource allocation system.

Your job is to analyze user input and determine their intent from these categories:

1. **DATABASE_QUERY**: User wants to search, find, or query information from the database
   - Examples: "Find all developers with Python skills", "Show me project allocations", "Who is working on the mobile app?", "What skills does John have?", "List all active projects"
   - Keywords: find, search, show, list, get, who, what, which, where, employees, projects, skills, allocations

2. **RESOURCE_MATCHING**: User wants team allocation, resource matching, or project team formation
   - Examples: "I need a team for mobile app development", "Find me developers for React project", "Allocate resources for new project", "I need 2 senior developers for 3 months", "Create a team for machine learning project"
   - Keywords: need team, allocate, assign, match, team for, developers for, resources for, project team, team formation

3. **PROJECT_INFO_REQUEST**: Follow-up responses providing missing project information
   - Examples: "3 months starting July", "Need 2 senior developers and 1 tech lead", "React Native and TypeScript skills required"
   - Context: Usually follows a resource matching request where more details were requested

4. **GENERAL_CONVERSATION**: General questions, discussions, or conversation not requiring database access
   - Examples: "How does resource allocation work?", "What is this system for?", "Can you explain project management?"

5. **GREETING**: Greetings, introductions, and pleasantries
   - Examples: "Hello", "Hi there", "Good morning", "How are you?"

6. **HELP_REQUEST**: User asking for help, instructions, or guidance
   - Examples: "How do I use this system?", "What can you help me with?", "Help", "What are your capabilities?"

7. **UNKNOWN**: Unable to determine clear intent or ambiguous requests


{chat_history}

Human: {user_input}


CLASSIFICATION RULES:
- RESOURCE_MATCHING: Look for "need", "team", "allocate", "assign", "project", "developers", "resources"
- DATABASE_QUERY: Look for "find", "search", "show", "list", "get", "who", "what", "which", "where"
- PROJECT_INFO_REQUEST: Usually short responses with project details like duration, skills, roles
- If user mentions team formation or resource allocation, it's likely RESOURCE_MATCHING
- If user wants to search existing data, it's DATABASE_QUERY
- If asking conceptual questions, it's GENERAL_CONVERSATION

RESPONSE FORMAT:
Return ONLY the intent category (DATABASE_QUERY, RESOURCE_MATCHING, PROJECT_INFO_REQUEST, GENERAL_CONVERSATION, GREETING, HELP_REQUEST, or UNKNOWN) without any explanation.

Intent:""",
        )

        # General response prompt for non-database queries
        self.general_response_prompt = PromptTemplate(
            input_variables=["user_input", "intent_type", "chat_history"],
            template="""You are ResourceWise AI Assistant, a helpful AI for resource allocation and project management.

User Intent: {intent_type}

{chat_history}

Human: {user_input}


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

        # Query contextualization prompt for database queries
        self.query_contextualization_prompt = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""You are a query contextualization assistant for ResourceWise. Your job is to take a user's query and enrich it with context from the conversation history to make it self-contained and clear.

CONVERSATION HISTORY:
{chat_history}

CURRENT USER INPUT: {user_input}

CONTEXTUALIZATION RULES:
1. If the current query references previous results (like "them", "those", "the ones", "who among them"), incorporate the relevant context
2. If the query is a follow-up question, combine it with the previous query context
3. If the query mentions "also" or "too", include what it's building upon
4. If pronouns or unclear references exist, replace them with specific entities from the chat history
5. Keep the query natural and conversational, but self-contained
6. If no contextualization is needed, return the original query unchanged

EXAMPLES:
- User asks: "Show me Python developers" → Next: "Who has React skills too?" 
  → Contextualized: "Show me Python developers who also have React skills"
  
- User asks: "Find employees in Engineering" → Next: "Which ones are available this month?"
  → Contextualized: "Find Engineering employees who are available this month"

- User asks: "List active projects" → Next: "Show their team sizes"
  → Contextualized: "Show team sizes for active projects"

Return ONLY the contextualized query, nothing else:""",
        )

        # Project detail extraction prompt
        self.project_extraction_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""Extract project details from the user's request. Return a JSON object with these fields:

{{
    "name": "project name or description (string or null)",
    "duration_months": "number of months as integer (convert weeks to months, null if not specified)",
    "start_date": "when project starts as string (July, next month, Q2, etc. or null)",
    "skills_required": ["array", "of", "technical", "skills"] (empty array if none specified),
    "resources_required": [{{"resource_type": "role name", "resource_count": number, "required_allocation_percentage": percentage_or_null}}] (e.g. [{{"resource_type": "Senior Developer", "resource_count": 2, "required_allocation_percentage": 100}}, {{"resource_type": "Tech Lead", "resource_count": 1, "required_allocation_percentage": 50}}], empty array if not specified)
}}

Examples:
- "I need a React Native team for 3 months" → {{"name": "React Native project", "duration_months": 3, "start_date": null, "skills_required": ["React Native"], "resources_required": []}}
- "Need 2 senior developers starting July" → {{"name": null, "duration_months": null, "start_date": "July", "skills_required": [], "resources_required": [{{"resource_type": "Senior Developer", "resource_count": 2, "required_allocation_percentage": null}}]}}

User Input: "{user_input}"

Extract what you can, use null for missing information. Return only valid JSON:""",
        )

        # Initialize chains
        self.classification_chain = self.intent_classification_prompt | self.llm
        self.response_chain = self.general_response_prompt | self.llm
        self.contextualization_chain = self.query_contextualization_prompt | self.llm
        self.extraction_chain = self.project_extraction_prompt | self.llm

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process user input to classify intent and generate appropriate response.

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
            Dictionary containing intent classification and response
        """
        logger.info("[INTENT-AGENT] Received request", input_data=input_data, agent_type="intent")

        try:
            # Parse and validate input data
            request = QueryRequest(**input_data)

            # Get context from metadata
            context = request.metadata or {}
            context_str = self._format_context(context)

            # Classify user intent
            intent_type = await self._classify_intent(
                request.query, context_str, context.get("chat_history", [])
            )
            logger.info(
                "[INTENT-AGENT] Intent classified",
                intent=intent_type,
                query=request.query,
                agent_type="intent",
            )
            contextualized_query = await self._contextualize_query(
                request.query, context.get("chat_history", [])
            )

            # Determine workflow type based on intent
            if intent_type == IntentType.DATABASE_QUERY:
                return {
                    "intent": intent_type,
                    "response": "I'll help you search the database for that information.",
                    "requires_database": True,
                    "success": True,
                    "agent_type": "intent",
                    "metadata": {
                        "original_query": request.query,
                        "contextualized_query": contextualized_query,
                        "session_id": request.session_id,
                        "user_id": request.user_id,
                    },
                }
            elif intent_type == IntentType.RESOURCE_MATCHING:
                return {
                    "intent": intent_type,
                    "response": "I'll help you find the right team for your project.",
                    "requires_database": True,  # Will need to query for employees
                    "success": True,
                    "agent_type": "intent",
                    "workflow_intent": "resource_matching",
                    "metadata": {
                        "original_query": request.query,
                        "contextualized_query": contextualized_query,
                        "session_id": request.session_id,
                        "user_id": request.user_id,
                    },
                }
            elif intent_type == IntentType.PROJECT_INFO_REQUEST:
                return {
                    "intent": intent_type,
                    "response": "Thank you for the additional information.",
                    "requires_database": True,  # May need to query for employees after info update
                    "success": True,
                    "agent_type": "intent",
                    "workflow_intent": "resource_matching",
                    "metadata": {
                        "original_query": request.query,
                        "contextualized_query": contextualized_query,
                        "session_id": request.session_id,
                        "user_id": request.user_id,
                    },
                }
            else:
                # For non-database queries, generate response directly
                response = await self._generate_general_response(
                    request, intent_type, context_str, context.get("chat_history", [])
                )
                return {
                    "intent": intent_type,
                    "response": response,
                    "requires_database": False,
                    "success": True,
                    "agent_type": "intent",
                }

        except Exception as e:
            logger.error(
                "[INTENT-AGENT] Error processing intent",
                error=str(e),
                input_data=input_data,
                agent_type="intent",
            )

            return {
                "intent": IntentType.UNKNOWN,
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "requires_database": False,
                "success": False,
                "error": str(e),
                "agent_type": "intent",
            }

    async def _classify_intent(
        self, user_input: str, context: str, chat_history: list[BaseMessage]
    ) -> IntentType:
        """Classify the user's intent.

        Args:
            user_input: User's input query
            context: Conversation context

        Returns:
            Classified intent type
        """
        try:
            chain_input = {"user_input": user_input, "chat_history": chat_history}
            logger.info(f"chain_input: {chain_input}")
            result = await self.classification_chain.ainvoke(chain_input)
            intent_str = str(result.content).strip().upper()

            # Map to enum, with fallback to UNKNOWN
            intent_mapping = {
                "DATABASE_QUERY": IntentType.DATABASE_QUERY,
                "RESOURCE_MATCHING": IntentType.RESOURCE_MATCHING,
                "PROJECT_INFO_REQUEST": IntentType.PROJECT_INFO_REQUEST,
                "GENERAL_CONVERSATION": IntentType.GENERAL_CONVERSATION,
                "GREETING": IntentType.GREETING,
                "HELP_REQUEST": IntentType.HELP_REQUEST,
                "UNKNOWN": IntentType.UNKNOWN,
            }

            classified_intent = intent_mapping.get(intent_str, IntentType.UNKNOWN)

            logger.info(
                "[INTENT-AGENT] Intent classification result",
                raw_response=intent_str,
                classified_intent=classified_intent,
                agent_type="intent",
            )

            return classified_intent

        except Exception as e:
            logger.error(
                "[INTENT-AGENT] Error classifying intent",
                error=str(e),
                user_input=user_input,
                agent_type="intent",
            )
            return IntentType.UNKNOWN

    async def _generate_general_response(
        self,
        request: QueryRequest,
        intent_type: IntentType,
        context: str,
        chat_history: list[BaseMessage],
    ) -> str:
        """Generate response for non-database queries.

        Args:
            request: Original query request
            intent_type: Classified intent type
            context: Conversation context

        Returns:
            Generated response string
        """
        try:
            chain_input = {
                "user_input": request.query,
                "intent_type": intent_type.value,
                "chat_history": chat_history,
            }

            result = await self.response_chain.ainvoke(chain_input)
            response = str(result.content)

            logger.info(
                "[INTENT-AGENT] Generated general response",
                intent_type=intent_type,
                response_length=len(response),
                agent_type="intent",
            )

            return response

        except Exception as e:
            logger.error(
                "[INTENT-AGENT] Error generating general response",
                error=str(e),
                intent=intent_type,
                agent_type="intent",
            )

            # Fallback responses based on intent
            fallback_responses = {
                IntentType.GREETING: "Hello! I'm ResourceWise AI Assistant. I can help you with resource allocation, finding employees, checking project status, and more. How can I assist you today?",
                IntentType.HELP_REQUEST: "I can help you with resource allocation and project management tasks. You can ask me to find employees by skills, check project allocations, search for team members, or get information about projects and departments. What would you like to know?",
                IntentType.GENERAL_CONVERSATION: "I'm here to help with resource allocation and project management. Please let me know what specific information you need.",
                IntentType.UNKNOWN: "I'm not sure how to help with that. I specialize in resource allocation, employee search, project management, and skill matching. Could you please rephrase your question?",
            }

            return fallback_responses.get(intent_type, fallback_responses[IntentType.UNKNOWN])

    async def _contextualize_query(self, user_input: str, chat_history: list[BaseMessage]) -> str:
        """Contextualize a database query using chat history.

        Args:
            user_input: Original user input
            chat_history: Previous conversation messages

        Returns:
            Contextualized query string
        """
        try:
            # If no chat history, return original query
            if not chat_history:
                return user_input

            # Format chat history for the prompt
            formatted_history = self._format_chat_history_for_contextualization(chat_history)

            # Only contextualize if there's meaningful history and the query seems to need it
            if not formatted_history or not self._needs_contextualization(user_input):
                return user_input

            chain_input = {
                "user_input": user_input,
                "chat_history": formatted_history,
            }

            result = await self.contextualization_chain.ainvoke(chain_input)
            contextualized_query = str(result.content).strip()

            # Fallback to original if contextualization failed
            if not contextualized_query or len(contextualized_query) < 3:
                logger.warning(
                    "[INTENT-AGENT] Contextualization returned empty result",
                    original=user_input,
                    agent_type="intent",
                )
                return user_input

            return contextualized_query

        except Exception as e:
            logger.error(
                "[INTENT-AGENT] Error contextualizing query",
                error=str(e),
                user_input=user_input,
                agent_type="intent",
            )
            # Fallback to original query if contextualization fails
            return user_input

    def _needs_contextualization(self, user_input: str) -> bool:
        """Check if a query likely needs contextualization.

        Args:
            user_input: User's input query

        Returns:
            True if query likely needs contextualization
        """
        # Convert to lowercase for checking
        query_lower = user_input.lower()

        # Indicators that contextualization might be needed
        contextual_indicators = [
            # Pronouns referring to previous results
            "them",
            "those",
            "these",
            "it",
            "they",
            # Reference words
            "who among",
            "which ones",
            "the ones",
            # Continuation words
            "also",
            "too",
            "as well",
            "additionally",
            # Follow-up indicators
            "what about",
            "how about",
            "and",
            # Comparative/related
            "their",
            "its",
            "his",
            "her",
        ]

        return any(indicator in query_lower for indicator in contextual_indicators)

    def _format_chat_history_for_contextualization(self, chat_history: list[BaseMessage]) -> str:
        """Format chat history for contextualization prompt.

        Args:
            chat_history: List of chat messages

        Returns:
            Formatted history string
        """
        if not chat_history:
            return ""

        formatted_messages = []

        # Only include the last few exchanges to avoid overwhelming the prompt
        recent_history = chat_history[-6:]  # Last 3 exchanges (user + assistant)

        for message in recent_history:
            if isinstance(message, HumanMessage):
                formatted_messages.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_messages.append(f"Assistant: {message.content}")
            elif hasattr(message, "content"):
                # Generic message type
                formatted_messages.append(f"Message: {message.content}")

        return "\n".join(formatted_messages)

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
        for item in history[-20:]:  # Last 10 exchanges
            if isinstance(item, dict):
                role = item.get("role", "unknown")
                content = item.get("content", "")
                recent_context.append(f"{role}: {content}")

        return " | ".join(recent_context) if recent_context else "No previous context"

    async def extract_project_details(self, user_input: str) -> tuple[dict[str, Any], list[str]]:
        """Extract project details from user input.

        Args:
            user_input: User's input containing project information

        Returns:
            Tuple of (project_details_dict, missing_required_fields_list)
        """
        try:
            # Extract project details using LLM
            result = await self.extraction_chain.ainvoke({"user_input": user_input})

            # Get the raw response content
            raw_content = str(result.content).strip()

            logger.info(
                "[INTENT-AGENT] Raw extraction response",
                raw_content=raw_content,
                agent_type="intent",
            )

            # Handle empty response
            if not raw_content:
                logger.warning(
                    "[INTENT-AGENT] Empty response from extraction chain",
                    user_input=user_input,
                    agent_type="intent",
                )
                raise ValueError("Empty response from LLM")

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from the response (in case there's extra text)
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                project_details = json.loads(json_str)
            else:
                # Fallback: try parsing the entire response as JSON
                project_details = json.loads(raw_content)

            # Validate and determine missing fields
            missing_fields = []
            required_fields = {
                "name": "project name or description",
                "duration_months": "project duration",
                "start_date": "project start date",
                "skills_required": "required technical skills",
                "resources_required": "team composition (roles and counts)",
            }

            for field, description in required_fields.items():
                value = project_details.get(field)
                if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                    missing_fields.append(field)

            logger.info(
                "[INTENT-AGENT] Project details extracted",
                project_details=project_details,
                missing_fields=missing_fields,
                agent_type="intent",
            )

            return project_details, missing_fields

        except json.JSONDecodeError as e:
            logger.error(
                "[INTENT-AGENT] JSON parsing error in project extraction",
                error=str(e),
                raw_content=raw_content if "raw_content" in locals() else "N/A",
                user_input=user_input,
                agent_type="intent",
            )

            # Try to create a basic fallback extraction
            fallback_details = self._create_fallback_project_details(user_input)
            if fallback_details:
                logger.info(
                    "[INTENT-AGENT] Using fallback project extraction",
                    fallback_details=fallback_details,
                    agent_type="intent",
                )

                # Determine missing fields
                missing_fields = []
                required_fields = [
                    "name",
                    "duration_months",
                    "start_date",
                    "skills_required",
                    "resources_required",
                ]

                for field in required_fields:
                    value = fallback_details.get(field)
                    if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                        missing_fields.append(field)

                return fallback_details, missing_fields

            # Return empty details with all fields missing
            return {}, [
                "name",
                "duration_months",
                "start_date",
                "skills_required",
                "resources_required",
            ]

        except Exception as e:
            logger.error(
                "[INTENT-AGENT] Error extracting project details",
                error=str(e),
                error_type=type(e).__name__,
                user_input=user_input,
                agent_type="intent",
            )

            # Return empty details with all fields missing
            return {}, [
                "name",
                "duration_months",
                "start_date",
                "skills_required",
                "resources_required",
            ]

    def _create_fallback_project_details(self, user_input: str) -> dict[str, Any]:
        """Create basic project details using simple text parsing as fallback.

        Args:
            user_input: User's input containing project information

        Returns:
            Basic project details dictionary
        """
        import re

        details = {
            "name": None,
            "duration_months": None,
            "start_date": None,
            "skills_required": [],
            "resources_required": [],
        }

        user_lower = user_input.lower()

        # Extract project name (look for "project" keyword)
        project_match = re.search(r"project\s+(\w+)", user_lower)
        if project_match:
            details["name"] = f"{project_match.group(1).title()} project"

        # Extract duration (look for numbers followed by month/months)
        duration_match = re.search(r"(\d+)\s*months?", user_lower)
        if duration_match:
            details["duration_months"] = int(duration_match.group(1))
        elif "couple" in user_lower and "month" in user_lower:
            details["duration_months"] = 2

        # Extract start date
        if "next month" in user_lower:
            details["start_date"] = "next month"
        elif "starting" in user_lower:
            # Look for month names after "starting"
            months = [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ]
            for month in months:
                if month in user_lower:
                    details["start_date"] = month.title()
                    break

        # Extract skills (common technical skills)
        skills = []
        skill_keywords = [
            "frontend",
            "backend",
            "react",
            "angular",
            "vue",
            "python",
            "java",
            "javascript",
            "typescript",
            "node",
            "django",
            "flask",
            "spring",
        ]
        for skill in skill_keywords:
            if skill in user_lower:
                skills.append(skill)
        details["skills_required"] = skills

        # Extract resources (look for role abbreviations and counts)
        resources = []

        # Look for TL (Tech Lead)
        tl_match = re.search(r"(\d+)\s*tl\s*\((\d+)%\)", user_lower)
        if tl_match:
            resources.append(
                {
                    "resource_type": "TL",
                    "resource_count": int(tl_match.group(1)),
                    "required_allocation_percentage": int(tl_match.group(2)),
                }
            )

        # Look for SSE (Senior Software Engineer)
        sse_match = re.search(r"(\d+)\s*sse\s*\((\d+)%\)", user_lower)
        if sse_match:
            resources.append(
                {
                    "resource_type": "SSE",
                    "resource_count": int(sse_match.group(1)),
                    "required_allocation_percentage": int(sse_match.group(2)),
                }
            )

        # Look for generic developer mentions
        dev_match = re.search(r"(\d+)\s*developers?", user_lower)
        if dev_match and not resources:  # Only if no specific roles found
            resources.append(
                {
                    "resource_type": "Developer",
                    "resource_count": int(dev_match.group(1)),
                    "required_allocation_percentage": None,
                }
            )

        details["resources_required"] = resources

        return details

    def generate_project_info_request(
        self, missing_fields: list[str], current_details: dict[str, Any]
    ) -> str:
        """Generate a request for missing project information.

        Args:
            missing_fields: List of missing required fields
            current_details: Currently available project details

        Returns:
            Formatted request message for missing information
        """
        field_questions = {
            "name": "What is the project name or description?",
            "duration_months": "How long is the project (in months)?",
            "start_date": "When would you like to start the project?",
            "skills_required": "What technical skills are required for this project?",
            "resources_required": "What roles do you need and how many? (e.g., 1 Tech Lead, 2 Senior Developers)",
        }

        questions = []
        for field in missing_fields:
            if field in field_questions:
                questions.append(f"• {field_questions[field]}")

        if not questions:
            return "I have all the information I need. Let me find available team members for your project."

        intro = "I can help you find the perfect team! I need a few more details:"
        return f"{intro}\n\n" + "\n".join(questions)
