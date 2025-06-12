"""Base model with auditing fields"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, Column, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class BaseModel(Base):
    """Base model with auditing fields for all entities"""

    __abstract__ = True

    # Timestamp auditing fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Soft delete

    # User tracking auditing fields - Foreign keys to users table
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )  # Who created this record
    updated_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )  # Who last updated this record
    deleted_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )  # Who deleted this record

    def soft_delete(self, deleted_by_user_id: uuid.UUID | None = None):
        """Mark record as soft deleted"""
        self.deleted_at = datetime.now(UTC)
        if deleted_by_user_id:
            self.deleted_by = deleted_by_user_id

    def update_audit_fields(self, updated_by_user_id: uuid.UUID | None = None):
        """Update audit fields for manual updates"""
        if updated_by_user_id:
            self.updated_by = updated_by_user_id
