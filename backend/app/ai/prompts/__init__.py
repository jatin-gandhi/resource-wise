"""AI Prompts package.

This package contains all prompt templates used by AI agents.
These files are excluded from linting to allow for natural language formatting.
"""

from app.ai.prompts.fuzzy_classifier_prompts import FuzzyClassifierPrompts
from app.ai.prompts.query_prompts import QueryPrompts
from app.ai.prompts.response_prompts import ResponsePrompts

__all__ = ["FuzzyClassifierPrompts", "QueryPrompts", "ResponsePrompts"]
