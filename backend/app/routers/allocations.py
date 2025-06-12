"""Allocations router"""

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.get("/allocations")
async def get_allocations():
    """Get allocations - to be implemented"""
    return {"message": "Allocations endpoint - coming soon"}
