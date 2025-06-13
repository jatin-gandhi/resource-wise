"""AI system orchestrator."""

import json
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
from app.services.database import db_service

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
        logger.info(f"orchestrator ready {openai_status} (with workflow)")

    async def process_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a user query through the complete workflow."""
        try:
            # Generate session ID if not provided
            session_id = session_id or str(uuid4())
            user_id = user_id or "anonymous"

            logger.info(f"processing query: {len(query)}chars, session: {session_id}")

            # Initialize database service if not already done
            if not db_service._connection_pool:
                await db_service.initialize()

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

            # Prepare workflow context
            workflow_context = {
                "user_id": user_id,
                "history": context.history if context else [],
                **(metadata or {})
            }

            # Process through workflow
            result = await self.workflow.process(
                user_input=query,
                session_id=session_id,
                context=workflow_context
            )

            # Extract response content
            query_result = result.query_result or {}
            response_content = query_result.get("response", "I apologize, but I couldn't process your request.")

            # Add assistant response to history
            self.context_service.add_to_history(
                session_id=session_id, message={"role": "assistant", "content": response_content}
            )

            # Build comprehensive response
            return {
                "session_id": session_id,
                "result": {
                    "content": response_content,
                    "intent": query_result.get("intent", "unknown"),
                    "requires_database": query_result.get("requires_database", False),
                    "sql_query": query_result.get("sql_query"),
                    "tables_used": query_result.get("tables_used", []),
                    "metadata": {
                        "current_stage": result.current_stage,
                        "workflow_success": result.current_stage == "completed",
                        **query_result.get("metadata", {})
                    }
                },
                "error": result.error
            }

        except Exception as e:
            logger.error(f"query failed: {str(e)}", exc_info=True)
            return {
                "session_id": session_id or str(uuid4()),
                "result": {
                    "content": f"I encountered an error processing your request: {str(e)}",
                    "intent": "error",
                    "requires_database": False
                },
                "error": str(e)
            }

    async def stream_query(
        self,
        query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncGenerator[str]:
        """Process a query with streaming response through the workflow."""
        accumulated_content = ""

        try:
            # Generate session ID if not provided
            session_id = session_id or str(uuid4())
            user_id = user_id or "anonymous"

            logger.info(f"streaming query: {len(query)}chars, session: {session_id}")

            # Initialize database service if not already done
            if not db_service._connection_pool:
                await db_service.initialize()

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

            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'data': {'session_id': session_id}})}\n\n"

            # Prepare workflow context
            workflow_context = {
                "user_id": user_id,
                "history": context.history if context else [],
                **(metadata or {})
            }

            # Process through workflow (non-streaming for now)
            # TODO: Implement proper streaming when workflow supports it
            result = await self.workflow.process(
                user_input=query,
                session_id=session_id,
                context=workflow_context
            )

            # Extract response content
            query_result = result.query_result or {}
            response_content = query_result.get("response", "I apologize, but I couldn't process your request.")
            
            # Send workflow metadata
            yield f"data: {json.dumps({'type': 'metadata', 'data': {'intent': query_result.get('intent', 'unknown'), 'requires_database': query_result.get('requires_database', False), 'sql_query': query_result.get('sql_query'), 'tables_used': query_result.get('tables_used', [])}})}\n\n"

            # Stream the response content in chunks
            chunk_size = 20  # Smaller chunks for better streaming experience
            for i in range(0, len(response_content), chunk_size):
                chunk = response_content[i:i + chunk_size]
                accumulated_content += chunk
                yield f"data: {json.dumps({'type': 'token', 'data': {'token': chunk, 'content': accumulated_content}})}\n\n"
                
                # Small delay to simulate streaming
                import asyncio
                await asyncio.sleep(0.05)

            # Add final response to history
            if accumulated_content:
                self.context_service.add_to_history(
                    session_id=session_id, message={"role": "assistant", "content": accumulated_content}
                )

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
                "error": result.error
            }
            
            yield f"data: {json.dumps({'type': 'done', 'data': completion_data})}\n\n"
            yield "data: [DONE]\n\n"

            logger.info(f"streaming completed: {len(accumulated_content)}chars")

        except Exception as e:
            logger.error(f"stream failed: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': f'Error: {str(e)}'}})}\n\n"
