"""Workflow state management."""

from typing import Any

from pydantic import BaseModel


class AgentState(BaseModel):
    """State for agent workflow."""

    # Input state
    user_input: str
    session_id: str

    # Processing state
    current_stage: str = "start"
    error: str | None = None

    # Agent outputs
    query_result: dict[str, Any] | None = None

    # Context
    context: dict[str, Any] = {}
    history: list[dict[str, Any]] = []

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
