"""Response generation agent implementation."""

from typing import Any

import structlog
from app.ai.agents.base import BaseAgent
from app.ai.core.config import AIConfig
from app.ai.prompts.response_prompts import ResponsePrompts
from app.core.config import settings
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
            temperature=0.5,  # Slightly higher temperature for more natural responses
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Get prompts from prompts module
        self.response_generation_prompt = ResponsePrompts.get_response_generation_prompt()
        self.error_response_prompt = ResponsePrompts.get_error_response_prompt()

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

            # Debug logging to understand what we're receiving
            logger.info(
                "[RESPONSE-AGENT] Processing db_results",
                result_count=result_count,
                query_context=query_context,
                sample_row=db_results[0] if db_results else None,
                agent_type="response",
            )

            # Prepare data for LLM (limit size to avoid token limits)
            limited_results = self._prepare_results_for_llm(db_results)

            # Debug what's being sent to LLM
            logger.info(
                "[RESPONSE-AGENT] Prepared data for LLM",
                formatted_length=len(limited_results),
                formatted_preview=(
                    limited_results[:300] + "..." if len(limited_results) > 300 else limited_results
                ),
                agent_type="response",
            )

            # Format query context for prompt
            context_summary = self._format_query_context(query_context)

            # Generate response using LLM
            chain_input = {
                "original_query": original_query,
                "db_results": limited_results,
                "query_context": context_summary,
                "result_count": result_count,
            }

            # Log exactly what we're sending to the LLM
            logger.info(
                "[RESPONSE-AGENT] Sending to LLM",
                chain_input_keys=list(chain_input.keys()),
                original_query=original_query,
                result_count=result_count,
                context_summary=context_summary,
                agent_type="response",
            )

            result = await self.response_chain.ainvoke(chain_input)
            natural_response = str(result.content)

            # Log what the LLM returned
            logger.info(
                "[RESPONSE-AGENT] LLM Response received",
                response_length=len(natural_response),
                response_preview=(
                    natural_response[:200] + "..."
                    if len(natural_response) > 200
                    else natural_response
                ),
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

    def _prepare_results_for_llm(self, db_results: list[dict]) -> str:
        """Prepare database results for LLM processing with intelligent formatting.

        Args:
            db_results: Raw database results

        Returns:
            Formatted string representation of results optimized for the result count
        """
        if not db_results:
            return "No results found."

        result_count = len(db_results)

        # Apply different strategies based on result count
        if result_count == 1:
            return self._format_single_result(db_results[0])
        elif result_count <= 5:
            return self._format_small_set(db_results)
        elif result_count <= 20:
            return self._format_medium_set(db_results)
        elif result_count <= 50:
            return self._format_large_set(db_results)
        else:
            return self._format_very_large_set(db_results)

    def _format_single_result(self, result: dict) -> str:
        """Format a single result with full detail."""
        clean_result = self._clean_row_data(result)
        return f"Single Result: {clean_result}"

    def _format_small_set(self, results: list[dict]) -> str:
        """Format 2-5 results with detailed information."""
        formatted_results = []
        for i, row in enumerate(results, 1):
            clean_row = self._clean_row_data(row)
            formatted_results.append(f"Record {i}: {clean_row}")
        return "\n".join(formatted_results)

    def _format_medium_set(self, results: list[dict]) -> str:
        """Format 6-20 results optimized for table presentation."""
        # Include all results for medium sets
        formatted_results = []
        for i, row in enumerate(results, 1):
            clean_row = self._clean_row_data(row)
            formatted_results.append(f"Row {i}: {clean_row}")

        result_text = "\n".join(formatted_results)
        result_text += (
            f"\n\nTotal Records: {len(results)} (All records included for table formatting)"
        )
        return result_text

    def _format_large_set(self, results: list[dict]) -> str:
        """Format 21-50 results with summary + key data."""
        # Show first 30 results + summary
        sample_size = min(30, len(results))
        formatted_results = []

        for i, row in enumerate(results[:sample_size], 1):
            clean_row = self._clean_row_data(row)
            formatted_results.append(f"Row {i}: {clean_row}")

        result_text = "\n".join(formatted_results)

        if len(results) > sample_size:
            result_text += f"\n\n[Showing first {sample_size} of {len(results)} total records]"
            result_text += (
                f"\nRemaining {len(results) - sample_size} records available for analysis."
            )

        # Add summary statistics
        result_text += self._generate_summary_stats(results)
        return result_text

    def _format_very_large_set(self, results: list[dict]) -> str:
        """Format 50+ results with analytics focus."""
        # Show sample + comprehensive analytics
        sample_size = 20
        formatted_results = []

        for i, row in enumerate(results[:sample_size], 1):
            clean_row = self._clean_row_data(row)
            formatted_results.append(f"Sample Row {i}: {clean_row}")

        result_text = f"LARGE DATASET ANALYSIS ({len(results)} total records)\n\n"
        result_text += "SAMPLE DATA:\n" + "\n".join(formatted_results)
        result_text += f"\n\n[Sample showing first {sample_size} of {len(results)} total records]"

        # Add comprehensive analytics
        result_text += self._generate_comprehensive_analytics(results)
        return result_text

    def _clean_row_data(self, row: dict) -> dict:
        """Clean and format a single row of data."""
        clean_row = {}
        for key, value in row.items():
            if value is not None:
                # Convert values to strings and limit length for very long values
                str_value = str(value)
                if len(str_value) > 200:  # Increased limit for better context
                    str_value = str_value[:197] + "..."
                clean_row[key] = str_value
        return clean_row

    def _generate_summary_stats(self, results: list[dict]) -> str:
        """Generate summary statistics for large datasets."""
        if not results:
            return ""

        stats = [f"\n\nSUMMARY STATISTICS:"]
        stats.append(f"- Total Records: {len(results)}")

        # Analyze common fields
        sample_row = results[0]
        for key in sample_row.keys():
            if key.lower() in ["status", "department", "location", "type", "category"]:
                unique_values = set(str(row.get(key, "")) for row in results if row.get(key))
                if len(unique_values) <= 10:  # Only show if manageable number
                    stats.append(
                        f"- {key.title()} Distribution: {len(unique_values)} unique values"
                    )

        return "\n".join(stats)

    def _generate_comprehensive_analytics(self, results: list[dict]) -> str:
        """Generate comprehensive analytics for very large datasets."""
        if not results:
            return ""

        analytics = [f"\n\nCOMPREHENSIVE ANALYTICS:"]
        analytics.append(f"- Dataset Size: {len(results)} records")

        # Field analysis
        sample_row = results[0]
        analytics.append(f"- Available Fields: {len(sample_row)} columns")
        analytics.append(
            f"- Field Names: {', '.join(list(sample_row.keys())[:10])}{'...' if len(sample_row) > 10 else ''}"
        )

        # Distribution analysis for key fields
        key_fields = ["status", "department", "location", "type", "category", "priority"]
        for field in key_fields:
            if field in sample_row:
                unique_values = set(str(row.get(field, "")) for row in results if row.get(field))
                if unique_values and len(unique_values) <= 20:
                    analytics.append(
                        f"- {field.title()} Categories: {', '.join(sorted(unique_values))}"
                    )

        analytics.append("\nRECOMMENDATION: Use more specific filters to get targeted results.")
        return "\n".join(analytics)

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
