"""Chat API Routes for AI-powered Resource Allocation"""

from typing import Dict, Any, List
import uuid
import json
import structlog
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.chat_orchestrator import ChatOrchestrator

logger = structlog.get_logger()

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str
    type: str
    session_id: str
    metadata: Dict[str, Any] = {}
    data: Any = None


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("WebSocket connected", session_id=session_id)
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("WebSocket disconnected", session_id=session_id)
    
    async def send_message(self, session_id: str, message: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(message)
    
    async def send_json(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(data)


manager = ConnectionManager()


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message and get AI response"""
    
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Initialize chat orchestrator
        orchestrator = ChatOrchestrator(db)
        
        # Process the message
        response = await orchestrator.process_chat_message(
            chat_message.message, 
            session_id
        )
        
        # Handle streaming responses
        if response.get("type") == "streaming":
            # For HTTP requests, we'll collect the streaming response
            content_parts = []
            async for chunk in response["generator"]:
                content_parts.append(chunk)
            
            return ChatResponse(
                content="".join(content_parts),
                type="streaming_complete",
                session_id=session_id,
                metadata={"streaming": True}
            )
        
        return ChatResponse(
            content=response["content"],
            type=response["type"],
            session_id=session_id,
            metadata=response.get("metadata", {}),
            data=response.get("data")
        )
        
    except Exception as e:
        logger.error("Chat message processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message/stream")
async def stream_chat_message(
    message: str,
    session_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Stream chat response for long-running queries"""
    
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize chat orchestrator
        orchestrator = ChatOrchestrator(db)
        
        # Process the message
        response = await orchestrator.process_chat_message(message, session_id)
        
        async def generate_stream():
            if response.get("type") == "streaming":
                # Stream the response
                async for chunk in response["generator"]:
                    yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
            else:
                # Send complete response
                yield f"data: {json.dumps(response)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error("Streaming chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    
    await manager.connect(websocket, session_id)
    orchestrator = ChatOrchestrator(db)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat_message":
                message = message_data.get("message", "")
                
                # Process the message
                response = await orchestrator.process_chat_message(message, session_id)
                
                if response.get("type") == "streaming":
                    # Send streaming response
                    await manager.send_json(session_id, {
                        "type": "streaming_start",
                        "message": "Processing your request..."
                    })
                    
                    async for chunk in response["generator"]:
                        await manager.send_json(session_id, {
                            "type": "streaming_chunk",
                            "content": chunk
                        })
                    
                    await manager.send_json(session_id, {
                        "type": "streaming_complete",
                        "session_id": session_id
                    })
                else:
                    # Send complete response
                    await manager.send_json(session_id, {
                        "type": "chat_response",
                        "content": response["content"],
                        "response_type": response["type"],
                        "metadata": response.get("metadata", {}),
                        "data": response.get("data")
                    })
            
            elif message_data.get("type") == "ping":
                # Respond to ping
                await manager.send_json(session_id, {"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), session_id=session_id)
        await manager.send_json(session_id, {
            "type": "error",
            "message": f"An error occurred: {str(e)}"
        })
        manager.disconnect(session_id)


@router.get("/sessions/{session_id}/history")
async def get_chat_history(
    session_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    
    try:
        orchestrator = ChatOrchestrator(db)
        history = await orchestrator.context_manager.get_conversation_history(
            session_id, limit
        )
        
        return {
            "session_id": session_id,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error("Failed to get chat history", error=str(e), session_id=session_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def clear_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Clear chat session and context"""
    
    try:
        orchestrator = ChatOrchestrator(db)
        await orchestrator.context_manager.clear_context(session_id)
        
        # Disconnect WebSocket if active
        manager.disconnect(session_id)
        
        return {
            "message": "Session cleared successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error("Failed to clear session", error=str(e), session_id=session_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections)
    }
