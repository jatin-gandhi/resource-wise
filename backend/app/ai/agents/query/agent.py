"""Enhanced Query Agent with integrated fuzzy term resolution."""

from typing import Any, Dict, List

import structlog
from app.ai.agents.base import BaseAgent
from app.ai.agents.fuzzy.classifier import FuzzyClassifier
from app.ai.agents.fuzzy.resolver import FuzzyTermResolver
from app.ai.core.config import AIConfig
from app.ai.prompts.query_prompts import QueryPrompts
from app.ai.services.schema import DatabaseSchemaService
from app.core.config import settings
from app.schemas.ai import QueryRequest
from langchain_openai import ChatOpenAI

logger = structlog.get_logger()


class QueryAgent(BaseAgent):
    """Enhanced Query Agent with integrated fuzzy term resolution."""

    def __init__(self, config: AIConfig, debug_explanations: bool = False):
        """Initialize the enhanced query agent.

        Args:
            config: AI configuration settings
            debug_explanations: Whether to generate query explanations for debugging
        """
        super().__init__(config)

        # Store debug flag
        self.debug_explanations = debug_explanations

        # Initialize services
        self.schema_service = DatabaseSchemaService()
        self.fuzzy_classifier = FuzzyClassifier(config)
        self.fuzzy_resolver = FuzzyTermResolver(config)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=0.5,
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Use unified fuzzy-enhanced prompts (handles both fuzzy and non-fuzzy queries)
        self.query_prompt = QueryPrompts.get_fuzzy_enhanced_query_prompt()
        self.validation_prompt = QueryPrompts.get_fuzzy_query_validation_prompt()
        self.explanation_prompt = QueryPrompts.get_query_explanation_prompt()

        # Initialize chains
        self.generation_chain = self.query_prompt | self.llm
        self.validation_chain = self.validation_prompt | self.llm
        self.explanation_chain = self.explanation_prompt | self.llm

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process the input to generate a database query with fuzzy term support.

        Args:
            input_data: Input data containing query and parameters

        Returns:
            Dictionary containing generated query and metadata
        """
        logger.info(
            "Received query request",
            input_data=input_data,
            agent_type="query_agent",
        )

        try:
            # Parse and validate intent data
            intent = QueryRequest(**input_data)

            # Get database schema
            schema = await self._get_database_schema()
            metadata = intent.metadata or {}

            # Check if query contains fuzzy terms and resolve them
            classification_result = await self.fuzzy_classifier.classify(intent.query)
            is_fuzzy = classification_result["classification"] == "fuzzy"

            logger.info(
                "Query classification completed",
                query=intent.query,
                is_fuzzy=is_fuzzy,
                fuzzy_terms=classification_result.get("fuzzy_terms", []),
                agent_type="query_agent",
            )

            # Resolve fuzzy terms (empty if non-fuzzy)
            resolved_terms = {}
            if is_fuzzy:
                resolved_terms = await self.fuzzy_resolver.resolve_fuzzy_terms(intent.query)
                logger.info(
                    "Fuzzy terms resolved",
                    resolved_terms=resolved_terms,
                    agent_type="query_agent",
                )

            # Generate SQL query using unified approach
            return await self._generate_query(intent, schema, metadata, resolved_terms)

        except Exception as e:
            logger.error(
                "Error processing query",
                error=str(e),
                input_data=input_data,
                agent_type="query_agent",
            )
            return {"query": "", "parameters": {}, "query_type": "unknown", "error": str(e)}

    async def _generate_query(
        self,
        intent: QueryRequest,
        schema: str,
        metadata: dict,
        resolved_terms: Dict[str, List[str]],
    ) -> dict[str, Any]:
        """Generate SQL query using unified fuzzy-enhanced approach.

        Args:
            intent: Query request object
            schema: Database schema
            metadata: Additional parameters
            resolved_terms: Resolved fuzzy terms (empty if non-fuzzy)

        Returns:
            Query result dictionary
        """
        logger.info(
            "Generating SQL query",
            query=intent.query,
            has_fuzzy_terms=bool(resolved_terms),
            agent_type="query_agent",
        )

        # Format resolved terms for the prompt (empty string if no fuzzy terms)
        resolved_terms_text = self._format_resolved_terms(resolved_terms)

        # Generate SQL with unified approach
        max_retries = 2
        final_query = ""

        for attempt in range(max_retries + 1):
            logger.info(
                f"SQL generation attempt {attempt + 1}/{max_retries + 1}",
                query=intent.query,
                agent_type="query_agent",
            )

            # Generate query
            chain_input = {
                "raw_query": intent.query,
                "schema": schema,
                "resolved_terms": resolved_terms_text,
                "parameters": str(metadata),
            }

            generated_query = await self.generation_chain.ainvoke(chain_input)
            raw_query = str(generated_query.content)

            logger.info(
                "Raw SQL generated",
                raw_sql=raw_query[:200] + "..." if len(raw_query) > 200 else raw_query,
                agent_type="query_agent",
            )

            # Validate and improve the query
            validation_input = {
                "query": raw_query,
                "schema": schema,
                "resolved_terms": resolved_terms_text,
            }
            validation_result = await self.validation_chain.ainvoke(validation_input)
            final_query = self._extract_query_from_validation(str(validation_result.content))

            # Validate against schema
            is_valid, schema_errors = await self._validate_query_against_schema(final_query)

            if is_valid:
                logger.info(
                    f"Query validated successfully on attempt {attempt + 1}",
                    agent_type="query_agent",
                )
                break
            else:
                logger.warning(
                    f"Schema validation failed on attempt {attempt + 1}",
                    errors=schema_errors,
                    agent_type="query_agent",
                )

        # Create result
        result = self._create_query_result(final_query, metadata, resolved_terms)

        # Add explanation if debug mode is enabled
        if self.debug_explanations:
            explanation = await self._generate_explanation(final_query, schema, resolved_terms_text)
            result["explanation"] = explanation

        logger.info(
            "SQL query generated successfully",
            query_type=result["query_type"],
            has_fuzzy_context=bool(resolved_terms),
            final_sql=final_query,
            agent_type="query_agent",
        )

        return result

    def _format_resolved_terms(self, resolved_terms: Dict[str, List[str]]) -> str:
        """Format resolved terms for the prompt.

        Args:
            resolved_terms: Dictionary of fuzzy terms to resolved values

        Returns:
            Formatted string for the prompt
        """
        if not resolved_terms:
            return "No fuzzy terms to resolve."

        formatted_terms = []
        for fuzzy_term, resolved_values in resolved_terms.items():
            values_str = ", ".join(f"'{v}'" for v in resolved_values)
            formatted_terms.append(f"- '{fuzzy_term}' → [{values_str}]")

        return "\n".join(formatted_terms)

    def _create_query_result(
        self, query: str, metadata: dict, resolved_terms: Dict[str, List[str]] = None
    ) -> dict[str, Any]:
        """Create the final query result dictionary.

        Args:
            query: Generated SQL query
            metadata: Query metadata
            resolved_terms: Optional resolved fuzzy terms

        Returns:
            Query result dictionary
        """
        query_type = self._detect_query_type(query)
        tables = self._extract_tables(query)
        joins = self._extract_joins(query)
        filters = self._extract_filters(query)

        result = {
            "query": query,
            "parameters": metadata,
            "query_type": query_type,
            "tables": tables,
            "joins": joins,
            "filters": filters,
        }

        # Add fuzzy context if available
        if resolved_terms:
            result["fuzzy_context"] = {
                "resolved_terms": resolved_terms,
                "explanation": self._create_fuzzy_explanation(resolved_terms),
            }

        return result

    def _create_fuzzy_explanation(self, resolved_terms: Dict[str, List[str]]) -> str:
        """Create explanation of fuzzy term resolution.

        Args:
            resolved_terms: Dictionary of resolved terms

        Returns:
            Human-readable explanation
        """
        explanations = []
        for fuzzy_term, resolved_values in resolved_terms.items():
            if len(resolved_values) == 1:
                explanations.append(f"'{fuzzy_term}' → '{resolved_values[0]}'")
            else:
                values_str = "', '".join(resolved_values[:3])
                if len(resolved_values) > 3:
                    explanations.append(
                        f"'{fuzzy_term}' → '{values_str}' and {len(resolved_values) - 3} more"
                    )
                else:
                    explanations.append(f"'{fuzzy_term}' → '{values_str}'")

        return "Resolved fuzzy terms: " + "; ".join(explanations)

    async def _generate_explanation(self, query: str, schema: str, resolved_terms: str) -> str:
        """Generate explanation for the query.

        Args:
            query: Generated SQL query
            schema: Database schema
            resolved_terms: Formatted resolved terms

        Returns:
            Human-readable explanation of the query
        """
        try:
            explanation_input = {
                "query": query,
                "schema": schema,
                "resolved_terms": resolved_terms,
            }

            explanation_result = await self.explanation_chain.ainvoke(explanation_input)
            return str(explanation_result.content).strip()

        except Exception as e:
            logger.warning(
                "Failed to generate query explanation",
                error=str(e),
                agent_type="query_agent",
            )
            return f"Query explanation unavailable: {str(e)}"

    # Utility methods
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of SQL operation from the query."""
        if not query:
            return "unknown"

        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT"):
            return "select"
        elif query_upper.startswith("INSERT"):
            return "insert"
        elif query_upper.startswith("UPDATE"):
            return "update"
        elif query_upper.startswith("DELETE"):
            return "delete"
        elif query_upper.startswith("WITH"):
            return "select"
        else:
            return "unknown"

    def _extract_query_from_validation(self, validation_result: str) -> str:
        """Extract the final query from validation result."""
        query = validation_result.replace("```sql", "").replace("```", "")

        prefixes_to_remove = [
            "Corrected SQL Query:",
            "SQL Query:",
            "Query:",
            "Here is the corrected query:",
            "The corrected query is:",
        ]

        for prefix in prefixes_to_remove:
            if query.strip().startswith(prefix):
                query = query.replace(prefix, "", 1).strip()

        query = " ".join(query.split())

        if query and not query.rstrip().endswith(";"):
            query = query.rstrip() + ";"

        return query

    async def _validate_query_against_schema(self, query: str) -> tuple[bool, list[str]]:
        """Validate query against database schema."""
        errors = []

        try:
            table_names = await self.schema_service.get_table_names()
            used_tables = set()

            words = query.split()
            for i, word in enumerate(words):
                if word.upper() in ["FROM", "JOIN"] and i + 1 < len(words):
                    table_name = words[i + 1].strip("();,").split()[0]
                    used_tables.add(table_name.lower())

            for table in used_tables:
                if table not in [t.lower() for t in table_names]:
                    errors.append(f"Table '{table}' does not exist in schema")

            return len(errors) == 0, errors

        except Exception as e:
            logger.warning("Error validating query against schema", error=str(e))
            return True, []

    async def _get_database_schema(self) -> str:
        """Get the database schema for query generation."""
        return await self.schema_service.get_schema_description()

    def _extract_tables(self, query: str) -> list[str]:
        """Extract table names from SQL query."""
        tables = []
        for line in query.split():
            if "FROM" in line.upper() or "JOIN" in line.upper():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.upper() in ["FROM", "JOIN"] and i + 1 < len(parts):
                        table = parts[i + 1].strip(";")
                        if table not in tables:
                            tables.append(table)
        return tables

    def _extract_joins(self, query: str) -> list[str]:
        """Extract JOIN clauses from SQL query."""
        joins = []
        words = query.split()
        for i, word in enumerate(words):
            if word.upper() == "JOIN":
                join_clause = " ".join(words[i : i + 5])
                joins.append(join_clause)
        return joins

    def _extract_filters(self, query: str) -> str:
        """Extract WHERE clause from SQL query."""
        if "WHERE" not in query.upper():
            return "1=1"

        where_start = query.upper().find("WHERE")
        where_clause = query[where_start:].split(";")[0]
        return where_clause.replace("WHERE", "").strip()
