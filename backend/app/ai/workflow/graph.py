"""LangGraph workflow definition."""

from typing import Any

import structlog
from app.ai.agents.intent.agent import IntentAgent
from app.ai.agents.query.agent import QueryAgent
from app.ai.agents.response.agent import ResponseAgent
from app.ai.core.config import AIConfig
from app.ai.workflow.state import AgentState, AgentStateDict
from app.services.database_service import database_service
from langgraph.graph import END, StateGraph

logger = structlog.get_logger()


class AgentWorkflow:
    """LangGraph-based workflow for agent orchestration."""

    def __init__(self, config: AIConfig):
        """Initialize the workflow.

        Args:
            config: AI configuration settings
        """
        self.config = config
        self.intent_agent = IntentAgent(config)
        self.query_agent = QueryAgent(config)
        self.response_agent = ResponseAgent(config)
        self.graph = self._create_graph()
        self.compiled_graph = self.graph.compile()
        logger.info("Initializing AgentWorkflow with Intent, Query, and Response Agents")

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow.

        Returns:
            Configured StateGraph
        """
        # Initialize graph
        workflow = StateGraph(AgentStateDict)

        # Define nodes
        workflow.add_node("intent_classification", self._intent_classification)
        workflow.add_node("query_generation", self._query_generation)
        workflow.add_node("database_execution", self._database_execution)
        workflow.add_node("response_generation", self._response_generation)

        # Define conditional routing function
        def route_after_intent(state: AgentStateDict) -> str:
            """Route based on intent classification result."""
            if state.get("query_result") and state["query_result"].get("requires_database", False):
                return "query_generation"
            else:
                return END

        # Define edges with conditional routing
        workflow.add_conditional_edges(
            "intent_classification",
            route_after_intent,
            {"query_generation": "query_generation", END: END},
        )

        # Database workflow: Query -> Execute -> Generate Response -> End
        workflow.add_edge("query_generation", "database_execution")
        workflow.add_edge("database_execution", "response_generation")
        workflow.add_edge("response_generation", END)

        # Set entry point
        workflow.set_entry_point("intent_classification")

        return workflow

    async def _intent_classification(self, state: AgentStateDict) -> AgentStateDict:
        """Process intent classification and routing.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        try:
            # logger.info(
            #     "Starting intent classification",
            #     user_input=state["user_input"],
            #     session_id=state["session_id"],
            # )

            # Prepare input for intent agent
            input_data = {
                "query": state["user_input"],
                "session_id": state["session_id"],
                "user_id": state["context"].get("user_id"),
                "metadata": {"history": state["history"], **state["context"]},
            }

            # Process through intent agent
            result = await self.intent_agent.process(input_data)

            # Update state with results
            state["current_stage"] = "intent_classified"
            state["query_result"] = result

            # logger.info(
            #     "Intent classification completed",
            #     intent=result.get("intent"),
            #     requires_database=result.get("requires_database", False),
            #     session_id=state["session_id"],
            # )

            return state

        except Exception as e:
            logger.error(
                "Error in intent classification",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Set error state
            state["current_stage"] = "error"
            state["error"] = str(e)
            state["query_result"] = {
                "intent": "unknown",
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "requires_database": False,
            }

            return state

    async def _query_generation(self, state: AgentStateDict) -> AgentStateDict:
        """Process database query generation.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        try:
            # Get the intent result from previous step
            intent_result = state["query_result"]
            if not intent_result:
                raise ValueError("No intent classification result available")

            # Use contextualized query if available, otherwise fall back to original input
            query_to_use = state["user_input"]
            intent_metadata = intent_result.get("metadata", {})
            if "contextualized_query" in intent_metadata:
                query_to_use = intent_metadata["contextualized_query"]
                logger.info(
                    "Using contextualized query from Intent Agent",
                    original_query=state["user_input"],
                    contextualized_query=query_to_use,
                    session_id=state["session_id"],
                )

            logger.info(f"query_to_use: {query_to_use}")

            # Prepare input for query agent using contextualized query
            input_data = {
                "query": query_to_use,
                "session_id": state["session_id"],
                "user_id": state["context"].get("user_id"),
                "metadata": {},  # Query agent handles parameter extraction internally
            }

            # Process through query agent
            query_result = await self.query_agent.process(input_data)

            # Store query result for database execution
            state["sql_query"] = query_result.get("query", "")
            # logger.info(f"sql_query: {state['sql_query']}")
            state["query_details"] = query_result
            state["current_stage"] = "query_generated"

            logger.info(f"state: {state}")
            return state

        except Exception as e:
            logger.error(
                "Error in query generation",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Set error state but continue to response generation for error handling
            state["current_stage"] = "query_error"
            state["error"] = str(e)
            state["sql_query"] = ""
            state["query_details"] = {"error": str(e)}

            return state

    async def _database_execution(self, state: AgentStateDict) -> AgentStateDict:
        """Execute the generated SQL query against the database.

        Args:
            state: Current workflow state

        Returns:
            Updated state with database results
        """
        try:
            # logger.info(
            #     "Starting database execution",
            #     user_input=state["user_input"],
            #     session_id=state["session_id"],
            # )
            # logger.info(f"for DB execution sql_query: {state}")

            # Get the SQL query from previous step
            sql_query = state.get("query_details", {}).get("query", "")
            if not sql_query:
                raise ValueError("No SQL query found for database execution")

            # Execute the query using our database service
            db_result = await database_service.execute_query(sql_query)

            # Store database results
            state["database_result"] = db_result
            state["current_stage"] = "database_executed"

            logger.info(
                "Database execution completed",
                success=db_result.get("success", False),
                row_count=db_result.get("row_count", 0),
                execution_time=db_result.get("execution_time", 0),
                session_id=state["session_id"],
            )

            return state

        except Exception as e:
            logger.error(
                "Error in database execution",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Store database error but continue to response generation
            state["current_stage"] = "database_error"
            state["error"] = str(e)
            state["database_result"] = {
                "success": False,
                "error": str(e),
                "error_type": "EXECUTION_ERROR",
                "db_results": [],
                "execution_time": 0,
            }

            return state

    async def _response_generation(self, state: AgentStateDict) -> AgentStateDict:
        """Generate natural language response using Response Agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state with natural language response
        """
        try:
            logger.info(
                "Starting response generation",
                user_input=state["user_input"],
                session_id=state["session_id"],
            )

            # Prepare input for Response Agent
            query_details = state.get("query_details", {})
            db_result = state.get("database_result", {})

            response_input = {
                "db_results": db_result.get("db_results", []),
                "original_query": state["user_input"],
                "query_context": {
                    **query_details,  # SQL generation context
                    **db_result,  # Database execution context
                },
                "user_id": state["context"].get("user_id"),
                "session_id": state["session_id"],
                "success": db_result.get("success", False),
                "error": state.get("error") or db_result.get("error"),
                "error_type": db_result.get("error_type"),
            }

            # Generate natural language response
            response_result = await self.response_agent.process(response_input)

            # Update the final query result with natural language response
            final_result = {
                **state.get("query_result", {}),  # Keep intent classification
                "response": response_result.get("response", ""),
                "success": response_result.get("success", True),
                "result_count": response_result.get("result_count", 0),
                "sql_query": state.get("query_details", {}).get("query", ""),
                "query_type": query_details.get("query_type", "unknown"),
                "tables_used": query_details.get("tables", []),
                "execution_time": db_result.get("execution_time", 0),
                "metadata": {
                    **state.get("query_result", {}).get("metadata", {}),
                    **response_result.get("metadata", {}),
                },
            }

            state["query_result"] = final_result
            state["current_stage"] = "completed"

            logger.info(
                "Response generation completed",
                success=response_result.get("success", True),
                response_length=len(response_result.get("response", "")),
                session_id=state["session_id"],
            )

            return state

        except Exception as e:
            logger.error(
                "Error in response generation",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Provide fallback response
            db_result = state.get("database_result", {})
            if db_result.get("success", False) and db_result.get("row_count", 0) > 0:
                fallback_response = f"I successfully retrieved {db_result['row_count']} result{'s' if db_result['row_count'] != 1 else ''} from the database, but encountered an error generating the response."
            else:
                fallback_response = "I encountered an error processing your database query."

            # Update final result with fallback
            final_result = {
                **state.get("query_result", {}),
                "response": fallback_response,
                "success": False,
                "error": str(e),
            }

            state["query_result"] = final_result
            state["current_stage"] = "completed_with_error"
            state["error"] = str(e)

            return state

    async def process(
        self, user_input: str, session_id: str, context: dict[str, Any]
    ) -> AgentState:
        """Process a user query through the workflow.

        Args:
            user_input: User's input query
            session_id: Session identifier
            context: Conversation context

        Returns:
            Final workflow state
        """
        try:
            logger.info(
                "Processing workflow", user_input=user_input, session_id=session_id, context=context
            )

            # Initialize state as dictionary for LangGraph
            initial_state = AgentState(
                session_id=session_id, user_input=user_input, context=context
            )
            state_dict = initial_state.to_dict()
            logger.debug("Initialized state", state=initial_state.dict())

            # Use pre-compiled graph for optimal performance
            raw_final_state = await self.compiled_graph.ainvoke(state_dict)

            # Convert LangGraph AddableValuesDict back to AgentState
            final_state = AgentState(
                session_id=raw_final_state.get("session_id", session_id),
                user_input=raw_final_state.get("user_input", user_input),
                current_stage=raw_final_state.get("current_stage", "unknown"),
                error=raw_final_state.get("error"),
                query_result=raw_final_state.get("query_result"),
                context=raw_final_state.get("context", context),
                history=raw_final_state.get("history", []),
            )

            logger.info(
                "Workflow completed",
                session_id=session_id,
                current_stage=final_state.current_stage,
                has_error=final_state.error is not None,
            )

            return final_state

        except Exception as e:
            logger.error(
                "Error in workflow processing",
                error=str(e),
                error_type=type(e).__name__,
                user_input=user_input,
                session_id=session_id,
                context=context,
                exc_info=True,
            )

            # Return error state
            error_state = AgentState(
                session_id=session_id,
                user_input=user_input,
                context=context,
                current_stage="error",
                error=str(e),
                query_result={
                    "intent": "unknown",
                    "response": "I apologize, but I encountered an error processing your request. Please try again.",
                    "error": str(e),
                    "requires_database": False,
                },
            )

            return error_state
