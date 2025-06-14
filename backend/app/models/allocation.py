"""Allocation database model"""

import uuid

from app.models.base import BaseModel
from app.models.enums import AllocationPercentage, AllocationStatus
from sqlalchemy import UUID, Column, Date, Enum, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship


class Allocation(BaseModel):
    """Allocation model - represents employee assignments to projects"""

    __tablename__ = "allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    percent_allocated = Column(Integer, default=AllocationPercentage.FULL.value, nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    # Status tracking
    status = Column(Enum(AllocationStatus), default=AllocationStatus.ACTIVE, index=True)

    # Financial tracking
    hourly_rate = Column(Numeric(10, 2), nullable=True)  # Rate for this specific allocation
    monthly_cost = Column(Numeric(12, 2), nullable=True)  # Monthly cost for this allocation

    # Relationships
    project = relationship("Project", back_populates="allocations")
    employee = relationship("Employee", back_populates="allocations")

    # Constraints
    __table_args__ = (
        UniqueConstraint("project_id", "employee_id", "start_date", name="unique_allocation"),
    )

    def __repr__(self):
        return (
            f"<Allocation(id={self.id}, employee_id={self.employee_id}, "
            f"project_id={self.project_id}, percent={self.percent_allocated}%)>"
        )
