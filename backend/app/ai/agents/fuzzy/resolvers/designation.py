"""Designation resolver for handling role abbreviations."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.config.designations import DesignationConfig
from app.ai.agents.fuzzy.resolvers.base import BaseResolver
from app.ai.core.config import AIConfig

logger = structlog.get_logger(__name__)


class DesignationResolver(BaseResolver):
    """Resolver for designation abbreviations using predefined mappings."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.designation_config = DesignationConfig

    def can_handle(self, term: str) -> bool:
        """Check if this resolver can handle the term."""
        return self.designation_config.is_known_designation_abbreviation(term)

    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve designation abbreviations to full role names."""
        logger.info(
            "Resolving designation abbreviations", agent_type="designation_resolver", terms=terms
        )

        resolved_terms = {}

        for term in terms:
            if not self.can_handle(term):
                continue

            mapped_designations = self.designation_config.get_mapped_designations(term)

            if mapped_designations:
                resolved_terms[term] = mapped_designations

                logger.info(
                    "Designation abbreviation resolved",
                    agent_type="designation_resolver",
                    term=term,
                    count=len(mapped_designations),
                    designations=mapped_designations,
                )

        return resolved_terms
