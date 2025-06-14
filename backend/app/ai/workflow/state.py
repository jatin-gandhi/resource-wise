"""Workflow state management."""

from typing import Any, TypedDict

from pydantic import BaseModel


class AgentStateDict(TypedDict):
    """TypedDict for LangGraph state management."""

    # Input state
    user_input: str
    session_id: str

    # Processing state
    current_stage: str
    error: str | None

    query_details: dict[str, Any] | None
    database_result: dict[str, Any] | None

    # Agent outputs
    query_result: dict[str, Any] | None

    # Context
    context: dict[str, Any]
    history: list[dict[str, Any]]


class AgentState(BaseModel):
    """Pydantic model for agent workflow state."""

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

    def to_dict(self) -> AgentStateDict:
        """Convert to TypedDict for LangGraph."""
        return AgentStateDict(
            user_input=self.user_input,
            session_id=self.session_id,
            current_stage=self.current_stage,
            error=self.error,
            query_result=self.query_result,
            context=self.context,
            history=self.history,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentState":
        """Create from dictionary."""
        return cls(
            user_input=data.get("user_input", ""),
            session_id=data.get("session_id", ""),
            current_stage=data.get("current_stage", "start"),
            error=data.get("error"),
            query_result=data.get("query_result"),
            context=data.get("context", {}),
            history=data.get("history", []),
        )
