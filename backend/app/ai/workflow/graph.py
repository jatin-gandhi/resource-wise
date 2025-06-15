"""LangGraph workflow definition."""

from typing import Any
import json
import structlog
from app.ai.agents.intent.agent import IntentAgent
from app.ai.agents.matching.agent import MatchingAgent
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
        self.matching_agent = MatchingAgent(config)
        self.graph = self._create_graph()
        self.compiled_graph = self.graph.compile()
        logger.info("Initializing AgentWorkflow with Intent, Query, Response, and Matching Agents")

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow.

        Returns:
            Configured StateGraph
        """
        # Initialize graph
        workflow = StateGraph(AgentStateDict)

        # Define nodes
        workflow.add_node("intent_classification", self._intent_classification)
        workflow.add_node("project_info_extraction", self._project_info_extraction)
        workflow.add_node("query_generation", self._query_generation)
        workflow.add_node("database_execution", self._database_execution)
        workflow.add_node("response_generation", self._response_generation)
        workflow.add_node("resource_matching", self._resource_matching)

        # Define conditional routing functions
        def route_after_intent(state: AgentStateDict) -> str:
            """Route based on intent classification result."""
            workflow_intent = state.get("workflow_intent")
            
            if workflow_intent == "resource_matching":
                return "project_info_extraction"
            elif state.get("query_result") and state["query_result"].get("requires_database", False):
                return "query_generation"
            else:
                return END

        def route_after_project_info(state: AgentStateDict) -> str:
            """Route after project info extraction."""
            missing_info = state.get("missing_project_info", [])
            
            if missing_info:
                return "response_generation"  # Ask for missing info
            else:
                return "query_generation"  # Get employees

        def route_after_response(state: AgentStateDict) -> str:
            """Route after response generation."""
            workflow_intent = state.get("workflow_intent")
            current_stage = state.get("current_stage")
            
            if workflow_intent == "resource_matching" and current_stage == "employees_retrieved":
                return "resource_matching"
            else:
                return END

        # Define edges with conditional routing
        workflow.add_conditional_edges(
            "intent_classification",
            route_after_intent,
            {
                "project_info_extraction": "project_info_extraction",
                "query_generation": "query_generation", 
                END: END
            },
        )

        workflow.add_conditional_edges(
            "project_info_extraction",
            route_after_project_info,
            {
                "response_generation": "response_generation",
                "query_generation": "query_generation"
            },
        )

        workflow.add_conditional_edges(
            "response_generation",
            route_after_response,
            {
                "resource_matching": "resource_matching",
                END: END
            },
        )

        # Regular edges
        workflow.add_edge("query_generation", "database_execution")
        workflow.add_edge("database_execution", "response_generation")
        workflow.add_edge("resource_matching", "response_generation")

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
            
            # Set workflow_intent based on result
            if "workflow_intent" in result:
                state["workflow_intent"] = result["workflow_intent"]
            elif result.get("intent") == "database_query":
                state["workflow_intent"] = "database_query"
            else:
                state["workflow_intent"] = "general"

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

    async def _project_info_extraction(self, state: AgentStateDict) -> AgentStateDict:
        """Extract and validate project information from user input.

        Args:
            state: Current workflow state

        Returns:
            Updated state with project details and missing info
        """
        try:
            logger.info(
                "Starting project info extraction",
                user_input=state["user_input"],
                session_id=state["session_id"],
            )

            # Extract project details using Intent Agent's enhanced capabilities
            project_details, missing_info = await self.intent_agent.extract_project_details(state["user_input"])

            # Update state
            state["project_details"] = project_details
            state["missing_project_info"] = missing_info
            state["current_stage"] = "project_info_extracted"

            logger.info(
                "Project info extraction completed",
                has_complete_info=len(missing_info) == 0,
                missing_fields=missing_info,
                project_details=project_details,
                session_id=state["session_id"],
            )

            return state

        except Exception as e:
            logger.error(
                "Error in project info extraction",
                error=str(e),
                error_type=type(e).__name__,
                user_input=state["user_input"],
                session_id=state["session_id"],
                exc_info=True,
            )

            # Set error state - will trigger info request
            state["current_stage"] = "project_info_error"
            state["error"] = str(e)
            state["missing_project_info"] = ["name", "duration_months", "start_date", "skills_required", "resources_required"]
            state["project_details"] = {}

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

            logger.info(f"query_to_use: {query_to_use}")

            workflow_intent = state.get("workflow_intent")
            
            if workflow_intent == "resource_matching":
                # Generate employee availability query
                project_details = state.get("project_details", {})
                
                # Create a natural language query for employee search
                skills = project_details.get("skills_required", [])
                resources = project_details.get("resources_required", [])
                
                employee_query = f"Find available employees"
                if skills:
                    employee_query += f" with skills: {', '.join(skills)}"
                if resources:
                    # Extract roles from new format (list of ResourceRequirement objects)
                    if isinstance(resources, list):
                        roles = [resource.get("resource_type", "") for resource in resources if isinstance(resource, dict)]
                        roles = [role for role in roles if role]  # Filter out empty strings
                    else:
                        # Backward compatibility with old format (dict)
                        roles = list(resources.keys())
                    
                    if roles:
                        employee_query += f" in roles: {', '.join(roles)}."
                employee_query += "Provide employee id as employee_id, name as employee_name, email as employee_email, designation title as employee_designation, skills as employee_skills, and available allocation percentage as employee_available_percentage. For each skill include skill name as skill_name, experience in months as skill_experience, and last used date as skill_last_used_date."

                input_data = {
                    "query": employee_query,
                    "session_id": state["session_id"],
                    "user_id": state["context"].get("user_id"),
                    "metadata": {
                        "workflow_intent": "resource_matching",
                        "project_details": project_details
                    }
                }
            else:
                # Regular database query
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
            
            # Handle resource matching workflow
            workflow_intent = state.get("workflow_intent")
            if workflow_intent == "resource_matching":
                # Store raw employees for transformation in matching step
                raw_employees = db_result.get("db_results", [])
                state["available_employees"] = raw_employees
                state["current_stage"] = "employees_retrieved"
                
                logger.info(
                    "Employee data retrieved for matching",
                    employee_count=len(raw_employees),
                    session_id=state["session_id"],
                )
            else:
                state["current_stage"] = "database_executed"

            logger.info(
                "Database execution completed",
                success=db_result.get("success", False),
                row_count=db_result.get("row_count", 0),
                execution_time=db_result.get("execution_time", 0),
                workflow_intent=workflow_intent,
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

            workflow_intent = state.get("workflow_intent")
            missing_info = state.get("missing_project_info", [])
            current_stage = state.get("current_stage")
            
            # Handle missing project information request
            if workflow_intent == "resource_matching" and missing_info:
                project_details = state.get("project_details", {})
                response = self.intent_agent.generate_project_info_request(missing_info, project_details)
                
                final_result = {
                    "intent": "project_info_request",
                    "response": response,
                    "requires_database": False,
                    "workflow_intent": workflow_intent,
                    "missing_project_info": missing_info,
                    "success": True
                }
                
                state["query_result"] = final_result
                state["current_stage"] = "awaiting_project_info"
                
                logger.info(
                    "Generated project info request",
                    missing_fields=missing_info,
                    session_id=state["session_id"],
                )
                
                return state
            
            # Handle employee availability response (before matching)
            elif workflow_intent == "resource_matching" and current_stage == "employees_retrieved":
                employees = state.get("available_employees", [])
                db_result = state.get("database_result", {})
                
                if employees:
                    response = f"I found {len(employees)} available employees that match your project requirements. Let me analyze the best team combinations for you."
                else:
                    response = "I couldn't find any employees that match your project requirements. You may want to adjust the skills or roles needed."
                
                final_result = {
                    "intent": "resource_matching",
                    "response": response,
                    "employee_count": len(employees),
                    "workflow_intent": workflow_intent,
                    "success": len(employees) > 0,
                    "execution_time": db_result.get("execution_time", 0)
                }
                
                state["query_result"] = final_result
                # Keep current_stage as "employees_retrieved" for routing to matching
                
                logger.info(
                    "Generated employee availability response",
                    employee_count=len(employees),
                    session_id=state["session_id"],
                )
                
                return state
            
            # Handle resource matching results (after matching)
            elif workflow_intent == "resource_matching" and current_stage == "matching_completed":
                matching_results = state.get("query_result", {})
                
                final_result = {
                    "intent": "resource_matching",
                    "response": matching_results.get("response", "Resource matching completed."),
                    "workflow_intent": workflow_intent,
                    "success": matching_results.get("success", True),
                    "matching_results": matching_results,
                    "team_combinations": state.get("team_combinations", [])
                }
                
                state["query_result"] = final_result
                state["current_stage"] = "completed"
                
                logger.info(
                    "Generated resource matching response",
                    has_team_combinations=len(state.get("team_combinations", [])) > 0,
                    session_id=state["session_id"],
                )
                
                return state
            
            # Regular database response handling
            else:
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

    async def _resource_matching(self, state: AgentStateDict) -> AgentStateDict:
        """Run resource matching algorithm using available employees.

        Args:
            state: Current workflow state

        Returns:
            Updated state with team combinations
        """
        try:
            logger.info(
                "Starting resource matching",
                session_id=state["session_id"],
            )

            project_details = state.get("project_details", {})
            raw_employees = state.get("available_employees", [])

            if not project_details:
                raise ValueError("No project details available for matching")
            
            if not raw_employees:
                raise ValueError("No available employees found for matching")

            # Transform project details to match MatchingAgent schema
            transformed_project_details = self._transform_project_details_for_matching(project_details)
            
            logger.info(
                "Data transformation completed",
                raw_employee_count=len(raw_employees),
                session_id=state["session_id"],
            )
            
            # Prepare input for MatchingAgent
            matching_input = {
                "project_details": transformed_project_details,
                "available_employees": raw_employees
            }

            # Run matching algorithm
            matching_result = await self.matching_agent.process(matching_input)

            # Extract team combinations from result
            team_combinations = matching_result.get("matching_results", {}).get("possible_team_combinations", [])

            # Store results in state
            state["team_combinations"] = team_combinations
            state["current_stage"] = "matching_completed"

            # Generate response with team combinations
            if team_combinations:
                response = json.dumps(matching_result.get("matching_results", {}))
            else:
                response = "I couldn't find suitable team combinations with the available employees. You may want to adjust the project requirements or consider alternative resources."

            # Update final response
            final_result = {
                **state.get("query_result", {}),
                "response": response,
                "team_combinations": team_combinations,
                "team_combinations_count": len(team_combinations),
                "matching_completed": True,
                "success": len(team_combinations) > 0
            }
            
            state["query_result"] = final_result

            logger.info(
                "Resource matching completed",
                team_combinations_count=len(team_combinations),
                session_id=state["session_id"],
            )

            return state

        except Exception as e:
            logger.error(
                "Error in resource matching",
                error=str(e),
                error_type=type(e).__name__,
                session_id=state["session_id"],
                exc_info=True,
            )

            # Fallback response
            final_result = {
                **state.get("query_result", {}),
                "response": "I found available employees but encountered an error generating team combinations. Please try again.",
                "error": str(e),
                "success": False
            }
            
            state["query_result"] = final_result
            state["current_stage"] = "matching_error"
            state["error"] = str(e)
            
            return state

    def _transform_project_details_for_matching(self, project_details: dict) -> dict:
        """Transform project details from our format to MatchingAgent schema.
        
        Args:
            project_details: Project details in our internal format
            
        Returns:
            Project details in MatchingAgent format
        """
        # Transform field names to match MatchingAgent schema
        transformed = {
            "name": project_details.get("name", "Unnamed Project"),
            "duration": project_details.get("duration_months", 1),  # duration_months -> duration
            "starting_from": project_details.get("start_date", "TBD"),  # start_date -> starting_from
            "skills_required": project_details.get("skills_required", []),
            "resources_required": []  # Will be transformed below
        }
        
        # Transform resources_required from our format to ResourceRequirement objects
        resources_required = project_details.get("resources_required", [])
        
        if isinstance(resources_required, list):
            # Already in new format - validate and ensure proper structure
            for resource in resources_required:
                if isinstance(resource, dict) and "resource_type" in resource and "resource_count" in resource:
                    transformed_resource = {
                        "resource_type": resource["resource_type"],
                        "resource_count": resource["resource_count"],
                        "required_allocation_percentage": resource.get("required_allocation_percentage")
                    }
                    transformed["resources_required"].append(transformed_resource)
        elif isinstance(resources_required, dict):
            # Old format - convert from {"Role": count} to new format
            for role, count in resources_required.items():
                transformed_resource = {
                    "resource_type": role,
                    "resource_count": count,
                    "required_allocation_percentage": None  # Default to None (100%)
                }
                transformed["resources_required"].append(transformed_resource)
        
        return transformed

    # def _format_team_combinations_response(self, team_combinations: list[dict]) -> str:
    #     """Format team combinations into a readable response.
        
    #     Args:
    #         team_combinations: List of team combination dictionaries
            
    #     Returns:
    #         Formatted response string
    #     """
    #     if not team_combinations:
    #         return "No suitable team combinations found."
        
    #     response = f"I found {len(team_combinations)} possible team combination{'s' if len(team_combinations) != 1 else ''}:\n\n"
        
    #     for i, combination in enumerate(team_combinations[:3], 1):  # Show top 3
    #         team_members = combination.get("team_members", [])
    #         skills_match = combination.get("skills_match", 0)
    #         skills_matched = combination.get("skills_matched", [])
    #         skills_missing = combination.get("skills_missing", [])
            
    #         response += f"**Team Option {i}** (Skills Match: {skills_match:.1f}%)\n"
            
    #         for member in team_members:
    #             name = member.get("name", "Unknown")
    #             designation = member.get("designation", "Unknown")
    #             availability = member.get("available_percentage", 0)
    #             response += f"• {name} - {designation} ({availability}% available)\n"
            
    #         if skills_matched:
    #             response += f"✅ Covers: {', '.join(skills_matched)}\n"
    #         if skills_missing:
    #             response += f"❌ Missing: {', '.join(skills_missing)}\n"
            
    #         response += "\n"
        
    #     if len(team_combinations) > 3:
    #         response += f"... and {len(team_combinations) - 3} more combinations available.\n"
        
    #     return response

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
                workflow_intent=raw_final_state.get("workflow_intent"),
                project_details=raw_final_state.get("project_details"),
                missing_project_info=raw_final_state.get("missing_project_info", []),
                available_employees=raw_final_state.get("available_employees", []),
                team_combinations=raw_final_state.get("team_combinations", []),
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
