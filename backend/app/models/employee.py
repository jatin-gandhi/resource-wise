"""Employee database model"""

import uuid

from sqlalchemy import UUID, Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Employee(BaseModel):
    """Employee model"""

    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    designation_id = Column(
        UUID(as_uuid=True), ForeignKey("designations.id"), nullable=False, index=True
    )
    capacity_percent = Column(Integer, default=100)  # e.g. 100, 70, 50
    onboarded_at = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    designation_ref = relationship("Designation", back_populates="employees")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    embeddings = relationship(
        "EmployeeEmbedding", back_populates="employee", cascade="all, delete-orphan"
    )
    allocations = relationship(
        "Allocation", back_populates="employee", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', designation_id={self.designation_id})>"

    @property
    def designation_code(self) -> str | None:
        """Get designation code for easy access"""
        return self.designation_ref.code if self.designation_ref else None

    @property
    def designation_title(self) -> str | None:
        """Get designation title for easy access"""
        return self.designation_ref.title if self.designation_ref else None
