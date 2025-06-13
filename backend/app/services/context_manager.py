"""Context Manager for Conversation Memory and State"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

logger = structlog.get_logger()


class ContextManager:
    """Manages conversation context and memory for chat sessions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_history_length = 10  # Keep last 10 exchanges
        self.context_ttl_hours = 24   # Context expires after 24 hours
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve conversation context for a session"""
        try:
            # For now, use in-memory storage since we don't have the table yet
            # In production, this would query the conversation_contexts table
            return self._get_memory_context(session_id)
            
        except Exception as e:
            logger.error("Failed to get context", session_id=session_id, error=str(e))
            return {}
    
    async def update_context(self, session_id: str, new_context: Dict[str, Any]):
        """Update conversation context"""
        try:
            existing = await self.get_context(session_id)
            merged_context = {**existing, **new_context}
            merged_context["updated_at"] = datetime.utcnow().isoformat()
            
            # Store in memory for now
            self._set_memory_context(session_id, merged_context)
            
        except Exception as e:
            logger.error("Failed to update context", session_id=session_id, error=str(e))
    
    async def add_query_to_history(self, session_id: str, query: str, response: str, metadata: Dict[str, Any] = None):
        """Add query-response pair to conversation history"""
        try:
            context = await self.get_context(session_id)
            
            if "history" not in context:
                context["history"] = []
            
            history_entry = {
                "query": query,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            context["history"].append(history_entry)
            
            # Keep only last N exchanges
            context["history"] = context["history"][-self.max_history_length:]
            
            await self.update_context(session_id, context)
            
        except Exception as e:
            logger.error("Failed to add query to history", session_id=session_id, error=str(e))
    
    async def get_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        try:
            context = await self.get_context(session_id)
            history = context.get("history", [])
            return history[-limit:] if history else []
            
        except Exception as e:
            logger.error("Failed to get conversation history", session_id=session_id, error=str(e))
            return []
    
    async def set_user_preferences(self, session_id: str, preferences: Dict[str, Any]):
        """Set user preferences for the session"""
        try:
            await self.update_context(session_id, {"preferences": preferences})
            
        except Exception as e:
            logger.error("Failed to set user preferences", session_id=session_id, error=str(e))
    
    async def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences for the session"""
        try:
            context = await self.get_context(session_id)
            return context.get("preferences", {})
            
        except Exception as e:
            logger.error("Failed to get user preferences", session_id=session_id, error=str(e))
            return {}
    
    async def clear_context(self, session_id: str):
        """Clear all context for a session"""
        try:
            self._clear_memory_context(session_id)
            
        except Exception as e:
            logger.error("Failed to clear context", session_id=session_id, error=str(e))
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a summary of the current context for AI prompts"""
        try:
            summary_parts = []
            
            # Recent queries
            history = context.get("history", [])
            if history:
                recent_queries = [h["query"] for h in history[-3:]]
                summary_parts.append(f"Recent queries: {', '.join(recent_queries)}")
            
            # User preferences
            preferences = context.get("preferences", {})
            if preferences:
                pref_items = [f"{k}: {v}" for k, v in preferences.items()]
                summary_parts.append(f"User preferences: {', '.join(pref_items)}")
            
            # Current focus/topic
            if "current_topic" in context:
                summary_parts.append(f"Current topic: {context['current_topic']}")
            
            return " | ".join(summary_parts) if summary_parts else "No previous context"
            
        except Exception as e:
            logger.error("Failed to generate context summary", error=str(e))
            return "Context summary unavailable"
    
    # In-memory storage for development (replace with database in production)
    _memory_contexts: Dict[str, Dict[str, Any]] = {}
    
    def _get_memory_context(self, session_id: str) -> Dict[str, Any]:
        """Get context from memory storage"""
        context = self._memory_contexts.get(session_id, {})
        
        # Check if context has expired
        if context and "updated_at" in context:
            try:
                updated_at = datetime.fromisoformat(context["updated_at"])
                if datetime.utcnow() - updated_at > timedelta(hours=self.context_ttl_hours):
                    # Context expired, clear it
                    self._clear_memory_context(session_id)
                    return {}
            except (ValueError, TypeError):
                pass
        
        return context
    
    def _set_memory_context(self, session_id: str, context: Dict[str, Any]):
        """Set context in memory storage"""
        self._memory_contexts[session_id] = context
    
    def _clear_memory_context(self, session_id: str):
        """Clear context from memory storage"""
        if session_id in self._memory_contexts:
            del self._memory_contexts[session_id]
    
    async def extract_entities_from_query(self, query: str) -> Dict[str, List[str]]:
        """Extract entities (employees, projects, skills) mentioned in the query"""
        try:
            entities = {
                "employees": [],
                "projects": [],
                "skills": [],
                "designations": []
            }
            
            # Simple keyword extraction (in production, use NER or more sophisticated methods)
            query_lower = query.lower()
            
            # Extract common employee names (this would be enhanced with actual employee data)
            common_names = ["john", "jane", "alice", "bob", "carol", "david", "eva", "frank"]
            for name in common_names:
                if name in query_lower:
                    entities["employees"].append(name.title())
            
            # Extract project-related keywords
            project_keywords = ["project", "app", "system", "platform", "website", "mobile", "web"]
            for keyword in project_keywords:
                if keyword in query_lower:
                    entities["projects"].append(keyword)
            
            # Extract skill keywords
            skill_keywords = ["react", "python", "java", "javascript", "node", "angular", "vue", 
                            "docker", "aws", "kubernetes", "machine learning", "ai", "ml"]
            for skill in skill_keywords:
                if skill in query_lower:
                    entities["skills"].append(skill)
            
            # Extract designation keywords
            designation_keywords = ["developer", "engineer", "lead", "manager", "architect", 
                                  "senior", "junior", "tl", "sse", "sde"]
            for designation in designation_keywords:
                if designation in query_lower:
                    entities["designations"].append(designation)
            
            return entities
            
        except Exception as e:
            logger.error("Failed to extract entities", error=str(e))
            return {"employees": [], "projects": [], "skills": [], "designations": []} 