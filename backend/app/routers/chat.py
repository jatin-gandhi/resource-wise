"""Chat router for AI interactions"""

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.post("/chat")
async def chat():
    """AI chat endpoint - to be implemented"""
    return {"message": "Chat endpoint - coming soon"}
