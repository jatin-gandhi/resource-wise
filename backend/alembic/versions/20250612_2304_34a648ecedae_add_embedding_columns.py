"""add embedding columns for semantic search

Revision ID: 20250613_0001
Revises: 20250612_2306_a1b2c3d4e5f6
Create Date: 2025-06-13 00:01:00.000000

"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "34a648ecedae"
down_revision = "4c3b1d2fdf93"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.add_column("employee_skills", sa.Column("embedding", Vector(1536)))
    op.add_column("designations", sa.Column("embedding", Vector(1536)))
    op.add_column("projects", sa.Column("embedding", Vector(1536)))


def downgrade():
    op.drop_column("employee_skills", "embedding")
    op.drop_column("designations", "embedding")
    op.drop_column("projects", "embedding")
