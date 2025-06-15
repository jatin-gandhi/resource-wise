"""AI router implementation."""

import time
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.ai.orchestrator import AIOrchestrator
from app.schemas.ai import QueryRequest, QueryResponse

router = APIRouter(prefix="/ai", tags=["ai"])
logger = structlog.get_logger()

# Global singleton orchestrator instance (managed by lifespan)
orchestrator_instance: AIOrchestrator | None = None


def get_orchestrator() -> AIOrchestrator:
    """Get singleton AI orchestrator instance."""
    if orchestrator_instance is None:
        raise HTTPException(
            status_code=503, 
            detail="AI service not initialized. Please wait for startup to complete."
        )
    return orchestrator_instance


async def initialize_orchestrator() -> None:
    """Initialize the singleton AI orchestrator instance."""
    global orchestrator_instance
    
    if orchestrator_instance is not None:
        logger.warning("AIOrchestrator already initialized")
        return
    
    try:
        logger.info("Initializing AIOrchestrator singleton...")
        orchestrator_instance = AIOrchestrator()
        logger.info("AIOrchestrator singleton ready ✓")
    except Exception as e:
        logger.error(f"Failed to initialize AIOrchestrator: {e}")
        raise


async def shutdown_orchestrator() -> None:
    """Shutdown the singleton AI orchestrator instance."""
    global orchestrator_instance
    
    if orchestrator_instance is not None:
        logger.info("Shutting down AIOrchestrator singleton...")
        orchestrator_instance = None
        logger.info("AIOrchestrator singleton shutdown complete")


@router.get("/health")
async def health_check(request: Request, orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """Check AI service health and OpenAI configuration."""
    start_time = time.time()

    logger.info("@/health")

    try:
        openai_configured = orchestrator.llm_service.client is not None
        status = "healthy" if openai_configured else "degraded"
        message = "AI service is running" if openai_configured else "OpenAI API key not configured"

        response = {"status": status, "openai_configured": openai_configured, "message": message}

        processing_time = round((time.time() - start_time) * 1000, 1)
        logger.info(f"@/health ✓ {processing_time}ms")

        return response

    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 1)
        logger.error(f"@/health ✗ {processing_time}ms - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") from e


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    http_request: Request,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    """Process a query using AI orchestrator."""
    start_time = time.time()

    logger.info(f"@/query [{request.session_id or 'new'}] {len(request.query)}chars")

    try:
        result = await orchestrator.process_query(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
        )

        processing_time = round((time.time() - start_time) * 1000, 1)
        response_len = len(str(result.get("result", {}).get("content", "")))
        has_error = "✗" if result.get("error") else "✓"

        logger.info(f"@/query {has_error} {processing_time}ms → {response_len}chars")

        return result

    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 1)
        logger.error(f"@/query ✗ {processing_time}ms - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/stream")
async def stream_query(
    request: QueryRequest,
    http_request: Request,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> StreamingResponse:
    """Stream query processing using AI orchestrator."""
    start_time = time.time()

    logger.info(f"[STREAM] [{request.session_id or 'new'}] {len(request.query)}chars")

    try:
        # Create a wrapper generator to log streaming completion
        async def logged_stream_generator():
            token_count = 0
            try:
                async for chunk in orchestrator.stream_query(
                    query=request.query,
                    session_id=request.session_id,
                    user_id=request.user_id,
                ):
                    token_count += 1
                    yield chunk

                processing_time = round((time.time() - start_time) * 1000, 1)
                logger.info(f"[STREAM] Completed in {processing_time}ms → {token_count} tokens")

            except Exception as e:
                processing_time = round((time.time() - start_time) * 1000, 1)
                logger.error(f"[STREAM] Failed in {processing_time}ms - {str(e)}")
                raise

        return StreamingResponse(
            logged_stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 1)
        logger.error(f"[STREAM] Failed in {processing_time}ms - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
