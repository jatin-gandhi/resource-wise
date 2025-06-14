"""Base resolver interface for fuzzy term resolution."""

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple

import structlog
from app.ai.core.config import AIConfig
from app.core.database import get_async_session
from sqlalchemy import text

logger = structlog.get_logger(__name__)


class BaseResolver(ABC):
    """Abstract base class for fuzzy term resolvers."""

    def __init__(self, config: AIConfig):
        self.config = config

    @abstractmethod
    async def resolve_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve fuzzy terms to database values.

        Args:
            terms: List of terms to resolve

        Returns:
            Dictionary mapping terms to resolved values
        """
        pass

    @abstractmethod
    def can_handle(self, term: str) -> bool:
        """Check if this resolver can handle the given term.

        Args:
            term: Term to check

        Returns:
            True if this resolver can handle the term
        """
        pass


class DatabaseMixin:
    """Mixin providing common database operations for resolvers."""

    async def get_available_data(self) -> Tuple[Set[str], Set[str]]:
        """Get all available skills and roles from database.

        Returns:
            Tuple of (available_skills, available_roles)
        """
        session_generator = get_async_session()
        session = await session_generator.__anext__()

        try:
            # Get all skills
            skills_result = await session.execute(
                text("SELECT DISTINCT skill_name FROM employee_skills")
            )
            available_skills = {row[0] for row in skills_result.fetchall()}

            # Get all roles/designations
            roles_result = await session.execute(text("SELECT DISTINCT title FROM designations"))
            available_roles = {row[0] for row in roles_result.fetchall()}

            return available_skills, available_roles

        finally:
            await session.close()

    def filter_available_items(self, items: List[str], available: Set[str]) -> List[str]:
        """Filter items to only include those available in database.

        Args:
            items: Items to filter
            available: Set of available items

        Returns:
            Filtered list of items
        """
        return [item for item in items if item in available]


class VectorSearchMixin:
    """Mixin providing vector similarity search capabilities."""

    async def vector_similarity_search(
        self, term: str, limit: int = 5, threshold: float = 0.2
    ) -> List[str]:
        """Perform vector similarity search for a term.

        Args:
            term: Search term
            limit: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            List of similar items
        """
        session_generator = get_async_session()
        session = await session_generator.__anext__()

        try:
            # Generate embedding for the search term
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.config.api_key)

            embedding_response = await client.embeddings.create(
                model="text-embedding-3-small", input=term
            )
            search_embedding = embedding_response.data[0].embedding
            embedding_str = str(search_embedding)

            results = []

            # Search skills - get unique skills with best similarity score
            skills_query = text(
                """
                SELECT skill_name, MAX(1 - (embedding <=> :embedding)) as similarity
                FROM employee_skills 
                WHERE embedding IS NOT NULL
                GROUP BY skill_name
                ORDER BY similarity DESC
                LIMIT :limit
            """
            )

            skills_result = await session.execute(
                skills_query, {"embedding": embedding_str, "limit": limit}
            )
            results.extend([row[0] for row in skills_result.fetchall() if row[1] > threshold])

            # Search roles - get unique roles with best similarity score
            roles_query = text(
                """
                SELECT title, MAX(1 - (embedding <=> :embedding)) as similarity
                FROM designations 
                WHERE embedding IS NOT NULL
                GROUP BY title
                ORDER BY similarity DESC
                LIMIT :limit
            """
            )

            roles_result = await session.execute(
                roles_query, {"embedding": embedding_str, "limit": limit}
            )
            results.extend([row[0] for row in roles_result.fetchall() if row[1] > threshold])

            return results

        except Exception as e:
            logger.warning(
                "Vector similarity search failed",
                agent_type="vector_search",
                term=term,
                error=str(e),
            )
            return []
        finally:
            await session.close()
