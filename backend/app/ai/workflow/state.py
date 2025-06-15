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

    # Resource matching workflow fields
    workflow_intent: str | None
    project_details: dict[str, Any] | None
    missing_project_info: list[str]
    available_employees: list[dict[str, Any]]
    team_combinations: list[dict[str, Any]]


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

    # Resource matching workflow fields
    workflow_intent: str | None = None
    project_details: dict[str, Any] | None = None
    missing_project_info: list[str] = []
    available_employees: list[dict[str, Any]] = []
    team_combinations: list[dict[str, Any]] = []

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
            workflow_intent=self.workflow_intent,
            project_details=self.project_details,
            missing_project_info=self.missing_project_info,
            available_employees=self.available_employees,
            team_combinations=self.team_combinations,
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
            workflow_intent=data.get("workflow_intent"),
            project_details=data.get("project_details"),
            missing_project_info=data.get("missing_project_info", []),
            available_employees=data.get("available_employees", []),
            team_combinations=data.get("team_combinations", []),
        )
