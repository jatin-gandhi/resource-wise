"""AI-related schemas."""

from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Schema for user queries."""

    query: str
    session_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] | None = None


class QueryResponse(BaseModel):
    """Schema for query responses."""

    session_id: str
    result: dict[str, Any]
    error: str | None = None


class StreamEvent(BaseModel):
    """Schema for streaming events."""

    type: str
    data: dict[str, Any]
    session_id: str


class ContextData(BaseModel):
    """Schema for context data."""

    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] | None = None
    history: list | None = None
