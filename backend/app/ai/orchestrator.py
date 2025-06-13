"""AI system orchestrator."""

import time
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import structlog

from app.ai.core.config import AIConfig
from app.ai.core.llm import LLMService
from app.ai.services.context import ContextService
from app.ai.services.stream import StreamService
from app.ai.workflow.graph import AgentWorkflow

logger = structlog.get_logger()


class AIOrchestrator:
    """Orchestrates the AI system components."""

    def __init__(self, config: AIConfig | None = None):
        """Initialize the orchestrator.

        Args:
            config: AI configuration settings. If None, will use default config with settings.
        """
        if config is None:
            config = AIConfig()

        self.config = config
        self.llm_service = LLMService(config)
        self.workflow = AgentWorkflow(config)
        self.context_service = ContextService()
        self.stream_service = StreamService()

        openai_status = "✓" if self.llm_service.client else "✗"
        logger.info(f"orchestrator ready {openai_status}")

    async def process_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a user query."""
        try:
            # Generate session ID if not provided
            session_id = session_id or str(uuid4())

            # Context management
            context = self.context_service.get_context(session_id)
            if not context:
                context = self.context_service.create_context(
                    session_id=session_id, user_id=user_id, metadata=metadata
                )

            # Add user message to history
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "user", "content": query}
            )

            # Get LLM response
            response_content = await self.llm_service.get_completion(user_message=query)

            # Add assistant response to history
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "assistant", "content": response_content}
            )

            return {"session_id": session_id, "result": {"content": response_content}, "error": None}

        except Exception as e:
            logger.error(f"query failed: {str(e)}")
            return {"session_id": session_id, "result": {}, "error": str(e)}

    async def stream_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncGenerator[str]:
        """Process a query with streaming response."""
        accumulated_content = ""

        try:
            # Generate session ID if not provided
            session_id = session_id or str(uuid4())

            # Context management
            context = self.context_service.get_context(session_id)
            if not context:
                context = self.context_service.create_context(
                    session_id=session_id, user_id=user_id, metadata=metadata
                )

            # Add user message to history
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "user", "content": query}
            )

            # Stream response from LLM service
            async for chunk in self.llm_service.stream_completion(
                user_message=query, session_id=session_id
            ):
                # Try to extract content from chunk for logging
                try:
                    import json
                    chunk_data = json.loads(chunk.replace("data: ", "").strip())
                    if chunk_data.get("type") == "token" and "data" in chunk_data:
                        token = chunk_data["data"].get("token", "")
                        accumulated_content += token
                except:
                    pass  # Ignore parsing errors for logging

                yield chunk

            # Add final response to history
            if accumulated_content:
                self.context_service.add_to_history(
                    session_id=session_id, message={"role": "assistant", "content": accumulated_content}
            )

        except Exception as e:
            logger.error(f"stream failed: {str(e)}")
            import json
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': f'Error: {str(e)}'}})}\n\n"
