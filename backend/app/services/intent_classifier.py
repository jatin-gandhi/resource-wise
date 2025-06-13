"""Intent Classification Service for Resource Allocation Queries"""

from enum import Enum
from typing import Dict, List, Optional
import structlog
from langchain.schema import BaseMessage
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..core.config import settings

logger = structlog.get_logger()


class IntentType(Enum):
    """Types of user intents for resource allocation queries"""
    SIMPLE_QUERY = "simple_query"
    COMPLEX_QUERY = "complex_query"
    ALLOCATION_MODIFICATION = "allocation_modification"
    PROJECT_CREATION = "project_creation"
    EMPLOYEE_SEARCH = "employee_search"
    AVAILABILITY_CHECK = "availability_check"
    SKILL_MATCHING = "skill_matching"
    TEAM_RECOMMENDATION = "team_recommendation"


class IntentClassifier:
    """Classifies user intents for resource allocation queries"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at classifying user intents for a resource allocation system.
            
            Classify the user's query into one of these categories:
            
            - SIMPLE_QUERY: Direct questions about existing data (who, what, when, where)
              Examples: "Who is working on Project X?", "What projects is John assigned to?"
            
            - COMPLEX_QUERY: Requires analysis, recommendations, or complex joins
              Examples: "Show me utilization trends", "Which teams are overallocated?"
            
            - ALLOCATION_MODIFICATION: Changing existing allocations
              Examples: "Replace Alice with Bob on Project Y", "Change John's allocation to 50%"
            
            - PROJECT_CREATION: Creating new projects or teams
              Examples: "I need a team for mobile app development", "Create a new project"
            
            - EMPLOYEE_SEARCH: Finding employees by criteria
              Examples: "Find all React developers", "Who has Python experience?"
            
            - AVAILABILITY_CHECK: Checking availability/capacity
              Examples: "Who is available next month?", "Check Sarah's availability"
            
            - SKILL_MATCHING: Finding people with specific skills
              Examples: "Who knows machine learning?", "Find someone with AWS experience"
            
            - TEAM_RECOMMENDATION: AI-powered team suggestions
              Examples: "Suggest optimal team for this project", "Recommend best developers"
            
            Return ONLY the category name in uppercase."""),
            ("human", "{query}")
        ])
    
    async def classify_intent(self, query: str) -> IntentType:
        """Classify the intent of a user query"""
        try:
            response = await self.llm.ainvoke(
                self.classification_prompt.format_messages(query=query)
            )
            intent_str = response.content.strip().upper()
            
            # Map response to enum
            try:
                return IntentType(intent_str.lower())
            except ValueError:
                logger.warning("Unknown intent classification", intent=intent_str, query=query)
                return IntentType.COMPLEX_QUERY  # Default to complex for safety
                
        except Exception as e:
            logger.error("Intent classification failed", error=str(e), query=query)
            return IntentType.COMPLEX_QUERY  # Default to complex for safety
    
    def is_simple_query(self, intent: IntentType) -> bool:
        """Check if the intent represents a simple query that can be handled immediately"""
        return intent in [
            IntentType.SIMPLE_QUERY,
            IntentType.EMPLOYEE_SEARCH,
            IntentType.AVAILABILITY_CHECK,
            IntentType.SKILL_MATCHING
        ]
    
    def requires_streaming(self, intent: IntentType) -> bool:
        """Check if the intent requires streaming response"""
        return intent in [
            IntentType.COMPLEX_QUERY,
            IntentType.TEAM_RECOMMENDATION,
            IntentType.PROJECT_CREATION
        ]
    
    def get_intent_description(self, intent: IntentType) -> str:
        """Get human-readable description of the intent"""
        descriptions = {
            IntentType.SIMPLE_QUERY: "Simple data query",
            IntentType.COMPLEX_QUERY: "Complex analysis query",
            IntentType.ALLOCATION_MODIFICATION: "Allocation change request",
            IntentType.PROJECT_CREATION: "New project creation",
            IntentType.EMPLOYEE_SEARCH: "Employee search",
            IntentType.AVAILABILITY_CHECK: "Availability check",
            IntentType.SKILL_MATCHING: "Skill-based search",
            IntentType.TEAM_RECOMMENDATION: "AI team recommendation"
        }
        return descriptions.get(intent, "Unknown intent") 