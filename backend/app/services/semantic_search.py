"""Semantic Search Service using OpenAI Embeddings and pgvector"""

from typing import List, Dict, Tuple, Any, Optional
import structlog
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from sqlalchemy import text, select
import numpy as np

logger = structlog.get_logger()


class SemanticSearchService:
    """Provides semantic search capabilities for employees and projects"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )
    
    async def search_employees_by_skills(
        self, 
        query: str, 
        limit: int = 10,
        similarity_threshold: float = 0.7,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Search employees using semantic similarity on skills and experience"""
        
        try:
            # Generate embedding for query
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Convert to string format for PostgreSQL
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Perform hybrid search combining semantic and text search
            sql = text("""
                WITH semantic_scores AS (
                    SELECT 
                        e.id,
                        e.name,
                        e.email,
                        d.title as designation,
                        d.code as designation_code,
                        e.capacity_percent,
                        e.is_active,
                        ee.summary,
                        ee.source,
                        (ee.embedding <=> :query_embedding::vector) as semantic_distance,
                        1 - (ee.embedding <=> :query_embedding::vector) as semantic_score
                    FROM employees e
                    JOIN designations d ON e.designation_id = d.id
                    JOIN employee_embeddings ee ON e.id = ee.employee_id
                    WHERE (:include_inactive OR e.is_active = true)
                    AND (ee.embedding <=> :query_embedding::vector) < :distance_threshold
                ),
                text_scores AS (
                    SELECT 
                        e.id,
                        ts_rank(e.search_vector, plainto_tsquery(:query)) as text_score
                    FROM employees e
                    WHERE e.search_vector @@ plainto_tsquery(:query)
                    AND (:include_inactive OR e.is_active = true)
                ),
                current_allocations AS (
                    SELECT 
                        employee_id,
                        SUM(
                            CASE 
                                WHEN percent_allocated = 'QUARTER' THEN 25
                                WHEN percent_allocated = 'HALF' THEN 50
                                WHEN percent_allocated = 'THREE_QUARTER' THEN 75
                                WHEN percent_allocated = 'FULL' THEN 100
                                ELSE 0
                            END
                        ) as total_allocated
                    FROM allocations
                    WHERE status = 'ACTIVE'
                    AND start_date <= CURRENT_DATE
                    AND end_date >= CURRENT_DATE
                    GROUP BY employee_id
                )
                SELECT 
                    ss.*,
                    COALESCE(ts.text_score, 0) as text_score,
                    COALESCE(ca.total_allocated, 0) as current_allocation,
                    ss.capacity_percent - COALESCE(ca.total_allocated, 0) as available_capacity,
                    (ss.semantic_score * 0.7 + COALESCE(ts.text_score, 0) * 0.3) as combined_score
                FROM semantic_scores ss
                LEFT JOIN text_scores ts ON ss.id = ts.id
                LEFT JOIN current_allocations ca ON ss.id = ca.employee_id
                ORDER BY combined_score DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(sql, {
                "query_embedding": embedding_str,
                "query": query,
                "distance_threshold": 1 - similarity_threshold,
                "limit": limit,
                "include_inactive": include_inactive
            })
            
            employees = []
            for row in result.fetchall():
                employee_data = {
                    "id": str(row.id),
                    "name": row.name,
                    "email": row.email,
                    "designation": row.designation,
                    "designation_code": row.designation_code,
                    "capacity_percent": row.capacity_percent,
                    "is_active": row.is_active,
                    "summary": row.summary,
                    "source": row.source,
                    "semantic_score": float(row.semantic_score),
                    "text_score": float(row.text_score),
                    "combined_score": float(row.combined_score),
                    "current_allocation": int(row.current_allocation),
                    "available_capacity": int(row.available_capacity)
                }
                employees.append(employee_data)
            
            return employees
            
        except Exception as e:
            logger.error("Employee semantic search failed", error=str(e), query=query)
            return []
    
    async def search_projects_by_description(
        self,
        query: str,
        limit: int = 10,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search projects using text search on description and tech stack"""
        
        try:
            # Build the SQL query with optional status filter
            status_condition = ""
            if status_filter:
                status_condition = "AND p.status = :status_filter"
            
            sql = text(f"""
                SELECT 
                    p.id,
                    p.name,
                    p.description,
                    p.duration_months,
                    p.tech_stack,
                    p.project_type,
                    p.status,
                    p.required_roles,
                    p.required_skills,
                    ts_rank(p.search_vector, plainto_tsquery(:query)) as relevance_score,
                    COUNT(a.id) as team_size
                FROM projects p
                LEFT JOIN allocations a ON p.id = a.project_id 
                    AND a.status = 'ACTIVE'
                    AND a.start_date <= CURRENT_DATE 
                    AND a.end_date >= CURRENT_DATE
                WHERE p.search_vector @@ plainto_tsquery(:query)
                {status_condition}
                GROUP BY p.id, p.name, p.description, p.duration_months, p.tech_stack, 
                         p.project_type, p.status, p.required_roles, p.required_skills, p.search_vector
                ORDER BY relevance_score DESC
                LIMIT :limit
            """)
            
            params = {
                "query": query,
                "limit": limit
            }
            if status_filter:
                params["status_filter"] = status_filter
            
            result = await self.db.execute(sql, params)
            
            projects = []
            for row in result.fetchall():
                project_data = {
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "duration_months": row.duration_months,
                    "tech_stack": row.tech_stack or [],
                    "project_type": row.project_type,
                    "status": row.status,
                    "required_roles": row.required_roles or [],
                    "required_skills": row.required_skills or [],
                    "relevance_score": float(row.relevance_score),
                    "team_size": int(row.team_size)
                }
                projects.append(project_data)
            
            return projects
            
        except Exception as e:
            logger.error("Project search failed", error=str(e), query=query)
            return []
    
    async def find_available_employees(
        self,
        required_skills: List[str] = None,
        min_availability: int = 25,
        designation_codes: List[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find employees with availability and optional skill/designation filters"""
        
        try:
            # Build skill matching condition
            skill_condition = ""
            if required_skills:
                skill_queries = [f"plainto_tsquery('{skill}')" for skill in required_skills]
                skill_condition = f"AND (e.search_vector @@ ({' || '.join(skill_queries)}))"
            
            # Build designation filter
            designation_condition = ""
            if designation_codes:
                designation_placeholders = ",".join([f"'{code}'" for code in designation_codes])
                designation_condition = f"AND d.code IN ({designation_placeholders})"
            
            sql = text(f"""
                WITH current_allocations AS (
                    SELECT 
                        employee_id,
                        SUM(
                            CASE 
                                WHEN percent_allocated = 'QUARTER' THEN 25
                                WHEN percent_allocated = 'HALF' THEN 50
                                WHEN percent_allocated = 'THREE_QUARTER' THEN 75
                                WHEN percent_allocated = 'FULL' THEN 100
                                ELSE 0
                            END
                        ) as total_allocated
                    FROM allocations
                    WHERE status = 'ACTIVE'
                    AND start_date <= CURRENT_DATE
                    AND end_date >= CURRENT_DATE
                    GROUP BY employee_id
                )
                SELECT 
                    e.id,
                    e.name,
                    e.email,
                    d.title as designation,
                    d.code as designation_code,
                    d.level as designation_level,
                    e.capacity_percent,
                    COALESCE(ca.total_allocated, 0) as current_allocation,
                    e.capacity_percent - COALESCE(ca.total_allocated, 0) as available_capacity,
                    ROUND((e.capacity_percent - COALESCE(ca.total_allocated, 0)) * 100.0 / e.capacity_percent, 1) as availability_percentage
                FROM employees e
                JOIN designations d ON e.designation_id = d.id
                LEFT JOIN current_allocations ca ON e.id = ca.employee_id
                WHERE e.is_active = true
                AND (e.capacity_percent - COALESCE(ca.total_allocated, 0)) >= :min_availability
                {skill_condition}
                {designation_condition}
                ORDER BY available_capacity DESC, d.level DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(sql, {
                "min_availability": min_availability,
                "limit": limit
            })
            
            employees = []
            for row in result.fetchall():
                employee_data = {
                    "id": str(row.id),
                    "name": row.name,
                    "email": row.email,
                    "designation": row.designation,
                    "designation_code": row.designation_code,
                    "designation_level": row.designation_level,
                    "capacity_percent": row.capacity_percent,
                    "current_allocation": int(row.current_allocation),
                    "available_capacity": int(row.available_capacity),
                    "availability_percentage": float(row.availability_percentage)
                }
                employees.append(employee_data)
            
            return employees
            
        except Exception as e:
            logger.error("Available employees search failed", error=str(e))
            return []
    
    async def get_employee_skills_summary(self, employee_id: str) -> Dict[str, Any]:
        """Get detailed skills summary for an employee"""
        
        try:
            sql = text("""
                SELECT 
                    es.skill_name,
                    es.summary,
                    es.experience_months,
                    es.last_used,
                    es.source,
                    ee.summary as embedding_summary
                FROM employee_skills es
                LEFT JOIN employee_embeddings ee ON es.employee_id = ee.employee_id
                WHERE es.employee_id = :employee_id
                ORDER BY es.experience_months DESC, es.last_used DESC
            """)
            
            result = await self.db.execute(sql, {"employee_id": employee_id})
            
            skills = []
            for row in result.fetchall():
                skill_data = {
                    "skill_name": row.skill_name,
                    "summary": row.summary,
                    "experience_months": row.experience_months,
                    "last_used": row.last_used.isoformat() if row.last_used else None,
                    "source": row.source
                }
                skills.append(skill_data)
            
            # Get embedding summary if available
            embedding_summary = None
            if result.rowcount > 0:
                first_row = result.fetchone()
                if first_row and hasattr(first_row, 'embedding_summary'):
                    embedding_summary = first_row.embedding_summary
            
            return {
                "employee_id": employee_id,
                "skills": skills,
                "embedding_summary": embedding_summary
            }
            
        except Exception as e:
            logger.error("Employee skills summary failed", error=str(e), employee_id=employee_id)
            return {"employee_id": employee_id, "skills": [], "embedding_summary": None} 