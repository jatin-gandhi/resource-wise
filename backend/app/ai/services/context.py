"""Context management service."""

from typing import Any

from pydantic import BaseModel


class ConversationContext(BaseModel):
    """Conversation context data."""

    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = {}
    history: list[dict[str, Any]] = []


class ContextService:
    """Service for managing conversation context."""

    def __init__(self):
        """Initialize the context service."""
        self._contexts: dict[str, ConversationContext] = {}

    def get_context(self, session_id: str) -> ConversationContext | None:
        """Get context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Conversation context if exists
        """
        return self._contexts.get(session_id)

    def create_context(
        self,
        session_id: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationContext:
        """Create new conversation context.

        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            metadata: Optional metadata

        Returns:
            Created conversation context
        """
        context = ConversationContext(
            session_id=session_id, user_id=user_id, metadata=metadata or {}
        )
        self._contexts[session_id] = context
        return context

    def update_context(
        self, session_id: str, metadata: dict[str, Any]
    ) -> ConversationContext | None:
        """Update context metadata.

        Args:
            session_id: Session identifier
            metadata: New metadata

        Returns:
            Updated context if exists
        """
        if context := self._contexts.get(session_id):
            context.metadata.update(metadata)
            return context
        return None

    def add_to_history(
        self, session_id: str, message: dict[str, Any]
    ) -> ConversationContext | None:
        """Add message to conversation history.

        Args:
            session_id: Session identifier
            message: Message to add

        Returns:
            Updated context if exists
        """
        if context := self._contexts.get(session_id):
            context.history.append(message)
            return context
        return None
