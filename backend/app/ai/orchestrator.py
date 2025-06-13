"""AI system orchestrator."""

from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import structlog

from app.ai.core.config import AIConfig
from app.ai.services.context import ContextService
from app.ai.services.stream import StreamService
from app.ai.workflow.graph import AgentWorkflow

logger = structlog.get_logger()


class AIOrchestrator:
    """Orchestrates the AI system components."""

    def __init__(self, config: AIConfig):
        """Initialize the orchestrator.

        Args:
            config: AI configuration settings
        """
        self.config = config
        self.workflow = AgentWorkflow(config)
        self.context_service = ContextService()
        self.stream_service = StreamService()

        logger.info(
            "AI Orchestrator initialized",
            config=config.dict(),
            components={"workflow": self.workflow.__class__.__name__},
        )

    async def process_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a user query.

        Args:
            query: User query
            session_id: Optional session identifier
            user_id: Optional user identifier
            metadata: Optional metadata

        Returns:
            Processing results
        """
        try:
            logger.info(
                "Processing query",
                query=query,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
            )

            # Generate session ID if not provided
            session_id = session_id or str(uuid4())

            # Get or create context
            context = self.context_service.get_context(session_id)
            if not context:
                context = self.context_service.create_context(
                    session_id=session_id, user_id=user_id, metadata=metadata
                )
            logger.debug("Retrieved context", context=context)

            # Process through workflow
            state = await self.workflow.process(
                user_input=query, session_id=session_id, context=context.dict()
            )
            logger.debug("Workflow result", result=state.query_result)

            # Update context
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "user", "content": query}
            )

            return {"session_id": session_id, "result": state.query_result, "error": state.error}

        except Exception as e:
            logger.error(
                "Error processing query",
                error=str(e),
                error_type=type(e).__name__,
                query=query,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
                exc_info=True,
            )
            return {"session_id": session_id, "result": {}, "error": str(e)}

    async def stream_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncGenerator[str]:
        """Process a query with streaming response.

        Args:
            query: User query
            session_id: Optional session identifier
            user_id: Optional user identifier
            metadata: Optional metadata

        Yields:
            Streaming response chunks
        """
        try:
            logger.info(
                "Streaming query",
                query=query,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
            )

            # Generate session ID if not provided
            session_id = session_id or str(uuid4())

            # Get or create context
            context = self.context_service.get_context(session_id)
            if not context:
                context = self.context_service.create_context(
                    session_id=session_id, user_id=user_id, metadata=metadata
                )
            logger.debug("Retrieved context", context=context)

            # Process through workflow with streaming
            async for chunk in self.workflow.stream_process(
                user_input=query, session_id=session_id, context=context.dict()
            ):
                yield chunk

            # Update context
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "user", "content": query}
            )

        except Exception as e:
            logger.error(
                "Error streaming query",
                error=str(e),
                error_type=type(e).__name__,
                query=query,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
                exc_info=True,
            )
            yield f"Error: {str(e)}"
