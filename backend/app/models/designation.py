"""Designation model for employee roles"""

import uuid

from app.models.base import BaseModel
from sqlalchemy import UUID, Boolean, Column, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship


class Designation(BaseModel):
    """Designation/Role model with hierarchy and metadata"""

    __tablename__ = "designations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic designation info
    code = Column(String(20), unique=True, nullable=False, index=True)  # TL, SSE, SD
    title = Column(String(100), nullable=False)  # Team Lead, Senior Software Engineer
    description = Column(Text)  # Role description

    # Hierarchy and organizational info
    level = Column(Integer, nullable=False, index=True)  # 1=Junior, 5=Senior
    is_leadership = Column(Boolean, default=False)  # Can lead teams
    is_active = Column(Boolean, default=True, index=True)  # Currently in use

    # Full-text search vector (automatically maintained by trigger)
    search_vector = Column(TSVECTOR)

    # Indexes for better performance
    __table_args__ = (
        # GIN index for full-text search
        Index("idx_designation_search_vector", search_vector, postgresql_using="gin"),
        # Composite index for common queries
        Index("idx_designation_active_level", is_active, level),
        Index("idx_designation_leadership_level", is_leadership, level),
    )

    # Relationships
    employees = relationship("Employee", back_populates="designation_ref")

    def __repr__(self):
        return f"<Designation(code='{self.code}', title='{self.title}', level={self.level})>"

    @property
    def display_name(self) -> str:
        """Human-readable display name"""
        return f"{self.title} ({self.code})"
