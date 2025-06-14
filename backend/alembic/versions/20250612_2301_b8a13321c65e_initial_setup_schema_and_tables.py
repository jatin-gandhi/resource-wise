"""initial setup - schema and tables

Revision ID: b8a13321c65e
Revises: 
Create Date: 2025-06-12 23:01:12.270623

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8a13321c65e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Enum types will be created automatically by SQLAlchemy when tables are created

    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_active_superuser', 'users', ['is_active', 'is_superuser'], unique=False)
    op.create_index('idx_user_search_vector', 'users', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_users_created_by'), 'users', ['created_by'], unique=False)
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_users_deleted_by'), 'users', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_updated_by'), 'users', ['updated_by'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table(
        "designations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("is_leadership", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index('idx_designation_active_level', 'designations', ['is_active', 'level'], unique=False)
    op.create_index('idx_designation_leadership_level', 'designations', ['is_leadership', 'level'], unique=False)
    op.create_index('idx_designation_search_vector', 'designations', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_designations_code'), 'designations', ['code'], unique=True)
    op.create_index(op.f('ix_designations_created_by'), 'designations', ['created_by'], unique=False)
    op.create_index(op.f('ix_designations_deleted_at'), 'designations', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_designations_deleted_by'), 'designations', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_designations_is_active'), 'designations', ['is_active'], unique=False)
    op.create_index(op.f('ix_designations_level'), 'designations', ['level'], unique=False)
    op.create_index(op.f('ix_designations_updated_by'), 'designations', ['updated_by'], unique=False)
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("tech_stack", sa.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "project_type", sa.Enum("CUSTOMER", "INTERNAL", name="projecttype"), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PLANNING", "ACTIVE", "ON_HOLD", "COMPLETED", "CANCELLED", name="projectstatus"
            ),
            nullable=True,
        ),
        sa.Column("required_roles", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("required_skills", sa.ARRAY(sa.String()), nullable=True),
        # New business fields for project management
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("project_manager_id", sa.UUID(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("project_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("monthly_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index('idx_project_required_skills', 'projects', ['required_skills'], unique=False, postgresql_using='gin')
    op.create_index('idx_project_search_vector', 'projects', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index('idx_project_status_duration', 'projects', ['status', 'duration_months'], unique=False)
    op.create_index('idx_project_tech_stack', 'projects', ['tech_stack'], unique=False, postgresql_using='gin')
    op.create_index("idx_project_customer_name", "projects", ["customer_name"], unique=False)
    op.create_index("idx_project_manager", "projects", ["project_manager_id"], unique=False)
    op.create_index("idx_project_dates", "projects", ["start_date", "end_date"], unique=False)
    op.create_index(op.f('ix_projects_created_by'), 'projects', ['created_by'], unique=False)
    op.create_index(op.f('ix_projects_deleted_at'), 'projects', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_projects_deleted_by'), 'projects', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_project_type'), 'projects', ['project_type'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)
    op.create_index(op.f('ix_projects_updated_by'), 'projects', ['updated_by'], unique=False)
    op.create_table(
        "employees",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("designation_id", sa.UUID(), nullable=False),
        sa.Column("capacity_percent", sa.Integer(), nullable=True),
        sa.Column("onboarded_at", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        # New business fields for employee organization and financial data
        sa.Column(
            "employee_group",
            sa.Enum("KD_INDIA", "KD_US", "DEV_PARTNER", "INDEPENDENT", name="employeegroup"),
            nullable=True,
        ),
        sa.Column(
            "employee_type",
            sa.Enum("FULL_TIME", "CONTRACTOR", "CONSULTANT", "INTERN", name="employeetype"),
            nullable=True,
        ),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("cost_per_hour", sa.Numeric(8, 2), nullable=True),
        sa.Column("billing_rate", sa.Numeric(8, 2), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["designation_id"],
            ["designations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index('idx_employee_active_designation', 'employees', ['is_active', 'designation_id'], unique=False)
    op.create_index('idx_employee_search_vector', 'employees', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(
        "idx_employee_organization", "employees", ["employee_group", "employee_type"], unique=False
    )
    op.create_index("idx_employee_location", "employees", ["location"], unique=False)
    op.create_index(
        "idx_employee_financial", "employees", ["cost_per_hour", "billing_rate"], unique=False
    )
    op.create_index(op.f('ix_employees_created_by'), 'employees', ['created_by'], unique=False)
    op.create_index(op.f('ix_employees_deleted_at'), 'employees', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_employees_deleted_by'), 'employees', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_employees_designation_id'), 'employees', ['designation_id'], unique=False)
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=True)
    op.create_index(op.f('ix_employees_is_active'), 'employees', ['is_active'], unique=False)
    op.create_index(op.f('ix_employees_name'), 'employees', ['name'], unique=False)
    op.create_index(op.f('ix_employees_updated_by'), 'employees', ['updated_by'], unique=False)
    op.create_table(
        "allocations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("percent_allocated", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "COMPLETED", "CANCELLED", name="allocationstatus"),
            nullable=True,
        ),
        # New business fields for allocation financial tracking
        sa.Column("hourly_rate", sa.Numeric(8, 2), nullable=True),
        sa.Column("monthly_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "employee_id", "start_date", name="unique_allocation"),
        # CRITICAL: Constraint to ensure total allocation per employee doesn't exceed 100%
        sa.CheckConstraint(
            "percent_allocated > 0 AND percent_allocated <= 100", name="check_allocation_range"
        ),
    )
    op.create_index(op.f('ix_allocations_created_by'), 'allocations', ['created_by'], unique=False)
    op.create_index(op.f('ix_allocations_deleted_at'), 'allocations', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_allocations_deleted_by'), 'allocations', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_allocations_employee_id'), 'allocations', ['employee_id'], unique=False)
    op.create_index(op.f('ix_allocations_end_date'), 'allocations', ['end_date'], unique=False)
    op.create_index(op.f('ix_allocations_project_id'), 'allocations', ['project_id'], unique=False)
    op.create_index(op.f('ix_allocations_start_date'), 'allocations', ['start_date'], unique=False)
    op.create_index(op.f('ix_allocations_status'), 'allocations', ['status'], unique=False)
    op.create_index(op.f('ix_allocations_updated_by'), 'allocations', ['updated_by'], unique=False)
    op.create_index(
        "idx_allocation_financial", "allocations", ["hourly_rate", "monthly_cost"], unique=False
    )

    # Add foreign key constraint for project manager after employees table is created
    op.create_foreign_key(
        "fk_project_manager", "projects", "employees", ["project_manager_id"], ["id"]
    )

    # Create function and trigger to enforce total allocation constraint
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_total_allocation()
        RETURNS TRIGGER AS $$
        DECLARE
            total_allocation INTEGER;
        BEGIN
            -- Calculate total allocation for the employee across all active allocations
            SELECT COALESCE(SUM(percent_allocated), 0) INTO total_allocation
            FROM allocations 
            WHERE employee_id = NEW.employee_id 
            AND status = 'ACTIVE'
            AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::uuid)
            AND (
                -- Check for overlapping date ranges
                (start_date <= NEW.end_date AND end_date >= NEW.start_date)
            );
            
            -- Add the new/updated allocation
            total_allocation := total_allocation + NEW.percent_allocated;
            
            -- Check if total exceeds 100%
            IF total_allocation > 100 THEN
                RAISE EXCEPTION 'Total allocation for employee cannot exceed 100%%. Current total would be: %', total_allocation;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_check_total_allocation
        BEFORE INSERT OR UPDATE ON allocations
        FOR EACH ROW
        EXECUTE FUNCTION check_total_allocation();
    """
    )

    op.create_table(
        "employee_embeddings",
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("employee_id", "source"),
    )
    op.create_index('idx_employee_embedding_cosine', 'employee_embeddings', ['embedding'], unique=False, postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}, postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.create_index('idx_employee_embedding_ivfflat', 'employee_embeddings', ['embedding'], unique=False, postgresql_using='ivfflat', postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.create_index('idx_employee_embedding_search_vector', 'employee_embeddings', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_employee_embeddings_created_by'), 'employee_embeddings', ['created_by'], unique=False)
    op.create_index(op.f('ix_employee_embeddings_deleted_at'), 'employee_embeddings', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_employee_embeddings_deleted_by'), 'employee_embeddings', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_employee_embeddings_updated_by'), 'employee_embeddings', ['updated_by'], unique=False)
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("skill_name", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("experience_months", sa.Integer(), nullable=True),
        sa.Column("last_used", sa.Date(), nullable=True),
        sa.Column(
            "source",
            sa.Enum(
                "PAT", "MANUAL", "SEED", "SELF_ASSESSMENT", "MANAGER_ASSESSMENT", name="skillsource"
            ),
            nullable=True,
        ),
        sa.Column("proficiency_level", sa.Integer(), nullable=True),  # Changed to Integer (1-5)
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "proficiency_level >= 1 AND proficiency_level <= 5", name="check_proficiency_range"
        ),
    )
    op.create_index('idx_employee_skill_name', 'employee_skills', ['employee_id', 'skill_name'], unique=False)
    op.create_index('idx_employee_skill_search_vector', 'employee_skills', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index('idx_skill_proficiency', 'employee_skills', ['skill_name', 'proficiency_level'], unique=False)
    op.create_index(op.f('ix_employee_skills_created_by'), 'employee_skills', ['created_by'], unique=False)
    op.create_index(op.f('ix_employee_skills_deleted_at'), 'employee_skills', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_employee_skills_deleted_by'), 'employee_skills', ['deleted_by'], unique=False)
    op.create_index(op.f('ix_employee_skills_employee_id'), 'employee_skills', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_skills_skill_name'), 'employee_skills', ['skill_name'], unique=False)
    op.create_index(op.f('ix_employee_skills_source'), 'employee_skills', ['source'], unique=False)
    op.create_index(op.f('ix_employee_skills_updated_by'), 'employee_skills', ['updated_by'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Drop trigger and function first
    op.execute("DROP TRIGGER IF EXISTS trigger_check_total_allocation ON allocations;")
    op.execute("DROP FUNCTION IF EXISTS check_total_allocation();")

    op.drop_index(op.f('ix_employee_skills_updated_by'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_source'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_skill_name'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_employee_id'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_deleted_by'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_deleted_at'), table_name='employee_skills')
    op.drop_index(op.f('ix_employee_skills_created_by'), table_name='employee_skills')
    op.drop_index('idx_skill_proficiency', table_name='employee_skills')
    op.drop_index('idx_employee_skill_search_vector', table_name='employee_skills', postgresql_using='gin')
    op.drop_index('idx_employee_skill_name', table_name='employee_skills')
    op.drop_table('employee_skills')
    op.drop_index(op.f('ix_employee_embeddings_updated_by'), table_name='employee_embeddings')
    op.drop_index(op.f('ix_employee_embeddings_deleted_by'), table_name='employee_embeddings')
    op.drop_index(op.f('ix_employee_embeddings_deleted_at'), table_name='employee_embeddings')
    op.drop_index(op.f('ix_employee_embeddings_created_by'), table_name='employee_embeddings')
    op.drop_index('idx_employee_embedding_search_vector', table_name='employee_embeddings', postgresql_using='gin')
    op.drop_index('idx_employee_embedding_ivfflat', table_name='employee_embeddings', postgresql_using='ivfflat', postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.drop_index('idx_employee_embedding_cosine', table_name='employee_embeddings', postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}, postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.drop_table('employee_embeddings')

    # Drop foreign key constraint first
    op.drop_constraint("fk_project_manager", "projects", type_="foreignkey")

    op.drop_index("idx_allocation_financial", table_name="allocations")
    op.drop_index(op.f('ix_allocations_updated_by'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_status'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_start_date'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_project_id'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_end_date'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_employee_id'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_deleted_by'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_deleted_at'), table_name='allocations')
    op.drop_index(op.f('ix_allocations_created_by'), table_name='allocations')
    op.drop_table('allocations')
    op.drop_index("idx_employee_financial", table_name="employees")
    op.drop_index("idx_employee_location", table_name="employees")
    op.drop_index("idx_employee_organization", table_name="employees")
    op.drop_index(op.f('ix_employees_updated_by'), table_name='employees')
    op.drop_index(op.f('ix_employees_name'), table_name='employees')
    op.drop_index(op.f('ix_employees_is_active'), table_name='employees')
    op.drop_index(op.f('ix_employees_email'), table_name='employees')
    op.drop_index(op.f('ix_employees_designation_id'), table_name='employees')
    op.drop_index(op.f('ix_employees_deleted_by'), table_name='employees')
    op.drop_index(op.f('ix_employees_deleted_at'), table_name='employees')
    op.drop_index(op.f('ix_employees_created_by'), table_name='employees')
    op.drop_index('idx_employee_search_vector', table_name='employees', postgresql_using='gin')
    op.drop_index('idx_employee_active_designation', table_name='employees')
    op.drop_table('employees')
    op.drop_index("idx_project_dates", table_name="projects")
    op.drop_index("idx_project_manager", table_name="projects")
    op.drop_index("idx_project_customer_name", table_name="projects")
    op.drop_index(op.f('ix_projects_updated_by'), table_name='projects')
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_type'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_deleted_by'), table_name='projects')
    op.drop_index(op.f('ix_projects_deleted_at'), table_name='projects')
    op.drop_index(op.f('ix_projects_created_by'), table_name='projects')
    op.drop_index('idx_project_tech_stack', table_name='projects', postgresql_using='gin')
    op.drop_index('idx_project_status_duration', table_name='projects')
    op.drop_index('idx_project_search_vector', table_name='projects', postgresql_using='gin')
    op.drop_index('idx_project_required_skills', table_name='projects', postgresql_using='gin')
    op.drop_table('projects')
    op.drop_index(op.f('ix_designations_updated_by'), table_name='designations')
    op.drop_index(op.f('ix_designations_level'), table_name='designations')
    op.drop_index(op.f('ix_designations_is_active'), table_name='designations')
    op.drop_index(op.f('ix_designations_deleted_by'), table_name='designations')
    op.drop_index(op.f('ix_designations_deleted_at'), table_name='designations')
    op.drop_index(op.f('ix_designations_created_by'), table_name='designations')
    op.drop_index(op.f('ix_designations_code'), table_name='designations')
    op.drop_index('idx_designation_search_vector', table_name='designations', postgresql_using='gin')
    op.drop_index('idx_designation_leadership_level', table_name='designations')
    op.drop_index('idx_designation_active_level', table_name='designations')
    op.drop_table('designations')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_updated_by'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_deleted_by'), table_name='users')
    op.drop_index(op.f('ix_users_deleted_at'), table_name='users')
    op.drop_index(op.f('ix_users_created_by'), table_name='users')
    op.drop_index('idx_user_search_vector', table_name='users', postgresql_using='gin')
    op.drop_index('idx_user_active_superuser', table_name='users')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS employeetype;")
    op.execute("DROP TYPE IF EXISTS employeegroup;")
    # ### end Alembic commands ###
