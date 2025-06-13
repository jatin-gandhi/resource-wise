"""AI-Powered Chat Orchestrator for Resource Allocation"""

from typing import Dict, Any, AsyncGenerator
import structlog
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .intent_classifier import IntentClassifier, IntentType
from .query_generator import QueryGenerator
from .context_manager import ContextManager
from .semantic_search import SemanticSearchService

logger = structlog.get_logger()

class ChatOrchestrator:
    """AI-powered chat orchestrator for resource allocation queries"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.intent_classifier = IntentClassifier()
        self.query_generator = QueryGenerator({})
        self.context_manager = ContextManager(db)
        self.semantic_search = SemanticSearchService(db)
    
    async def process_chat_message(self, query: str, session_id: str) -> Dict[str, Any]:
        """Process chat message using AI services"""
        
        logger.info("Processing chat message", query=query, session_id=session_id)
        
        try:
            # Store user message in context
            await self.context_manager.add_query_to_history(session_id, query, "", {"type": "user_query"})
            
            # Classify intent
            intent = await self.intent_classifier.classify_intent(query)
            logger.info("Intent classified", intent=intent.value, session_id=session_id)
            
            # Route based on intent
            if intent == IntentType.SIMPLE_QUERY:
                return await self._handle_simple_query(query, session_id)
            elif intent == IntentType.COMPLEX_QUERY:
                return await self._handle_complex_query(query, session_id)
            elif intent == IntentType.ALLOCATION_MODIFICATION:
                return await self._handle_allocation_modification(query, session_id)
            elif intent == IntentType.EMPLOYEE_SEARCH:
                return await self._handle_employee_search(query, session_id)
            elif intent == IntentType.PROJECT_SEARCH:
                return await self._handle_project_search(query, session_id)
            elif intent == IntentType.AVAILABILITY_CHECK:
                return await self._handle_availability_check(query, session_id)
            elif intent == IntentType.SKILL_MATCHING:
                return await self._handle_skill_matching(query, session_id)
            else:  # GENERAL_CONVERSATION
                return await self._handle_general_conversation(query, session_id)
                
        except Exception as e:
            logger.error("Error processing chat message", error=str(e), session_id=session_id)
            return {
                "content": f"I encountered an error processing your request: {str(e)}. Please try again or rephrase your question.",
                "type": "error",
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "error": str(e)
                }
            }
    
    async def _handle_simple_query(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle simple database queries"""
        try:
            # Generate SQL query
            query_result = await self.query_generator.generate_query(query, "simple_query")
            
            if query_result["success"] and query_result["sql"]:
                # Execute the generated SQL
                try:
                    db_result = await self.db.execute(text(query_result["sql"]))
                    rows = db_result.fetchall()
                    data = [dict(row._mapping) for row in rows]
                    
                    result = {
                        "success": True,
                        "data": data,
                        "sql_query": query_result["sql"]
                    }
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"Database execution error: {str(e)}",
                        "sql_query": query_result["sql"]
                    }
            else:
                result = {
                    "success": False,
                    "error": f"Query generation failed: {', '.join(query_result['validation_errors'])}",
                    "sql_query": None
                }
            
            if result["success"]:
                response = self._format_query_results(result["data"], query)
                await self.context_manager.add_query_to_history(session_id, query, response, {"type": "query_result"})
                
                return {
                    "content": response,
                    "type": "query_result",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "sql_query": result.get("sql_query"),
                        "row_count": len(result["data"]) if result["data"] else 0
                    },
                    "data": result["data"]
                }
            else:
                return {
                    "content": f"I couldn't execute your query: {result['error']}",
                    "type": "error",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "error": result["error"]
                    }
                }
        except Exception as e:
            logger.error("Error in simple query", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_complex_query(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle complex queries that might need streaming"""
        try:
            # For complex queries, we might want to stream the response
            query_result = await self.query_generator.generate_query(query, "complex_query")
            
            if query_result["success"] and query_result["sql"]:
                # Execute the generated SQL
                try:
                    db_result = await self.db.execute(text(query_result["sql"]))
                    rows = db_result.fetchall()
                    data = [dict(row._mapping) for row in rows]
                    
                    result = {
                        "success": True,
                        "data": data,
                        "sql_query": query_result["sql"]
                    }
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"Database execution error: {str(e)}",
                        "sql_query": query_result["sql"]
                    }
            else:
                result = {
                    "success": False,
                    "error": f"Query generation failed: {', '.join(query_result['validation_errors'])}",
                    "sql_query": None
                }
            
            if result["success"]:
                response = self._format_complex_results(result["data"], query)
                await self.context_manager.add_query_to_history(session_id, query, response, {"type": "complex_result"})
                
                return {
                    "content": response,
                    "type": "complex_result",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "sql_query": result.get("sql_query"),
                        "complexity": "high"
                    },
                    "data": result["data"]
                }
            else:
                return await self._handle_fallback_response(query, session_id)
        except Exception as e:
            logger.error("Error in complex query", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_employee_search(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle employee search queries"""
        try:
            # Use semantic search for employee queries
            employees = await self.semantic_search.search_employees_by_skills(query)
            
            if employees:
                response = self._format_employee_results(employees, query)
                await self.context_manager.add_query_to_history(session_id, query, response, {"type": "employee_search"})
                
                return {
                    "content": response,
                    "type": "employee_search",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "result_count": len(employees)
                    },
                    "data": employees
                }
            else:
                return {
                    "content": "I couldn't find any employees matching your criteria. Could you provide more specific details?",
                    "type": "no_results",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id
                    }
                }
        except Exception as e:
            logger.error("Error in employee search", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_project_search(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle project search queries"""
        try:
            # Use semantic search for project queries
            projects = await self.semantic_search.search_projects_by_description(query)
            
            if projects:
                response = self._format_project_results(projects, query)
                await self.context_manager.add_query_to_history(session_id, query, response, {"type": "project_search"})
                
                return {
                    "content": response,
                    "type": "project_search",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "result_count": len(projects)
                    },
                    "data": projects
                }
            else:
                return {
                    "content": "I couldn't find any projects matching your criteria. Could you provide more details?",
                    "type": "no_results",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id
                    }
                }
        except Exception as e:
            logger.error("Error in project search", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_availability_check(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle availability check queries"""
        try:
            # Extract time period and employee info from query
            availability_data = await self.semantic_search.find_available_employees()
            
            response = self._format_availability_results(availability_data, query)
            await self.context_manager.add_query_to_history(session_id, query, response, {"type": "availability_check"})
            
            return {
                "content": response,
                "type": "availability_check",
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id
                },
                "data": availability_data
            }
        except Exception as e:
            logger.error("Error in availability check", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_skill_matching(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle skill matching queries"""
        try:
            # Use semantic search to find employees with matching skills
            matches = await self.semantic_search.search_employees_by_skills(query)
            
            if matches:
                response = self._format_skill_match_results(matches, query)
                await self.context_manager.add_query_to_history(session_id, query, response, {"type": "skill_matching"})
                
                return {
                    "content": response,
                    "type": "skill_matching",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "match_count": len(matches)
                    },
                    "data": matches
                }
            else:
                return {
                    "content": "I couldn't find employees with the specific skills you mentioned. Could you try different skill keywords?",
                    "type": "no_results",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id
                    }
                }
        except Exception as e:
            logger.error("Error in skill matching", error=str(e))
            return await self._handle_fallback_response(query, session_id)
    
    async def _handle_allocation_modification(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle allocation modification requests"""
        return {
            "content": "Allocation modifications are not yet implemented. This feature will allow you to modify project assignments and resource allocations.",
            "type": "not_implemented",
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "feature": "allocation_modification"
            }
        }
    
    async def _handle_general_conversation(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle general conversation"""
        return {
            "content": "I'm ResourceWise AI, specialized in helping with resource allocation and project management queries. I can help you find employees, check availability, search projects, and analyze resource allocation. What would you like to know?",
            "type": "general_response",
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            }
        }
    
    async def _handle_fallback_response(self, query: str, session_id: str) -> Dict[str, Any]:
        """Fallback response when other handlers fail"""
        return {
            "content": "I'm having trouble processing your request right now. Could you try rephrasing your question or asking about employees, projects, or resource allocation?",
            "type": "fallback",
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "original_query": query
            }
        }
    
    def _format_query_results(self, data: list, query: str) -> str:
        """Format SQL query results into readable text"""
        if not data:
            return "No results found for your query."
        
        if len(data) == 1:
            return f"Found 1 result: {self._format_single_record(data[0])}"
        else:
            return f"Found {len(data)} results:\n" + "\n".join([
                f"• {self._format_single_record(record)}" for record in data[:5]
            ]) + (f"\n... and {len(data) - 5} more results" if len(data) > 5 else "")
    
    def _format_complex_results(self, data: list, query: str) -> str:
        """Format complex query results"""
        return self._format_query_results(data, query)
    
    def _format_employee_results(self, employees: list, query: str) -> str:
        """Format employee search results"""
        if not employees:
            return "No employees found matching your criteria."
        
        result = f"Found {len(employees)} employee(s):\n"
        for emp in employees[:5]:
            result += f"• {emp.get('name', 'Unknown')} - {emp.get('designation', 'No designation')}\n"
        
        if len(employees) > 5:
            result += f"... and {len(employees) - 5} more employees"
        
        return result
    
    def _format_project_results(self, projects: list, query: str) -> str:
        """Format project search results"""
        if not projects:
            return "No projects found matching your criteria."
        
        result = f"Found {len(projects)} project(s):\n"
        for proj in projects[:5]:
            result += f"• {proj.get('name', 'Unknown Project')}\n"
        
        if len(projects) > 5:
            result += f"... and {len(projects) - 5} more projects"
        
        return result
    
    def _format_availability_results(self, data: dict, query: str) -> str:
        """Format availability check results"""
        return f"Availability information: {data.get('summary', 'No availability data found')}"
    
    def _format_skill_match_results(self, matches: list, query: str) -> str:
        """Format skill matching results"""
        return self._format_employee_results(matches, query)
    
    def _format_single_record(self, record: dict) -> str:
        """Format a single database record"""
        if isinstance(record, dict):
            # Format key-value pairs nicely
            formatted_items = []
            for key, value in record.items():
                if value is not None:
                    formatted_items.append(f"{key}: {value}")
            return ", ".join(formatted_items)
        else:
            return str(record) 