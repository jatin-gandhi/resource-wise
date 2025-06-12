"""add tsvector triggers and functions

Revision ID: dfd42fe4d81a
Revises: 1fecf4fe661d
Create Date: 2025-06-12 21:49:45.337141

"""

from typing import Sequence, Union

import pgvector
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dfd42fe4d81a"
down_revision: Union[str, None] = "1fecf4fe661d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create TSVector update functions

    # 1. Employee search vector function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_employee_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # 2. User search vector function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_user_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.username, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.full_name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.bio, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # 3. Project search vector function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_project_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # 4. Designation search vector function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_designation_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.code, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # 5. Employee skill search vector function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_employee_skill_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.skill_name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create triggers for automatic TSVector updates

    # Employee triggers
    op.execute(
        """
        CREATE TRIGGER employee_search_vector_update
            BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE FUNCTION update_employee_search_vector();
    """
    )

    # User triggers
    op.execute(
        """
        CREATE TRIGGER user_search_vector_update
            BEFORE INSERT OR UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_user_search_vector();
    """
    )

    # Project triggers
    op.execute(
        """
        CREATE TRIGGER project_search_vector_update
            BEFORE INSERT OR UPDATE ON projects
            FOR EACH ROW EXECUTE FUNCTION update_project_search_vector();
    """
    )

    # Designation triggers
    op.execute(
        """
        CREATE TRIGGER designation_search_vector_update
            BEFORE INSERT OR UPDATE ON designations
            FOR EACH ROW EXECUTE FUNCTION update_designation_search_vector();
    """
    )

    # Employee skill triggers
    op.execute(
        """
        CREATE TRIGGER employee_skill_search_vector_update
            BEFORE INSERT OR UPDATE ON employee_skills
            FOR EACH ROW EXECUTE FUNCTION update_employee_skill_search_vector();
    """
    )

    # Update existing records to populate search_vector fields
    op.execute("UPDATE employees SET search_vector = search_vector WHERE id IS NOT NULL;")
    op.execute("UPDATE users SET search_vector = search_vector WHERE id IS NOT NULL;")
    op.execute("UPDATE projects SET search_vector = search_vector WHERE id IS NOT NULL;")
    op.execute("UPDATE designations SET search_vector = search_vector WHERE id IS NOT NULL;")
    op.execute("UPDATE employee_skills SET search_vector = search_vector WHERE id IS NOT NULL;")


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS employee_search_vector_update ON employees;")
    op.execute("DROP TRIGGER IF EXISTS user_search_vector_update ON users;")
    op.execute("DROP TRIGGER IF EXISTS project_search_vector_update ON projects;")
    op.execute("DROP TRIGGER IF EXISTS designation_search_vector_update ON designations;")
    op.execute("DROP TRIGGER IF EXISTS employee_skill_search_vector_update ON employee_skills;")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_employee_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_user_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_project_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_designation_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_employee_skill_search_vector();")
