"""Streaming service implementation."""

from collections.abc import AsyncGenerator
from typing import Any

from pydantic import BaseModel


class StreamEvent(BaseModel):
    """Stream event data."""

    type: str
    data: dict[str, Any]
    session_id: str


class StreamService:
    """Service for handling streaming responses."""

    def __init__(self):
        """Initialize the stream service."""
        self._streams: dict[str, AsyncGenerator[StreamEvent]] = {}

    async def create_stream(self, session_id: str, generator: AsyncGenerator[StreamEvent]) -> None:
        """Create a new stream for a session.

        Args:
            session_id: Session identifier
            generator: Event generator
        """
        self._streams[session_id] = generator

    async def get_stream(self, session_id: str) -> AsyncGenerator[StreamEvent]:
        """Get stream for a session.

        Args:
            session_id: Session identifier

        Returns:
            Event generator
        """
        if stream := self._streams.get(session_id):
            return stream
        raise ValueError(f"No stream found for session {session_id}")

    async def close_stream(self, session_id: str) -> None:
        """Close stream for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._streams:
            del self._streams[session_id]

    async def send_event(self, session_id: str, event_type: str, data: dict[str, Any]) -> None:
        """Send event to a stream.

        Args:
            session_id: Session identifier
            event_type: Event type
            data: Event data
        """
        if stream := self._streams.get(session_id):
            event = StreamEvent(type=event_type, data=data, session_id=session_id)
            await stream.asend(event)
