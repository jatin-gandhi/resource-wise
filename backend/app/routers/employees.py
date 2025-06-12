"""Employees router"""

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.get("/employees")
async def get_employees():
    """Get employees - to be implemented"""
    return {"message": "Employees endpoint - coming soon"}
