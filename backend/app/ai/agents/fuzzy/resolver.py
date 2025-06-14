"""Fuzzy term resolver for converting vague terms to specific database values."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.classifier import FuzzyClassifier
from app.ai.core.config import AIConfig

logger = structlog.get_logger()


class FuzzyTermResolver:
    """Resolver for converting fuzzy terms to specific database values using semantic similarity."""

    def __init__(self, config: AIConfig):
        """Initialize the fuzzy term resolver.

        Args:
            config: AI configuration settings
        """
        self.config = config
        self.classifier = FuzzyClassifier(config)

    async def resolve_fuzzy_terms(self, query: str) -> Dict[str, List[str]]:
        """Resolve fuzzy terms in a query to specific database values.

        Args:
            query: User query containing fuzzy terms

        Returns:
            Dictionary mapping fuzzy terms to their resolved values
        """
        try:
            logger.info(
                "Starting fuzzy term resolution",
                query=query,
                agent_type="fuzzy_resolver",
            )

            # Use classifier to extract fuzzy terms
            fuzzy_terms = await self.classifier.get_fuzzy_terms(query)

            if not fuzzy_terms:
                logger.info(
                    "No fuzzy terms found",
                    query=query,
                    agent_type="fuzzy_resolver",
                )
                return {}

            logger.info(
                "Extracted fuzzy terms",
                fuzzy_terms=fuzzy_terms,
                query=query,
                agent_type="fuzzy_resolver",
            )

            # Use hybrid resolver for parallel resolution of designations + skills
            from app.ai.agents.fuzzy.resolvers.hybrid import HybridFuzzyResolver

            hybrid_resolver = HybridFuzzyResolver(self.config)
            resolved_terms = await hybrid_resolver.resolve_fuzzy_terms(fuzzy_terms)

            logger.info(
                "Fuzzy terms resolved",
                resolved_terms=resolved_terms,
                query=query,
                agent_type="fuzzy_resolver",
            )

            return resolved_terms

        except Exception as e:
            logger.error(
                "Error resolving fuzzy terms",
                error=str(e),
                query=query,
                agent_type="fuzzy_resolver",
            )
            return {}
