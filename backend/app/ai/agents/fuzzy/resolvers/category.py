"""Skill category resolver using predefined mappings."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.config.categories import SkillCategoryConfig
from app.ai.agents.fuzzy.resolvers.base import BaseResolver, DatabaseMixin, VectorSearchMixin
from app.ai.core.config import AIConfig

logger = structlog.get_logger(__name__)


class CategoryResolver(BaseResolver, DatabaseMixin, VectorSearchMixin):
    """Resolver for skill categories using predefined mappings."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.config_manager = SkillCategoryConfig

    def can_handle(self, term: str) -> bool:
        """Check if this resolver can handle the term."""
        return self.config_manager.is_known_category(term)

    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve skill category terms using predefined mappings."""
        logger.info("Resolving skill categories", agent_type="category_resolver", terms=terms)

        resolved_terms = {}

        # Get available data once for all terms
        available_skills, available_roles = await self.get_available_data()

        for term in terms:
            if not self.can_handle(term):
                continue

            resolved_items = await self._resolve_single_category(
                term, available_skills, available_roles
            )

            if resolved_items:
                resolved_terms[term] = resolved_items

                logger.info(
                    "Category resolved",
                    agent_type="category_resolver",
                    term=term,
                    count=len(resolved_items),
                    items=resolved_items[:3],
                )

        return resolved_terms

    async def _resolve_single_category(
        self, term: str, available_skills: set, available_roles: set
    ) -> List[str]:
        """Resolve a single category term."""
        # Resolve to canonical category name
        canonical_category = self.config_manager.resolve_category(term)
        category_data = self.config_manager.get_category_data(canonical_category)

        if not category_data:
            return []

        resolved_items = []

        # Add available skills from this category
        category_skills = category_data.get("skills", [])
        available_category_skills = self.filter_available_items(category_skills, available_skills)
        resolved_items.extend(available_category_skills)

        # Add available roles from this category
        category_roles = category_data.get("roles", [])
        available_category_roles = self.filter_available_items(category_roles, available_roles)
        resolved_items.extend(available_category_roles)

        # Remove duplicates and limit results
        max_results = self.config_manager.get_setting("max_results_per_category", 20)
        unique_items = list(dict.fromkeys(resolved_items))[:max_results]

        return unique_items


class VectorResolver(BaseResolver, VectorSearchMixin):
    """Resolver using vector similarity search for unknown terms."""

    def can_handle(self, term: str) -> bool:
        """This resolver can handle any term as a fallback."""
        return True

    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve terms using vector similarity search."""
        logger.info(
            "Resolving terms with vector similarity", agent_type="vector_resolver", terms=terms
        )

        resolved_terms = {}

        for term in terms:
            # Get settings from config
            threshold = SkillCategoryConfig.get_setting("vector_similarity_threshold", 0.2)

            similar_items = await self.vector_similarity_search(term, limit=10, threshold=threshold)

            if similar_items:
                resolved_terms[term] = similar_items

                logger.info(
                    "Vector similarity resolved",
                    agent_type="vector_resolver",
                    term=term,
                    count=len(similar_items),
                    items=similar_items[:3],
                )

        return resolved_terms
