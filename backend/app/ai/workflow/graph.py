"""LangGraph workflow definition."""

from typing import Any

import structlog
from langgraph.graph import END, StateGraph

from app.ai.agents.intent.agent import IntentAgent
from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig
from app.ai.workflow.state import AgentState, AgentStateDict
from app.services.database import db_service
from app.services.response_formatter import response_formatter

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
        self.graph = self._create_graph()
        logger.info("Initializing AgentWorkflow with Intent and Query Agents")

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
        workflow.add_node("response_formatting", self._response_formatting)

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
            {
                "query_generation": "query_generation",
                END: END
            }
        )

        # Database workflow: Query -> Execute -> Format -> End
        workflow.add_edge("query_generation", "database_execution")
        workflow.add_edge("database_execution", "response_formatting")
        workflow.add_edge("response_formatting", END)

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
            logger.info(
                "Starting intent classification",
                user_input=state["user_input"],
                session_id=state["session_id"]
            )

            # Prepare input for intent agent
            input_data = {
                "query": state["user_input"],
                "session_id": state["session_id"],
                "user_id": state["context"].get("user_id"),
                "metadata": {
                    "history": state["history"],
                    **state["context"]
                }
            }

            # Process through intent agent
            result = await self.intent_agent.process(input_data)

            # Update state with results
            state["current_stage"] = "intent_classified"
            state["query_result"] = result

            logger.info(
                "Intent classification completed",
                intent=result.get("intent"),
                requires_database=result.get("requires_database", False),
                session_id=state["session_id"]
            )

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
                "requires_database": False
            }

            return state

    async def _query_generation(self, state: AgentStateDict) -> AgentStateDict:
        """Process database query generation and execution.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        try:
            logger.info(
                "Starting query generation",
                user_input=state["user_input"],
                session_id=state["session_id"]
            )

            # Get the intent result from previous step
            intent_result = state["query_result"]
            if not intent_result:
                raise ValueError("No intent classification result available")

            # Prepare input for query agent using intent metadata
            input_data = {
                "query": state["user_input"],
                "session_id": state["session_id"],
                "user_id": state["context"].get("user_id"),
                "metadata": intent_result.get("metadata", {})
            }

            # Process through query agent
            query_result = await self.query_agent.process(input_data)

            # Combine intent and query results
            final_result = {
                **intent_result,  # Keep intent classification info
                "query_details": query_result,  # Add query generation details
                "sql_query": query_result.get("query", ""),
                "query_parameters": query_result.get("parameters", {}),
                "tables_used": query_result.get("tables", []),
            }

            # Update the response to include query information
            if query_result.get("query"):
                response_parts = [
                    intent_result.get("response", ""),
                    f"\n\nGenerated SQL Query:\n```sql\n{query_result['query']}\n```"
                ]
                if query_result.get("parameters"):
                    response_parts.append(f"\nQuery Parameters: {query_result['parameters']}")

                final_result["response"] = "\n".join(response_parts).strip()

            # Update state with combined results
            state["current_stage"] = "completed"
            state["query_result"] = final_result

            logger.info(
                "Query generation completed",
                has_sql_query=bool(query_result.get("query")),
                tables_used=query_result.get("tables", []),
                session_id=state["session_id"]
            )

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

            # Preserve intent result but add error info
            if state["query_result"]:
                state["query_result"].update({
                    "query_error": str(e),
                    "response": state["query_result"].get("response", "") + f"\n\nNote: I encountered an error generating the database query: {str(e)}"
                })
            else:
                state["query_result"] = {
                    "intent": "database_query",
                    "response": "I apologize, but I encountered an error generating your database query. Please try rephrasing your request.",
                    "error": str(e),
                    "requires_database": True
                }

            state["current_stage"] = "completed_with_error"
            state["error"] = str(e)

            return state

    async def _database_execution(self, state: AgentStateDict) -> AgentStateDict:
        """Execute the generated SQL query against the database.

        Args:
            state: Current workflow state

        Returns:
            Updated state with database results
        """
        try:
            logger.info(
                "Starting database execution",
                user_input=state["user_input"],
                session_id=state["session_id"]
            )

            # Get the query result from previous step
            query_result = state["query_result"]
            if not query_result:
                raise ValueError("No query generation result available")

            # Extract SQL query
            sql_query = query_result.get("sql_query", "")
            if not sql_query:
                raise ValueError("No SQL query found in query generation result")

            # Execute the query
            db_result = await db_service.execute_query(sql_query)

            # Update state with database results
            state["query_result"]["database_result"] = db_result
            state["current_stage"] = "database_executed"

            logger.info(
                "Database execution completed",
                success=db_result.get("success", False),
                row_count=db_result.get("row_count", 0),
                execution_time=db_result.get("execution_time", 0),
                session_id=state["session_id"]
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

            # Add database error to state
            if state["query_result"]:
                state["query_result"]["database_result"] = {
                    "success": False,
                    "error": str(e),
                    "error_type": "EXECUTION_ERROR",
                    "data": [],
                    "columns": [],
                    "row_count": 0,
                    "execution_time": 0
                }

            state["current_stage"] = "database_error"
            state["error"] = str(e)

            return state

    async def _response_formatting(self, state: AgentStateDict) -> AgentStateDict:
        """Format the database results into user-friendly response.

        Args:
            state: Current workflow state

        Returns:
            Updated state with formatted response
        """
        try:
            logger.info(
                "Starting response formatting",
                user_input=state["user_input"],
                session_id=state["session_id"]
            )

            # Get the query and database results
            query_result = state["query_result"]
            if not query_result:
                raise ValueError("No query result available")

            db_result = query_result.get("database_result")
            if not db_result:
                raise ValueError("No database result available")

            # Prepare context for formatting
            query_context = {
                "query_type": query_result.get("query_details", {}).get("query_type", "unknown"),
                "intent": query_result.get("intent", "database_query"),
                "parameters": query_result.get("query_parameters", {}),
                "tables_used": query_result.get("tables_used", [])
            }

            # Format the response
            formatted_response = await response_formatter.format_database_response(
                query_result=db_result,
                query_context=query_context,
                original_query=state["user_input"]
            )

            # Update the final response
            final_response = {
                **query_result,  # Keep all previous data
                "response": formatted_response.get("response", ""),
                "formatted_data": formatted_response.get("formatted_data"),
                "summary": formatted_response.get("summary", ""),
                "success": formatted_response.get("success", True),
                "metadata": {
                    **query_result.get("metadata", {}),
                    **formatted_response.get("metadata", {})
                }
            }

            # If formatting failed, provide fallback response
            if not formatted_response.get("success", True):
                fallback_msg = "I successfully retrieved the data from the database, but encountered an issue formatting the response."
                if db_result.get("success", False) and db_result.get("row_count", 0) > 0:
                    fallback_msg += f" Found {db_result['row_count']} result{'s' if db_result['row_count'] != 1 else ''}."

                final_response["response"] = fallback_msg

            # Update state
            state["query_result"] = final_response
            state["current_stage"] = "completed"

            logger.info(
                "Response formatting completed",
                success=formatted_response.get("success", True),
                format_type=formatted_response.get("metadata", {}).get("format", "unknown"),
                session_id=state["session_id"]
            )

            return state

        except Exception as e:
            logger.error(
                "Error in response formatting",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Provide fallback response
            if state["query_result"] and state["query_result"].get("database_result", {}).get("success", False):
                db_result = state["query_result"]["database_result"]
                fallback_response = f"I successfully retrieved {db_result.get('row_count', 0)} result{'s' if db_result.get('row_count', 0) != 1 else ''} from the database, but encountered an error formatting the response."
                state["query_result"]["response"] = fallback_response
            else:
                state["query_result"]["response"] = "I encountered an error processing your database query."

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
                "Processing workflow",
                user_input=user_input,
                session_id=session_id,
                context=context
            )

            # Initialize state as dictionary for LangGraph
            initial_state = AgentState(
                session_id=session_id,
                user_input=user_input,
                context=context
            )
            state_dict = initial_state.to_dict()
            logger.debug("Initialized state", state=initial_state.dict())

            # Compile and run workflow
            compiled_graph = self.graph.compile()
            raw_final_state = await compiled_graph.ainvoke(state_dict)

            # Convert LangGraph AddableValuesDict back to AgentState
            final_state = AgentState(
                session_id=raw_final_state.get("session_id", session_id),
                user_input=raw_final_state.get("user_input", user_input),
                current_stage=raw_final_state.get("current_stage", "unknown"),
                error=raw_final_state.get("error"),
                query_result=raw_final_state.get("query_result"),
                context=raw_final_state.get("context", context),
                history=raw_final_state.get("history", [])
            )

            logger.info(
                "Workflow completed",
                session_id=session_id,
                current_stage=final_state.current_stage,
                has_error=final_state.error is not None
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
                    "requires_database": False
                }
            )

            return error_state

    async def stream_process(
        self, user_input: str, session_id: str, context: dict[str, Any]
    ) -> Any:
        """Process a user query through the workflow with streaming.

        Args:
            user_input: User's input query
            session_id: Session identifier
            context: Conversation context

        Yields:
            Streaming response chunks
        """
        try:
            logger.info(
                "Starting streaming workflow",
                user_input=user_input,
                session_id=session_id
            )

            # For now, process normally and yield the final result
            # TODO: Implement proper streaming when LangGraph supports it better
            final_state = await self.process(user_input, session_id, context)

            if final_state.query_result:
                response = final_state.query_result.get("response", "")
                # Stream the response in chunks
                chunk_size = 50
                for i in range(0, len(response), chunk_size):
                    chunk = response[i:i + chunk_size]
                    yield chunk

        except Exception as e:
            logger.error(
                "Error in streaming workflow",
                error=str(e),
                error_type=type(e).__name__,
                user_input=user_input,
                session_id=session_id,
                context=context,
                exc_info=True,
            )
            yield f"Error: {str(e)}"
