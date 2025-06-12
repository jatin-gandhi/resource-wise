"""Project database model"""

import uuid

from app.models.base import BaseModel
from app.models.enums import ProjectStatus, ProjectType
from sqlalchemy import ARRAY, UUID, Column, Enum, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship


class Project(BaseModel):
    """Project model"""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    duration_months = Column(Integer)
    tech_stack = Column(ARRAY(String), default=[])  # Array of technologies
    project_type = Column(Enum(ProjectType), nullable=False, index=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)

    # Requirements
    required_roles = Column(ARRAY(String), default=[])
    required_skills = Column(ARRAY(String), default=[])

    # Full-text search vector (automatically maintained by trigger)
    search_vector = Column(TSVECTOR)

    # Relationships
    allocations = relationship("Allocation", back_populates="project", cascade="all, delete-orphan")

    # Indexes for better performance
    __table_args__ = (
        # GIN index for full-text search
        Index("idx_project_search_vector", search_vector, postgresql_using="gin"),
        # GIN index for array searches
        Index("idx_project_tech_stack", tech_stack, postgresql_using="gin"),
        Index("idx_project_required_skills", required_skills, postgresql_using="gin"),
        # Composite index for common queries
        Index("idx_project_status_duration", status, duration_months),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status.value}')>"
