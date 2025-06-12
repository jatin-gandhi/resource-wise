"""add tsvector triggers and functions

Revision ID: 4c3b1d2fdf93
Revises: b8a13321c65e
Create Date: 2025-01-12 23:02:30.825088

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c3b1d2fdf93"
down_revision: Union[str, None] = "b8a13321c65e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create TSVector update functions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_user_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.username, '') || ' ' ||
                COALESCE(NEW.email, '') || ' ' ||
                COALESCE(NEW.full_name, '') || ' ' ||
                COALESCE(NEW.bio, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_designation_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.code, '') || ' ' ||
                COALESCE(NEW.title, '') || ' ' ||
                COALESCE(NEW.description, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_project_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.name, '') || ' ' ||
                COALESCE(NEW.description, '') || ' ' ||
                COALESCE(array_to_string(NEW.tech_stack, ' '), '') || ' ' ||
                COALESCE(array_to_string(NEW.required_roles, ' '), '') || ' ' ||
                COALESCE(array_to_string(NEW.required_skills, ' '), '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_employee_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.name, '') || ' ' ||
                COALESCE(NEW.email, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_employee_embedding_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.source, '') || ' ' ||
                COALESCE(NEW.summary, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_employee_skill_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', 
                COALESCE(NEW.skill_name, '') || ' ' ||
                COALESCE(NEW.summary, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create triggers
    op.execute(
        """
        CREATE TRIGGER trigger_update_user_search_vector
        BEFORE INSERT OR UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_user_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_designation_search_vector
        BEFORE INSERT OR UPDATE ON designations
        FOR EACH ROW EXECUTE FUNCTION update_designation_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_project_search_vector
        BEFORE INSERT OR UPDATE ON projects
        FOR EACH ROW EXECUTE FUNCTION update_project_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_employee_search_vector
        BEFORE INSERT OR UPDATE ON employees
        FOR EACH ROW EXECUTE FUNCTION update_employee_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_employee_embedding_search_vector
        BEFORE INSERT OR UPDATE ON employee_embeddings
        FOR EACH ROW EXECUTE FUNCTION update_employee_embedding_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_update_employee_skill_search_vector
        BEFORE INSERT OR UPDATE ON employee_skills
        FOR EACH ROW EXECUTE FUNCTION update_employee_skill_search_vector();
    """
    )


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_update_user_search_vector ON users;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_designation_search_vector ON designations;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_project_search_vector ON projects;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_employee_search_vector ON employees;")
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_update_employee_embedding_search_vector ON employee_embeddings;"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_update_employee_skill_search_vector ON employee_skills;"
    )

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_user_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_designation_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_project_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_employee_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_employee_embedding_search_vector();")
    op.execute("DROP FUNCTION IF EXISTS update_employee_skill_search_vector();")
