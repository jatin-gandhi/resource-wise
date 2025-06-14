"""Skill resolver for handling skill variations and categories."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.config.categories import SkillCategoryConfig
from app.ai.agents.fuzzy.resolvers.base import BaseResolver, DatabaseMixin
from app.ai.core.config import AIConfig

logger = structlog.get_logger(__name__)


class SkillResolver(BaseResolver, DatabaseMixin):
    """Resolver for skill variations using predefined categories + tsvector fuzzy search."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.category_config = SkillCategoryConfig

    def can_handle(self, term: str) -> bool:
        """Check if this resolver can handle the term.

        Returns True for any term that could be a skill or technology,
        since we'll try both static mappings and fuzzy search.
        """
        # First check static category mappings
        if self.category_config.is_known_category(term):
            return True

        # For other terms, we'll let the resolver try fuzzy search
        # This is more permissive but we'll validate in resolve_terms
        return len(term) <= 30 and not any(char.isdigit() for char in term)

    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve skill terms using static category mappings + tsvector fuzzy search."""
        logger.info("Resolving skill terms", agent_type="skill_resolver", terms=terms)

        resolved_terms = {}

        for term in terms:
            # Step 1: Try static category mappings first (for broad categories)
            static_result = self._get_mapped_skills_from_category(term)
            if static_result:
                resolved_terms[term] = static_result
                logger.info(
                    "Skill resolved via static category mapping",
                    agent_type="skill_resolver",
                    term=term,
                    count=len(static_result),
                    skills=static_result,
                )
                continue

            # Step 2: Try tsvector fuzzy search on employee_skills table
            fuzzy_result = await self._fuzzy_search_skills(term)
            if fuzzy_result:
                resolved_terms[term] = fuzzy_result
                logger.info(
                    "Skill resolved via fuzzy search",
                    agent_type="skill_resolver",
                    term=term,
                    count=len(fuzzy_result),
                    skills=fuzzy_result,
                )

        return resolved_terms

    def _get_mapped_skills_from_category(self, term: str) -> List[str]:
        """Get skills from static category mappings."""
        if not self.category_config.is_known_category(term):
            return []

        category = self.category_config.resolve_category(term)
        category_data = self.category_config.get_category_data(category)
        return category_data.get("skills", [])

    async def _fuzzy_search_skills(self, term: str) -> List[str]:
        """Use tsvector and similarity to find matching skills in the database."""
        from app.core.database import get_async_session
        from sqlalchemy import text

        session_generator = get_async_session()
        session = await session_generator.__anext__()

        try:
            # Use both tsvector full-text search and pg_trgm similarity
            query = text(
                """
            SELECT DISTINCT es.skill_name, 
                   GREATEST(
                       ts_rank(to_tsvector('english', es.skill_name), plainto_tsquery('english', :term)),
                       similarity(es.skill_name, :term)
                   ) as relevance_score
            FROM employee_skills es
            WHERE (
                to_tsvector('english', es.skill_name) @@ plainto_tsquery('english', :term)
                OR similarity(es.skill_name, :term) > 0.3
            )
            ORDER BY relevance_score DESC
            LIMIT 10
            """
            )

            result = await session.execute(query, {"term": term})
            rows = result.fetchall()

            if rows:
                # Return skills with relevance score > 0.2 for quality filtering
                results = [row[0] for row in rows if row[1] > 0.2]
                return results[:5]  # Limit to top 5 matches

        except Exception as e:
            logger.warning(
                "Fuzzy skill search failed",
                agent_type="skill_resolver",
                term=term,
                error=str(e),
            )
        finally:
            await session.close()

        return []
