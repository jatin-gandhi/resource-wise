"""AI system orchestrator."""

import json
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import structlog

from app.ai.core.config import AIConfig
from app.ai.core.llm import LLMService
from app.ai.services.context import ContextService
from app.ai.services.stream import StreamService
from app.ai.workflow.graph import AgentWorkflow
from app.services.database import db_service
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

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
        self.chat_history: list[BaseMessage] = []

        openai_status = "✓" if self.llm_service.client else "✗"
        # logger.info(f"orchestrator ready {openai_status} (with workflow)")

    async def stream_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> AsyncGenerator[str]:
        """Process a query with streaming response through the workflow."""
        accumulated_content = ""

        try:
            # Generate session ID if not provided
            session_id = session_id or str(uuid4())
            user_id = user_id or "anonymous"

            # logger.info(f"streaming query: {len(query)}chars, session: {session_id}")

            # Initialize database service if not already done
            if not db_service._connection_pool:
                await db_service.initialize()

            # Context management
            context = self.context_service.get_context(session_id)
            if not context:
                context = self.context_service.create_context(
                    session_id=session_id, user_id=user_id
                )


            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'data': {'session_id': session_id}})}\n\n"

            # Prepare workflow context
            workflow_context = {
                "user_id": user_id,
                'chat_history': self.chat_history
            }

            result = await self.workflow.process(
                user_input=query, session_id=session_id, context=workflow_context
            )

            # Extract response content
            query_result = result.query_result or {}
            response_content = query_result.get(
                "response", "I apologize, but I couldn't process your request."
            )

            self.chat_history.extend([
                HumanMessage(content=query),
                AIMessage(content=response_content)
            ])

            # Send workflow metadata
            yield f"data: {json.dumps({'type': 'metadata', 'data': {'intent': query_result.get('intent', 'unknown'), 'requires_database': query_result.get('requires_database', False), 'sql_query': query_result.get('sql_query'), 'tables_used': query_result.get('tables_used', [])}})}\n\n"

            # Stream the response content in chunks
            chunk_size = 20  # Smaller chunks for better streaming experience
            for i in range(0, len(response_content), chunk_size):
                chunk = response_content[i : i + chunk_size]
                accumulated_content += chunk
                yield f"data: {json.dumps({'type': 'token', 'data': {'token': chunk, 'content': accumulated_content}})}\n\n"

                # Small delay to simulate streaming
                import asyncio

                await asyncio.sleep(0.05)

            # Send completion event with full metadata
            completion_data = {
                "content": accumulated_content,
                "session_id": session_id,
                "intent": query_result.get("intent", "unknown"),
                "requires_database": query_result.get("requires_database", False),
                "sql_query": query_result.get("sql_query"),
                "tables_used": query_result.get("tables_used", []),
                "current_stage": result.current_stage,
                "success": result.current_stage == "completed",
                "error": result.error,
            }

            yield f"data: {json.dumps({'type': 'done', 'data': completion_data})}\n\n"
            yield "data: [DONE]\n\n"

            # logger.info(f"streaming completed: {len(accumulated_content)}chars")

        except Exception as e:
            logger.error(f"stream failed: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': f'Error: {str(e)}'}})}\n\n"
