"""Context management service."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class ConversationContext(BaseModel):
    """Conversation context data."""

    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = {}
    history: list[dict[str, Any]] = []
    created_at: str = ""
    last_updated: str = ""

    def __init__(self, **data):
        """Initialize with timestamps."""
        if not data.get("created_at"):
            data["created_at"] = datetime.now().isoformat()
        if not data.get("last_updated"):
            data["last_updated"] = datetime.now().isoformat()
        super().__init__(**data)

    def update_timestamp(self):
        """Update the last_updated timestamp."""
        self.last_updated = datetime.now().isoformat()


class ContextService:
    """Service for managing conversation context."""

    def __init__(self):
        """Initialize the context service."""
        self._contexts: dict[str, ConversationContext] = {}
        self._conversations_dir = Path("conversations")
        self._ensure_conversations_directory()

    def get_context(self, session_id: str) -> ConversationContext | None:
        """Get context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Conversation context if exists
        """
        # First check in-memory cache
        if session_id in self._contexts:
            logger.info(f"Found context in memory", session_id=session_id)
            return self._contexts[session_id]
        
        # Try loading from file
        context = self._load_context_from_file(session_id)
        if context:
            # Cache in memory
            self._contexts[session_id] = context
            logger.info(f"Loaded conversation context from file", session_id=session_id)
        
        return context

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
            session_id=session_id, 
            user_id=user_id,
            metadata=metadata or {}
        )
        self._contexts[session_id] = context
        
        # Save to file immediately
        self._save_context_to_file(context)
        logger.info(f"Created new conversation context", session_id=session_id)
        
        return context

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
        # Get context (will load from file if not in memory)
        context = self.get_context(session_id)
        if context:
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.now().isoformat()
            
            context.history.append(message)
            context.update_timestamp()
            
            # Save updated context to file
            self._save_context_to_file(context)
            
            return context
        return None

    def _ensure_conversations_directory(self) -> None:
        """Create conversations directory if it doesn't exist."""
        try:
            self._conversations_dir.mkdir(exist_ok=True)
            logger.info(f"Conversations directory ready: {self._conversations_dir}")
        except Exception as e:
            logger.error(f"Failed to create conversations directory: {e}")

    def _get_conversation_file_path(self, session_id: str) -> Path:
        """Get file path for a session's conversation.

        Args:
            session_id: Session identifier

        Returns:
            Path to conversation file
        """
        return self._conversations_dir / f"{session_id}.json"

    def _load_context_from_file(self, session_id: str) -> ConversationContext | None:
        """Load conversation context from JSON file.

        Args:
            session_id: Session identifier

        Returns:
            Loaded context or None if file doesn't exist
        """
        file_path = self._get_conversation_file_path(session_id)
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ConversationContext(**data)
        except Exception as e:
            logger.error(f"Failed to load conversation from file: {e}", session_id=session_id, file_path=str(file_path))
        
        return None

    def _save_context_to_file(self, context: ConversationContext) -> bool:
        """Save conversation context to JSON file.

        Args:
            context: Context to save

        Returns:
            True if saved successfully, False otherwise
        """
        file_path = self._get_conversation_file_path(context.session_id)
        
        try:
            # Convert to dict for JSON serialization
            data = context.dict()
            
            # Write to file atomically (write to temp file, then rename)
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.rename(file_path)
            
            logger.debug(f"Saved conversation context to file", session_id=context.session_id, file_path=str(file_path))
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation to file: {e}", session_id=context.session_id, file_path=str(file_path))
            return False
