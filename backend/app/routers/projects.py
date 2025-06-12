"""Projects router"""

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.get("/projects")
async def get_projects():
    """Get projects - to be implemented"""
    return {"message": "Projects endpoint - coming soon"}
