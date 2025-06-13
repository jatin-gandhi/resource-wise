"""Query Generation Service using LangGraph for SQL generation and validation"""

from typing import Dict, List, Optional, TypedDict, Any
import structlog
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..core.config import settings
from langchain.schema import BaseMessage
import sqlparse
import re

logger = structlog.get_logger()


class QueryState(TypedDict):
    """State for the query generation workflow"""
    query: str
    intent: str
    context: Dict[str, Any]
    schema_info: Dict[str, Any]
    generated_sql: Optional[str]
    validation_errors: List[str]
    final_sql: Optional[str]
    execution_plan: Optional[str]


class QueryGenerator:
    """Generates and validates SQL queries using LangGraph workflow"""
    
    def __init__(self, db_schema: Dict[str, Any]):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.db_schema = db_schema
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for query generation"""
        workflow = StateGraph(QueryState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("validate_sql", self._validate_sql)
        workflow.add_node("fix_sql", self._fix_sql)
        workflow.add_node("optimize_sql", self._optimize_sql)
        
        # Add edges
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "generate_sql")
        workflow.add_edge("generate_sql", "validate_sql")
        workflow.add_conditional_edges(
            "validate_sql",
            self._should_fix_sql,
            {
                "fix": "fix_sql",
                "optimize": "optimize_sql",
                "end": END
            }
        )
        workflow.add_edge("fix_sql", "validate_sql")
        workflow.add_edge("optimize_sql", END)
        
        return workflow.compile()
    
    async def _analyze_query(self, state: QueryState) -> QueryState:
        """Analyze query and extract key information"""
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze this resource allocation query and extract:
            1. Main entities involved (employees, projects, allocations, skills, designations)
            2. Time constraints (dates, periods, ranges)
            3. Filters and conditions (skills, availability, status)
            4. Required output format (list, count, summary, detailed)
            5. Aggregations needed (sum, count, average, group by)
            
            Database schema context:
            {schema}
            
            Return a JSON-like analysis with these fields:
            - entities: list of main tables needed
            - time_filters: any date/time constraints
            - conditions: filters to apply
            - output_type: what kind of result is expected
            - aggregations: any grouping or calculations needed"""),
            ("human", "Query: {query}\nIntent: {intent}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                analysis_prompt.format_messages(
                    query=state["query"],
                    intent=state["intent"],
                    schema=str(self.db_schema)
                )
            )
            
            # Parse response and update context
            state["context"].update({
                "analysis": response.content,
                "analyzed": True
            })
            
        except Exception as e:
            logger.error("Query analysis failed", error=str(e))
            state["context"]["analysis"] = "Analysis failed"
        
        return state
    
    async def _generate_sql(self, state: QueryState) -> QueryState:
        """Generate SQL query based on analysis"""
        sql_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert PostgreSQL query generator for a resource allocation system.
            
            Database Schema:
            {schema}
            
            Key Guidelines:
            1. Use proper JOINs with appropriate indexes
            2. Handle NULL values with COALESCE or IS NULL/IS NOT NULL
            3. Use array operations for tech_stack and skills (ANY, @>, &&)
            4. Leverage full-text search with @@ and to_tsquery for text searches
            5. Use proper date filtering with DATE functions
            6. Include proper LIMIT clauses for performance
            7. Use window functions for rankings and analytics
            8. Always use table aliases for readability
            9. Use EXISTS instead of IN for better performance when appropriate
            10. Consider using CTEs for complex queries
            
            Example patterns:
            - Array search: WHERE 'React' = ANY(tech_stack)
            - Text search: WHERE search_vector @@ plainto_tsquery('mobile app')
            - Date range: WHERE start_date <= CURRENT_DATE AND end_date >= CURRENT_DATE
            - Availability: WHERE capacity_percent - COALESCE(allocated_percent, 0) >= 50
            
            Return ONLY the SQL query, no explanations or markdown."""),
            ("human", """Query: {query}
            Intent: {intent}
            Analysis: {analysis}
            
            Generate a PostgreSQL query that answers this question efficiently.""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                sql_prompt.format_messages(
                    query=state["query"],
                    intent=state["intent"],
                    analysis=state["context"].get("analysis", ""),
                    schema=str(self.db_schema)
                )
            )
            
            # Clean up the SQL
            sql = response.content.strip()
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.endswith("```"):
                sql = sql[:-3]
            
            state["generated_sql"] = sql.strip()
            
        except Exception as e:
            logger.error("SQL generation failed", error=str(e))
            state["generated_sql"] = None
        
        return state
    
    async def _validate_sql(self, state: QueryState) -> QueryState:
        """Validate generated SQL"""
        errors = []
        sql = state["generated_sql"]
        
        if not sql:
            errors.append("No SQL query generated")
            state["validation_errors"] = errors
            return state
        
        try:
            # Parse SQL syntax
            parsed = sqlparse.parse(sql)
            if not parsed:
                errors.append("Invalid SQL syntax")
            
            # Check if it's a SELECT statement
            if not sql.strip().upper().startswith("SELECT"):
                errors.append("Query must be a SELECT statement")
            
            # Check for dangerous operations
            dangerous_keywords = ["DELETE", "DROP", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]
            sql_upper = sql.upper()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    errors.append(f"Dangerous operation detected: {keyword}")
            
            # Check for required table references
            required_tables = ["employees", "projects", "allocations"]
            for table in required_tables:
                if table in state["context"].get("analysis", "").lower():
                    if table not in sql.lower():
                        errors.append(f"Missing expected table: {table}")
            
            # Check for LIMIT clause in complex queries
            if "join" in sql.lower() and "limit" not in sql.lower():
                errors.append("Consider adding LIMIT clause for performance")
            
        except Exception as e:
            errors.append(f"SQL validation error: {str(e)}")
        
        state["validation_errors"] = errors
        return state
    
    def _should_fix_sql(self, state: QueryState) -> str:
        """Decide whether to fix SQL, optimize, or end"""
        errors = state["validation_errors"]
        
        # If there are critical errors, fix them
        critical_errors = [e for e in errors if any(word in e.lower() 
                          for word in ["invalid", "dangerous", "missing"])]
        if critical_errors:
            return "fix"
        
        # If only performance suggestions, optimize
        if errors and all("limit" in e.lower() or "performance" in e.lower() for e in errors):
            return "optimize"
        
        # If no errors, we're done
        return "end"
    
    async def _fix_sql(self, state: QueryState) -> QueryState:
        """Fix SQL based on validation errors"""
        fix_prompt = ChatPromptTemplate.from_messages([
            ("system", """Fix this SQL query based on the validation errors.
            Maintain the original intent while addressing all issues.
            Return ONLY the corrected SQL query."""),
            ("human", """Original SQL: {sql}
            
            Validation Errors: {errors}
            
            Fix the SQL to address these issues:""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                fix_prompt.format_messages(
                    sql=state["generated_sql"],
                    errors="\n".join(state["validation_errors"])
                )
            )
            
            # Clean up the fixed SQL
            sql = response.content.strip()
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.endswith("```"):
                sql = sql[:-3]
            
            state["generated_sql"] = sql.strip()
            
        except Exception as e:
            logger.error("SQL fixing failed", error=str(e))
        
        return state
    
    async def _optimize_sql(self, state: QueryState) -> QueryState:
        """Optimize SQL for better performance"""
        optimize_prompt = ChatPromptTemplate.from_messages([
            ("system", """Optimize this SQL query for better performance while maintaining correctness.
            Add appropriate LIMIT clauses, use indexes effectively, and consider query structure.
            Return ONLY the optimized SQL query."""),
            ("human", "SQL to optimize: {sql}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                optimize_prompt.format_messages(sql=state["generated_sql"])
            )
            
            # Clean up the optimized SQL
            sql = response.content.strip()
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.endswith("```"):
                sql = sql[:-3]
            
            state["final_sql"] = sql.strip()
            
        except Exception as e:
            logger.error("SQL optimization failed", error=str(e))
            state["final_sql"] = state["generated_sql"]
        
        return state
    
    async def generate_query(self, query: str, intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for query generation"""
        initial_state = QueryState(
            query=query,
            intent=intent,
            context=context or {},
            schema_info=self.db_schema,
            generated_sql=None,
            validation_errors=[],
            final_sql=None,
            execution_plan=None
        )
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "sql": final_state.get("final_sql") or final_state.get("generated_sql"),
                "analysis": final_state["context"].get("analysis"),
                "validation_errors": final_state["validation_errors"],
                "success": len(final_state["validation_errors"]) == 0
            }
            
        except Exception as e:
            logger.error("Query generation workflow failed", error=str(e))
            return {
                "sql": None,
                "analysis": None,
                "validation_errors": [f"Workflow error: {str(e)}"],
                "success": False
            } 