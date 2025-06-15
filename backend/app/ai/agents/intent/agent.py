"""Intent classification agent implementation."""

from enum import Enum
from typing import Any

import structlog
from app.ai.agents.base import BaseAgent
from app.ai.core.config import AIConfig
from app.core.config import settings
from app.schemas.ai import QueryRequest
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

logger = structlog.get_logger()


class IntentType(str, Enum):
    """Types of user intents."""

    DATABASE_QUERY = "database_query"  # User wants to query/search the database
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

        # Initialize LLM for intent classification using config values
        # Note: api_key will be automatically picked up from OPENAI_API_KEY env var
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=0.3,  # Low temperature for consistent classification
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

2. **GENERAL_CONVERSATION**: General questions, discussions, or conversation not requiring database access
   - Examples: "How does resource allocation work?", "What is this system for?", "Can you explain project management?"

3. **GREETING**: Greetings, introductions, and pleasantries
   - Examples: "Hello", "Hi there", "Good morning", "How are you?"

4. **HELP_REQUEST**: User asking for help, instructions, or guidance
   - Examples: "How do I use this system?", "What can you help me with?", "Help", "What are your capabilities?"

5. **UNKNOWN**: Unable to determine clear intent or ambiguous requests


{chat_history}

Human: {user_input}


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

        # Initialize chains
        self.classification_chain = self.intent_classification_prompt | self.llm
        self.response_chain = self.general_response_prompt | self.llm

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

            # Determine if this requires database access
            requires_database = intent_type == IntentType.DATABASE_QUERY

            # For non-database queries, generate response directly
            if not requires_database:
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
            else:
                # For database queries, just return intent - workflow will handle the rest
                return {
                    "intent": intent_type,
                    "response": "I'll help you search the database for that information.",
                    "requires_database": True,
                    "success": True,
                    "agent_type": "intent",
                    "metadata": {
                        "original_query": request.query,
                        "session_id": request.session_id,
                        "user_id": request.user_id,
                    },
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
