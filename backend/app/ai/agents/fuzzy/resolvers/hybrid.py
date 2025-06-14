"""Hybrid fuzzy resolver with tiered resolution strategy."""

from typing import Dict, List

import structlog
from app.ai.agents.fuzzy.config.categories import SkillCategoryConfig
from app.ai.agents.fuzzy.resolvers.category import VectorResolver
from app.ai.agents.fuzzy.resolvers.designation import DesignationResolver
from app.ai.agents.fuzzy.resolvers.skill import SkillResolver
from app.ai.core.config import AIConfig

logger = structlog.get_logger(__name__)


class HybridFuzzyResolver:
    """Hybrid fuzzy resolver using tiered resolution strategy with tsvector fuzzy matching."""

    def __init__(self, config: AIConfig):
        self.config = config
        self.designation_resolver = DesignationResolver(config)
        self.skill_resolver = SkillResolver(config)
        self.vector_resolver = VectorResolver(config)

    async def resolve_fuzzy_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Resolve fuzzy terms using parallel + fallback approach.

        Parallel: Designation fuzzy matching (SSE, TLs) + Skill fuzzy matching (reactjs, backend)
        Fallback: Vector similarity for truly unknown terms

        Args:
            terms: List of terms to resolve

        Returns:
            Dictionary mapping terms to resolved values
        """
        logger.info("Starting hybrid fuzzy resolution", agent_type="hybrid_resolver", terms=terms)

        resolved_terms = {}
        unresolved_terms = []

        # Separate terms by type for parallel processing
        designation_terms = []
        skill_terms = []
        unknown_terms = []

        for term in terms:
            if self.designation_resolver.can_handle(term):
                designation_terms.append(term)
            elif self.skill_resolver.can_handle(term):
                skill_terms.append(term)
            else:
                unknown_terms.append(term)

        # Process designation and skill terms in parallel
        if designation_terms:
            designation_results = await self.designation_resolver.resolve_terms(designation_terms)
            resolved_terms.update(designation_results)

        if skill_terms:
            skill_results = await self.skill_resolver.resolve_terms(skill_terms)
            resolved_terms.update(skill_results)

        # Unknown terms go to vector fallback
        unresolved_terms = unknown_terms

        # Use vector similarity for unresolved terms
        if unresolved_terms and SkillCategoryConfig.get_setting("enable_vector_fallback", True):
            logger.info(
                "Using vector fallback for unresolved terms",
                agent_type="hybrid_resolver",
                unresolved_terms=unresolved_terms,
            )

            vector_results = await self.vector_resolver.resolve_terms(unresolved_terms)
            resolved_terms.update(vector_results)

        logger.info(
            "Hybrid fuzzy resolution completed",
            agent_type="hybrid_resolver",
            total_terms=len(terms),
            resolved_count=len(resolved_terms),
            resolved_terms=list(resolved_terms.keys()),
        )

        return resolved_terms

    def get_resolution_stats(self, terms: List[str], resolved_terms: Dict[str, List[str]]) -> Dict:
        """Get statistics about the resolution process."""
        designation_resolved = []
        skill_resolved = []
        vector_resolved = []
        unresolved = []

        for term in terms:
            if term in resolved_terms:
                if self.designation_resolver.can_handle(term):
                    designation_resolved.append(term)
                elif self.skill_resolver.can_handle(term):
                    skill_resolved.append(term)
                else:
                    vector_resolved.append(term)
            else:
                unresolved.append(term)

        return {
            "total_terms": len(terms),
            "designation_resolved": len(designation_resolved),
            "skill_resolved": len(skill_resolved),
            "vector_resolved": len(vector_resolved),
            "unresolved": len(unresolved),
            "resolution_rate": len(resolved_terms) / len(terms) if terms else 0,
            "designation_terms": designation_resolved,
            "skill_terms": skill_resolved,
            "vector_terms": vector_resolved,
            "unresolved_terms": unresolved,
        }
