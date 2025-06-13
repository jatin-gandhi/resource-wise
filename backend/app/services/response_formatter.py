"""Response formatting service for database query results."""

import json
from typing import Any

import structlog

logger = structlog.get_logger()


class ResponseFormatter:
    """Service for formatting database query results into user-friendly responses."""

    def __init__(self):
        """Initialize response formatter."""
        self.max_table_rows = 20  # Maximum rows to show in table format
        self.max_list_items = 50  # Maximum items to show in list format

    async def format_database_response(
        self, query_result: dict[str, Any], query_context: dict[str, Any], original_query: str
    ) -> dict[str, Any]:
        """Format database query results into user-friendly response.

        Args:
            query_result: Raw database query results
            query_context: Context about the query (intent, parameters, etc.)
            original_query: Original user query

        Returns:
            Formatted response dictionary
        """
        try:
            if not query_result.get("success", False):
                return await self._format_error_response(query_result, original_query)

            data = query_result.get("data", [])
            columns = query_result.get("columns", [])
            row_count = query_result.get("row_count", 0)

            # Determine response format based on query context and data
            response_format = self._determine_response_format(query_context, data, columns)

            # Generate formatted response
            if response_format == "table":
                return await self._format_table_response(
                    data, columns, query_result, query_context, original_query
                )
            elif response_format == "list":
                return await self._format_list_response(
                    data, columns, query_result, query_context, original_query
                )
            elif response_format == "summary":
                return await self._format_summary_response(
                    data, columns, query_result, query_context, original_query
                )
            else:
                return await self._format_default_response(
                    data, columns, query_result, query_context, original_query
                )

        except Exception as e:
            logger.error("Error formatting database response", error=str(e))
            return {
                "response": f"I retrieved the data successfully, but encountered an error formatting the response: {str(e)}",
                "formatted_data": None,
                "summary": "Data formatting error",
                "success": False,
            }

    def _determine_response_format(
        self, query_context: dict[str, Any], data: list[dict], columns: list[str]
    ) -> str:
        """Determine the best response format based on data characteristics.

        Args:
            query_context: Query context information
            data: Query result data
            columns: Column names

        Returns:
            Response format type: 'table', 'list', 'summary', or 'default'
        """
        if not data:
            return "summary"

        row_count = len(data)
        col_count = len(columns)

        # Determine based on query type
        query_type = query_context.get("query_type", "unknown")

        if query_type == "analytics":
            return "summary"
        elif query_type in ["resource_search", "skill_search", "department_search"]:
            if row_count <= 5 and col_count <= 4:
                return "list"
            elif row_count <= self.max_table_rows:
                return "table"
            else:
                return "summary"

        # Default logic based on data size
        if row_count == 1:
            return "list"
        elif row_count <= self.max_table_rows and col_count <= 8:
            return "table"
        else:
            return "summary"

    async def _format_table_response(
        self,
        data: list[dict],
        columns: list[str],
        query_result: dict[str, Any],
        query_context: dict[str, Any],
        original_query: str,
    ) -> dict[str, Any]:
        """Format response as a table."""
        try:
            # Create markdown table
            table_md = self._create_markdown_table(data, columns)

            # Generate summary
            summary = self._generate_data_summary(data, columns, query_context)

            # Create response
            response_parts = [summary, "", table_md]

            # Add metadata if results were truncated
            if query_result.get("truncated", False):
                response_parts.append(
                    f"\n*Note: Results limited to {len(data)} rows out of {query_result.get('total_rows', 'many')} total.*"
                )

            return {
                "response": "\n".join(response_parts),
                "formatted_data": {
                    "type": "table",
                    "table": table_md,
                    "data": data[: self.max_table_rows],  # Limit for JSON response
                    "columns": columns,
                },
                "summary": summary,
                "success": True,
                "metadata": {
                    "format": "table",
                    "row_count": len(data),
                    "column_count": len(columns),
                    "execution_time": query_result.get("execution_time", 0),
                },
            }

        except Exception as e:
            logger.error("Error formatting table response", error=str(e))
            return await self._format_default_response(
                data, columns, query_result, query_context, original_query
            )

    async def _format_list_response(
        self,
        data: list[dict],
        columns: list[str],
        query_result: dict[str, Any],
        query_context: dict[str, Any],
        original_query: str,
    ) -> dict[str, Any]:
        """Format response as a list."""
        try:
            # Generate summary
            summary = self._generate_data_summary(data, columns, query_context)

            # Create list items
            list_items = []
            for i, row in enumerate(data[: self.max_list_items], 1):
                item = self._format_list_item(row, columns, i)
                list_items.append(item)

            # Create response
            response_parts = [summary, ""]
            response_parts.extend(list_items)

            # Add metadata if results were truncated
            if len(data) > self.max_list_items:
                response_parts.append(
                    f"\n*Showing first {self.max_list_items} results out of {len(data)} total.*"
                )

            return {
                "response": "\n".join(response_parts),
                "formatted_data": {
                    "type": "list",
                    "items": list_items,
                    "data": data[: self.max_list_items],
                },
                "summary": summary,
                "success": True,
                "metadata": {
                    "format": "list",
                    "row_count": len(data),
                    "execution_time": query_result.get("execution_time", 0),
                },
            }

        except Exception as e:
            logger.error("Error formatting list response", error=str(e))
            return await self._format_default_response(
                data, columns, query_result, query_context, original_query
            )

    async def _format_summary_response(
        self,
        data: list[dict],
        columns: list[str],
        query_result: dict[str, Any],
        query_context: dict[str, Any],
        original_query: str,
    ) -> dict[str, Any]:
        """Format response as a summary with key insights."""
        try:
            # Generate comprehensive summary
            summary = self._generate_comprehensive_summary(data, columns, query_context)

            # Add key statistics
            stats = self._generate_statistics(data, columns)

            response_parts = [summary]
            if stats:
                response_parts.extend(["", "**Key Statistics:**"] + stats)

            # Add sample data if available
            if data and len(data) <= 5:
                response_parts.extend(["", "**Sample Results:**"])
                for i, row in enumerate(data[:3], 1):
                    item = self._format_list_item(row, columns, i)
                    response_parts.append(item)

            return {
                "response": "\n".join(response_parts),
                "formatted_data": {
                    "type": "summary",
                    "summary": summary,
                    "statistics": stats,
                    "sample_data": data[:5] if data else [],
                },
                "summary": summary,
                "success": True,
                "metadata": {
                    "format": "summary",
                    "row_count": len(data),
                    "execution_time": query_result.get("execution_time", 0),
                },
            }

        except Exception as e:
            logger.error("Error formatting summary response", error=str(e))
            return await self._format_default_response(
                data, columns, query_result, query_context, original_query
            )

    async def _format_default_response(
        self,
        data: list[dict],
        columns: list[str],
        query_result: dict[str, Any],
        query_context: dict[str, Any],
        original_query: str,
    ) -> dict[str, Any]:
        """Format default response when other formats fail."""
        try:
            if not data:
                return {
                    "response": "No results found for your query.",
                    "formatted_data": {"type": "empty", "data": []},
                    "summary": "No results found",
                    "success": True,
                    "metadata": {"format": "empty", "row_count": 0},
                }

            summary = f"Found {len(data)} result{'s' if len(data) != 1 else ''}"

            # Show first few results as JSON
            sample_data = data[:3]
            json_str = json.dumps(sample_data, indent=2, default=str)

            response = f"{summary}:\n\n```json\n{json_str}\n```"

            if len(data) > 3:
                response += f"\n\n*Showing first 3 results out of {len(data)} total.*"

            return {
                "response": response,
                "formatted_data": {"type": "json", "data": sample_data},
                "summary": summary,
                "success": True,
                "metadata": {"format": "json", "row_count": len(data)},
            }

        except Exception as e:
            logger.error("Error formatting default response", error=str(e))
            return {
                "response": f"Retrieved {len(data) if data else 0} results, but encountered a formatting error.",
                "formatted_data": None,
                "summary": "Formatting error",
                "success": False,
            }

    async def _format_error_response(
        self, query_result: dict[str, Any], original_query: str
    ) -> dict[str, Any]:
        """Format error response."""
        error_type = query_result.get("error_type", "UNKNOWN")
        error_msg = query_result.get("error", "Unknown error occurred")

        # Create user-friendly error messages
        user_messages = {
            "SECURITY_VIOLATION": "I cannot execute this query due to security restrictions. Please try a different approach.",
            "TIMEOUT": "The query took too long to execute. Please try a more specific query.",
            "SYNTAX_ERROR": "There was an issue with the query syntax. Let me try to rephrase your request.",
            "CONNECTION_ERROR": "I'm having trouble connecting to the database. Please try again in a moment.",
            "PERMISSION_ERROR": "I don't have permission to access the requested data.",
        }

        user_message = user_messages.get(
            error_type, f"I encountered an error while processing your query: {error_msg}"
        )

        return {
            "response": user_message,
            "formatted_data": None,
            "summary": f"Query failed: {error_type}",
            "success": False,
            "error": error_msg,
            "error_type": error_type,
        }

    def _create_markdown_table(self, data: list[dict], columns: list[str]) -> str:
        """Create a markdown table from data."""
        if not data or not columns:
            return "No data to display."

        # Limit columns for readability
        display_columns = columns[:8]  # Max 8 columns

        # Create header
        header = "| " + " | ".join(display_columns) + " |"
        separator = "| " + " | ".join(["---"] * len(display_columns)) + " |"

        # Create rows
        rows = []
        for row in data[: self.max_table_rows]:
            row_values = []
            for col in display_columns:
                value = row.get(col, "")
                # Handle None values and long strings
                if value is None:
                    value = ""
                else:
                    value = str(value)
                    if len(value) > 50:
                        value = value[:47] + "..."
                row_values.append(value)

            rows.append("| " + " | ".join(row_values) + " |")

        return "\n".join([header, separator] + rows)

    def _format_list_item(self, row: dict, columns: list[str], index: int) -> str:
        """Format a single row as a list item."""
        # Determine key fields to display
        key_fields = self._get_key_fields(columns)

        parts = [f"{index}."]
        for field in key_fields[:3]:  # Show max 3 key fields
            value = row.get(field)
            if value is not None:
                parts.append(f"**{field.replace('_', ' ').title()}:** {value}")

        return " ".join(parts)

    def _get_key_fields(self, columns: list[str]) -> list[str]:
        """Determine key fields to display based on column names."""
        # Priority order for common fields
        priority_fields = [
            "name",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "title",
            "designation",
            "department",
            "skill_name",
            "project_name",
            "status",
        ]

        key_fields = []

        # Add priority fields that exist
        for field in priority_fields:
            if field in columns:
                key_fields.append(field)

        # Add remaining fields
        for col in columns:
            if col not in key_fields:
                key_fields.append(col)

        return key_fields

    def _generate_data_summary(
        self, data: list[dict], columns: list[str], query_context: dict[str, Any]
    ) -> str:
        """Generate a summary of the data."""
        if not data:
            return "No results found for your query."

        count = len(data)
        query_type = query_context.get("query_type", "search")

        # Generate context-aware summary
        if query_type == "resource_search":
            return f"Found {count} employee{'s' if count != 1 else ''} matching your criteria:"
        elif query_type == "skill_search":
            return f"Found {count} result{'s' if count != 1 else ''} for your skill search:"
        elif query_type == "department_search":
            return f"Found {count} result{'s' if count != 1 else ''} in the specified department:"
        elif query_type == "analytics":
            return f"Analysis complete. Here are the results ({count} record{'s' if count != 1 else ''}):"
        else:
            return f"Query completed successfully. Found {count} result{'s' if count != 1 else ''}:"

    def _generate_comprehensive_summary(
        self, data: list[dict], columns: list[str], query_context: dict[str, Any]
    ) -> str:
        """Generate a comprehensive summary with insights."""
        if not data:
            return "No results found for your query."

        count = len(data)
        summary_parts = [f"Analysis of {count} record{'s' if count != 1 else ''}:"]

        # Add insights based on data patterns
        insights = self._extract_insights(data, columns)
        if insights:
            summary_parts.extend(insights)

        return "\n".join(summary_parts)

    def _extract_insights(self, data: list[dict], columns: list[str]) -> list[str]:
        """Extract insights from the data."""
        insights = []

        try:
            # Look for common patterns
            if "status" in columns:
                status_counts = {}
                for row in data:
                    status = row.get("status")
                    if status:
                        status_counts[status] = status_counts.get(status, 0) + 1

                if status_counts:
                    most_common = max(status_counts, key=status_counts.get)
                    insights.append(
                        f"- Most common status: {most_common} ({status_counts[most_common]} records)"
                    )

            # Add more insight patterns as needed

        except Exception as e:
            logger.debug("Error extracting insights", error=str(e))

        return insights

    def _generate_statistics(self, data: list[dict], columns: list[str]) -> list[str]:
        """Generate key statistics from the data."""
        stats = []

        try:
            stats.append(f"- Total records: {len(data)}")
            stats.append(f"- Data fields: {len(columns)}")

            # Add more statistics based on data types

        except Exception as e:
            logger.debug("Error generating statistics", error=str(e))

        return stats


# Global response formatter instance
response_formatter = ResponseFormatter()
