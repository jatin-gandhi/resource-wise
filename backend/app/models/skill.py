"""Skill and embedding database models"""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, Column, Date, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import SkillProficiencyLevel, SkillSource


class EmployeeSkill(BaseModel):
    """Employee skill model - stores PAT and other skill assessments"""

    __tablename__ = "employee_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    summary = Column(Text)  # Description of experience
    experience_months = Column(Integer, default=0)  # Months of experience
    last_used = Column(Date)  # When last used this skill
    source = Column(Enum(SkillSource), default=SkillSource.PAT, index=True)

    # Skill rating (1-5 scale)
    proficiency_level = Column(Enum(SkillProficiencyLevel), default=SkillProficiencyLevel.BEGINNER)

    # Relationships
    employee = relationship("Employee", back_populates="skills")

    # Indexes for better performance
    __table_args__ = (
        Index("idx_employee_skill_name", employee_id, skill_name),
        Index("idx_skill_proficiency", skill_name, proficiency_level),
    )

    def __repr__(self):
        return (
            f"<EmployeeSkill(employee_id={self.employee_id}, "
            f"skill='{self.skill_name}', level={self.proficiency_level.value})>"
        )


class EmployeeEmbedding(BaseModel):
    """Employee embedding model - stores vector embeddings for semantic search"""

    __tablename__ = "employee_embeddings"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), primary_key=True)
    source = Column(String(50), primary_key=True)  # 'skills', 'projects', 'profile', etc.
    summary = Column(Text, nullable=False)  # The text that was embedded
    embedding = Column(Vector(1536))  # OpenAI ada-002 embedding dimension

    # Relationships
    employee = relationship("Employee", back_populates="embeddings")

    def __repr__(self):
        return f"<EmployeeEmbedding(employee_id={self.employee_id}, source='{self.source}')>"
