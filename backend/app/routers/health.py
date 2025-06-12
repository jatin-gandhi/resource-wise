"""Health check router"""

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "ok", "service": "Resource Wise API", "version": "0.1.0"}


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_async_session)):  # noqa: B008
    """Detailed health check including database connectivity"""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "ok" if result.scalar() == 1 else "error"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": "Resource Wise API",
        "version": "0.1.0",
        "checks": {
            "database": db_status,
        },
    }
