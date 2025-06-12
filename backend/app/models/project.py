"""Project database model"""

import uuid

from sqlalchemy import ARRAY, UUID, Column, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import ProjectStatus


class Project(BaseModel):
    """Project model"""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    duration_months = Column(Integer)
    tech_stack = Column(ARRAY(String), default=[])  # Array of technologies
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)

    # Requirements
    required_roles = Column(ARRAY(String), default=[])
    required_skills = Column(ARRAY(String), default=[])

    # Relationships
    allocations = relationship("Allocation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status.value}')>"
