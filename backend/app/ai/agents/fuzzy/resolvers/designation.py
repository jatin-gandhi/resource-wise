"""Designation resolver for handling role abbreviations."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.config.designations import DesignationConfig
from app.ai.agents.fuzzy.resolvers.base import BaseResolver, DatabaseMixin
from app.ai.core.config import AIConfig

logger = structlog.get_logger(__name__)


class DesignationResolver(BaseResolver, DatabaseMixin):
    """Resolver for designation abbreviations using predefined mappings + tsvector fuzzy search."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.designation_config = DesignationConfig

    def can_handle(self, term: str) -> bool:
        """Check if this resolver can handle the term.

        Returns True for terms that are likely to be designations/roles.
        """
        # First check static mappings
        if self.designation_config.is_known_designation_abbreviation(term):
            return True

        # Check for designation-like terms (roles, titles, positions)
        term_lower = term.lower().strip()

        # Common designation keywords
        designation_keywords = [
            "lead",
            "manager",
            "engineer",
            "developer",
            "architect",
            "analyst",
            "director",
            "officer",
            "specialist",
            "consultant",
            "coordinator",
            "supervisor",
            "administrator",
            "technician",
            "designer",
            "tester",
            "qa",
            "quality",
            "assurance",
            "senior",
            "junior",
            "principal",
            "staff",
            "associate",
            "intern",
            "trainee",
            "head",
            "chief",
        ]

        # Check if term contains designation keywords
        for keyword in designation_keywords:
            if keyword in term_lower:
                return True

                # Check for common abbreviation patterns (2-4 uppercase letters)
        if len(term) <= 4 and term.isupper() and term.isalpha():
            return True

        # Check for plural abbreviations (e.g., TLs, SSEs, PMs)
        if len(term) <= 5 and term.endswith("s") and term[:-1].isupper() and term[:-1].isalpha():
            # Check if the singular form is a known abbreviation
            singular = term[:-1]
            if self.designation_config.is_known_designation_abbreviation(singular):
                return True

        return False

    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve designation abbreviations using static mappings + tsvector fuzzy search."""
        logger.info(
            "Resolving designation abbreviations", agent_type="designation_resolver", terms=terms
        )

        resolved_terms = {}

        for term in terms:
            # Step 1: Try static mappings first (for exact abbreviations)
            static_result = self.designation_config.get_mapped_designations(term)
            if static_result:
                resolved_terms[term] = static_result
                logger.info(
                    "Designation resolved via static mapping",
                    agent_type="designation_resolver",
                    term=term,
                    count=len(static_result),
                    designations=static_result,
                )
                continue

            # Step 1.5: Try plural abbreviations (TLs → TL)
            if (
                len(term) <= 5
                and term.endswith("s")
                and term[:-1].isupper()
                and term[:-1].isalpha()
            ):
                singular = term[:-1]
                singular_result = self.designation_config.get_mapped_designations(singular)
                if singular_result:
                    resolved_terms[term] = singular_result
                    logger.info(
                        "Designation resolved via plural abbreviation",
                        agent_type="designation_resolver",
                        term=term,
                        singular=singular,
                        count=len(singular_result),
                        designations=singular_result,
                    )
                    continue

            # Step 2: Try tsvector fuzzy search on designations table
            fuzzy_result = await self._fuzzy_search_designations(term)
            if fuzzy_result:
                resolved_terms[term] = fuzzy_result
                logger.info(
                    "Designation resolved via fuzzy search",
                    agent_type="designation_resolver",
                    term=term,
                    count=len(fuzzy_result),
                    designations=fuzzy_result,
                )

        return resolved_terms

    async def _fuzzy_search_designations(self, term: str) -> List[str]:
        """Use tsvector and similarity to find matching designations in the database."""
        from app.core.database import get_async_session
        from sqlalchemy import text

        session_generator = get_async_session()
        session = await session_generator.__anext__()

        try:
            # Use both tsvector full-text search and pg_trgm similarity
            query = text(
                """
            SELECT DISTINCT d.title, 
                   GREATEST(
                       ts_rank(to_tsvector('english', d.title), plainto_tsquery('english', :term)),
                       similarity(d.title, :term)
                   ) as relevance_score
            FROM designations d
            WHERE (
                to_tsvector('english', d.title) @@ plainto_tsquery('english', :term)
                OR similarity(d.title, :term) > 0.3
            )
            ORDER BY relevance_score DESC
            LIMIT 5
            """
            )

            result = await session.execute(query, {"term": term})
            rows = result.fetchall()

            if rows:
                # Return titles with relevance score > 0.2 for quality filtering
                results = [row[0] for row in rows if row[1] > 0.2]
                return results[:3]  # Limit to top 3 matches

        except Exception as e:
            logger.warning(
                "Fuzzy designation search failed",
                agent_type="designation_resolver",
                term=term,
                error=str(e),
            )
        finally:
            await session.close()

        return []
