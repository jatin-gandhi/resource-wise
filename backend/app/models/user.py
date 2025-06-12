"""User authentication model"""

import uuid

from app.models.base import BaseModel
from sqlalchemy import UUID, Boolean, Column, Index, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import validates


class User(BaseModel):
    """User model for authentication and audit tracking"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication fields
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile fields
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)

    # Optional profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Full-text search vector (automatically maintained by trigger)
    search_vector = Column(TSVECTOR)

    # Indexes for better performance
    __table_args__ = (
        # GIN index for full-text search
        Index("idx_user_search_vector", search_vector, postgresql_using="gin"),
        # Composite index for common queries
        Index("idx_user_active_superuser", is_active, is_superuser),
    )

    # Relationships - we'll add these when we have other models that reference users
    # created_records = relationship("BaseModel", foreign_keys="BaseModel.created_by")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (for compatibility)"""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (for compatibility)"""
        return False

    @validates("email")
    def normalize_email(self, key, value):
        """Normalize email to lowercase and strip whitespace"""
        if value:
            return value.lower().strip()
        return value

    @validates("username")
    def normalize_username(self, key, value):
        """Normalize username to lowercase and strip whitespace"""
        if value:
            return value.lower().strip()
        return value
