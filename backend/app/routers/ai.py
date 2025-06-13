"""AI router implementation."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.ai.core.config import AIConfig
from app.ai.orchestrator import AIOrchestrator
from app.schemas.ai import QueryRequest, QueryResponse

router = APIRouter(prefix="/ai", tags=["ai"])


def get_orchestrator() -> AIOrchestrator:
    """Get AI orchestrator instance."""
    return AIOrchestrator(config=AIConfig())


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    """Process a query.

    Args:
        request: Query request
        orchestrator: AI orchestrator instance

    Returns:
        Query response
    """
    try:
        return await orchestrator.process_query(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            metadata=request.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/stream")
async def stream_query(
    request: QueryRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> StreamingResponse:
    """Stream query processing.

    Args:
        request: Query request
        orchestrator: AI orchestrator instance

    Returns:
        Streaming response
    """
    try:
        return StreamingResponse(
            orchestrator.stream_query(
                query=request.query,
                session_id=request.session_id,
                user_id=request.user_id,
                metadata=request.metadata,
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
