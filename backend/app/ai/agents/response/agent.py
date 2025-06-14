"""Response generation agent implementation."""

from typing import Any

import structlog
from app.ai.agents.base import BaseAgent
from app.ai.core.config import AIConfig
from app.core.config import settings
from app.schemas.ai import QueryRequest
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = structlog.get_logger()


class ResponseAgent(BaseAgent):
    """Agent for generating natural language responses from database results."""

    def __init__(self, config: AIConfig):
        """Initialize the response agent.

        Args:
            config: AI configuration settings. Required - contains API keys and model settings.
        """
        super().__init__(config)

        # Initialize LLM using config values
        # Note: api_key will be automatically picked up from OPENAI_API_KEY env var
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=0.3,  # Slightly higher temperature for more natural responses
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Response generation prompt
        self.response_generation_prompt = PromptTemplate(
            input_variables=["original_query", "db_results", "query_context", "result_count"],
            template="""You are ResourceWise AI Assistant, an expert in analyzing and explaining resource allocation data.

Your task is to convert database query results into natural, conversational responses that are helpful and insightful.

**Original User Query:** "{original_query}"

**Database Results:** {db_results}

**Query Context:**
- Query Type: {query_context}
- Number of Results: {result_count}

**Response Guidelines:**

1. **Be Conversational & Natural**
   - Start with phrases like "I found...", "Here's what I discovered...", "Based on your query..."
   - Avoid robotic language like "Query executed successfully"

2. **Provide Context & Insights**
   - Explain what the data means in business terms
   - Highlight interesting patterns or outliers
   - Relate findings back to resource allocation implications

3. **Format for Readability**
   - Use bullet points or numbered lists for multiple results
   - Bold important information like names, percentages, dates
   - Keep individual items concise but informative

4. **Handle Different Scenarios:**
   - **Multiple Results:** Group similar items, highlight key differences
   - **Single Result:** Provide detailed breakdown of that item
   - **No Results:** Explain possible reasons and suggest alternatives
   - **Large Result Sets:** Summarize key patterns and show representative examples

5. **Add Actionable Insights**
   - For availability queries: Mention who might be good candidates for new projects
   - For skill searches: Note experience levels and current commitments
   - For overallocation: Explain potential risks and recommendations
   - For project data: Highlight timelines, capacity, and team composition

6. **Business Context Examples:**
   - "Sarah has 25% availability, making her a good candidate for a new project"
   - "Most of these developers are currently under-allocated, which is great for project planning"
   - "The Mobile Banking App team is fully allocated until March"
   - "I notice several Senior Engineers with React skills are available"

**Response Format:**
- Start with a clear, conversational opening
- Present the main findings in an organized way
- End with actionable insights or next steps when appropriate
- Keep technical details minimal unless specifically requested

Generate a helpful, natural response:""",
        )

        # Error response prompt
        self.error_response_prompt = PromptTemplate(
            input_variables=["original_query", "error_details", "error_type"],
            template="""You are ResourceWise AI Assistant. You need to explain a database error in user-friendly terms.

**User Query:** "{original_query}"
**Error Type:** {error_type}
**Error Details:** {error_details}

**Task:** Convert this technical error into a helpful, user-friendly message.

**Guidelines:**
1. **Be Empathetic:** Acknowledge the user's request
2. **Explain Simply:** Avoid technical jargon
3. **Suggest Alternatives:** When possible, suggest what they could try instead
4. **Stay Positive:** Focus on what you can help with

**Common Error Types:**
- **No Results:** "I couldn't find anyone matching those criteria. You might try..."
- **Too Many Results:** "I found a lot of matches. Could you be more specific about..."
- **Permission Issues:** "I don't have access to that information, but I can help you with..."
- **Query Issues:** "I had trouble understanding that request. Could you rephrase it as..."

Generate a helpful, friendly error response:""",
        )

        # Initialize chains
        self.response_chain = self.response_generation_prompt | self.llm
        self.error_chain = self.error_response_prompt | self.llm

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process database results to generate natural language response.

        Args:
            input_data: Input data containing database results and context
                Expected format:
                {
                    "db_results": [...],           # Database query results
                    "original_query": "...",       # User's original question
                    "query_context": {...},        # Context from Query Agent
                    "user_id": "123",
                    "session_id": "456",
                    "success": True/False,
                    "error": "..." (if error occurred)
                }

        Returns:
            Dictionary containing natural language response
        """
        logger.info(
            "[RESPONSE-AGENT] Received request",
            has_results=bool(input_data.get("db_results")),
            success=input_data.get("success", False),
            agent_type="response",
        )

        try:
            # Check if this is an error case
            if not input_data.get("success", True) or input_data.get("error"):
                return await self._handle_error_response(input_data)

            # Extract data
            db_results = input_data.get("db_results", [])
            original_query = input_data.get("original_query", "")
            query_context = input_data.get("query_context", {})

            # Process successful database results
            return await self._generate_success_response(db_results, original_query, query_context)

        except Exception as e:
            logger.error(
                "[RESPONSE-AGENT] Error generating response",
                error=str(e),
                agent_type="response",
            )
            return {
                "response": "I retrieved your data successfully, but encountered an issue generating the response. Please try again.",
                "success": False,
                "error": str(e),
                "agent_type": "response",
            }

    async def _generate_success_response(
        self, db_results: list[dict], original_query: str, query_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate natural language response from successful database results.

        Args:
            db_results: Database query results
            original_query: User's original query
            query_context: Context from Query Agent

        Returns:
            Response dictionary
        """
        try:
            result_count = len(db_results)

            logger.info(
                "[RESPONSE-AGENT] Generating success response",
                result_count=result_count,
                query_type=query_context.get("query_type", "unknown"),
                agent_type="response",
            )

            # Prepare data for LLM (limit size to avoid token limits)
            limited_results = self._prepare_results_for_llm(db_results)

            # Format query context for prompt
            context_summary = self._format_query_context(query_context)

            # Generate response using LLM
            chain_input = {
                "original_query": original_query,
                "db_results": limited_results,
                "query_context": context_summary,
                "result_count": result_count,
            }

            result = await self.response_chain.ainvoke(chain_input)
            natural_response = str(result.content)

            logger.info(
                "[RESPONSE-AGENT] Generated natural response",
                response_length=len(natural_response),
                agent_type="response",
            )

            return {
                "response": natural_response,
                "success": True,
                "result_count": result_count,
                "agent_type": "response",
                "metadata": {
                    "query_type": query_context.get("query_type", "unknown"),
                    "execution_time": query_context.get("execution_time", 0),
                    "tables_used": query_context.get("tables", []),
                },
            }

        except Exception as e:
            logger.error(
                "[RESPONSE-AGENT] Error in success response generation",
                error=str(e),
                agent_type="response",
            )
            return {
                "response": f"I found {len(db_results)} result(s) for your query, but had trouble formatting the response. Here's a summary: {self._create_simple_summary(db_results)}",
                "success": True,
                "result_count": len(db_results),
                "agent_type": "response",
                "error": str(e),
            }

    async def _handle_error_response(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Handle error cases with natural language explanation.

        Args:
            input_data: Input data containing error information

        Returns:
            Error response dictionary
        """
        try:
            original_query = input_data.get("original_query", "")
            error_details = input_data.get("error", "Unknown error occurred")
            error_type = input_data.get("error_type", "UNKNOWN")

            logger.info(
                "[RESPONSE-AGENT] Generating error response",
                error_type=error_type,
                agent_type="response",
            )

            # Generate user-friendly error response
            chain_input = {
                "original_query": original_query,
                "error_details": error_details,
                "error_type": error_type,
            }

            result = await self.error_chain.ainvoke(chain_input)
            error_response = str(result.content)

            logger.info(
                "[RESPONSE-AGENT] Generated error response",
                response_length=len(error_response),
                agent_type="response",
            )

            return {
                "response": error_response,
                "success": False,
                "error": error_details,
                "error_type": error_type,
                "agent_type": "response",
            }

        except Exception as e:
            logger.error(
                "[RESPONSE-AGENT] Error generating error response",
                error=str(e),
                agent_type="response",
            )
            return {
                "response": "I encountered an issue while processing your request. Please try rephrasing your question.",
                "success": False,
                "error": str(e),
                "agent_type": "response",
            }

    def _prepare_results_for_llm(self, db_results: list[dict], max_rows: int = 20) -> str:
        """Prepare database results for LLM processing.

        Args:
            db_results: Raw database results
            max_rows: Maximum number of rows to include

        Returns:
            Formatted string representation of results
        """
        if not db_results:
            return "No results found."

        # Limit results to avoid token limits
        limited_results = db_results[:max_rows]

        # Format as clean JSON-like structure
        formatted_results = []
        for i, row in enumerate(limited_results, 1):
            # Clean up the row data
            clean_row = {}
            for key, value in row.items():
                if value is not None:
                    # Convert values to strings and limit length
                    str_value = str(value)
                    if len(str_value) > 100:
                        str_value = str_value[:97] + "..."
                    clean_row[key] = str_value

            formatted_results.append(f"Result {i}: {clean_row}")

        result_text = "\n".join(formatted_results)

        # Add truncation notice if needed
        if len(db_results) > max_rows:
            result_text += f"\n... and {len(db_results) - max_rows} more results"

        return result_text

    def _format_query_context(self, query_context: dict[str, Any]) -> str:
        """Format query context for prompt inclusion.

        Args:
            query_context: Query context from Query Agent

        Returns:
            Formatted context string
        """
        parts = []

        if query_context.get("query_type"):
            parts.append(f"Query Type: {query_context['query_type']}")

        if query_context.get("tables"):
            parts.append(f"Tables: {', '.join(query_context['tables'])}")

        if query_context.get("execution_time"):
            parts.append(f"Execution Time: {query_context['execution_time']}ms")

        return " | ".join(parts) if parts else "No additional context"

    def _create_simple_summary(self, db_results: list[dict]) -> str:
        """Create a simple fallback summary of results.

        Args:
            db_results: Database results

        Returns:
            Simple summary string
        """
        if not db_results:
            return "No results found."

        count = len(db_results)
        if count == 1:
            # Show key fields from single result
            first_result = db_results[0]
            key_info = []
            for key in ["name", "email", "title", "designation", "project_name"]:
                if key in first_result and first_result[key]:
                    key_info.append(f"{key}: {first_result[key]}")

            if key_info:
                return f"Found 1 result - {', '.join(key_info[:3])}"
            else:
                return "Found 1 result"
        else:
            return f"Found {count} results"
