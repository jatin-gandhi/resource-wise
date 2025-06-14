"""Employee database model"""

import uuid

from app.models.base import BaseModel
from app.models.enums import EmployeeGroup, EmployeeType
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, validates


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
    onboarded_at = Column(Date, nullable=True)  # Nullable for historical data flexibility
    is_active = Column(Boolean, default=True, index=True)

    # Organization and classification fields
    employee_group = Column(Enum(EmployeeGroup), nullable=True, index=True)  # KD India, KD-US, etc.
    organization = Column(String(100), nullable=True, index=True)  # Company/partner name
    employee_type = Column(
        Enum(EmployeeType), nullable=True, index=True
    )  # Full-time, contractor, etc.
    location = Column(String(100), nullable=True, index=True)  # Bangalore, New York, Remote

    # Financial fields
    cost_per_hour = Column(Numeric(10, 2), nullable=True)  # Internal cost rate
    billing_rate = Column(Numeric(10, 2), nullable=True)  # Client billing rate

    # Full-text search vector (automatically maintained by trigger)
    search_vector = Column(TSVECTOR)

    # Relationships
    designation_ref = relationship("Designation", back_populates="employees")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    embeddings = relationship(
        "EmployeeEmbedding", back_populates="employee", cascade="all, delete-orphan"
    )
    allocations = relationship(
        "Allocation", back_populates="employee", cascade="all, delete-orphan"
    )
    managed_projects = relationship(
        "Project", back_populates="project_manager", foreign_keys="Project.project_manager_id"
    )

    # Indexes for better performance
    __table_args__ = (
        # GIN index for full-text search
        Index("idx_employee_search_vector", search_vector, postgresql_using="gin"),
        # Composite index for common queries
        Index("idx_employee_active_designation", is_active, designation_id),
        Index("idx_employees_group_type", employee_group, employee_type),
        Index("idx_employees_organization", organization),
        Index("idx_employees_location", location),
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

    @validates("email")
    def normalize_email(self, key, value):
        """Normalize email to lowercase and strip whitespace"""
        if value:
            return value.lower().strip()
        return value
