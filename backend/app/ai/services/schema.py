"""Database schema service for AI query generation."""

from typing import Any

import structlog
from app.models import (
    Allocation,
    Designation,
    Employee,
    EmployeeEmbedding,
    EmployeeSkill,
    Project,
    User,
)

logger = structlog.get_logger()


class DatabaseSchemaService:
    """Service for retrieving database schema information."""

    def __init__(self):
        """Initialize the schema service."""
        self.models = [
            User,
            Designation,
            Employee,
            Project,
            Allocation,
            EmployeeSkill,
            EmployeeEmbedding,
        ]

    async def get_schema_description(self) -> str:
        """Get a human-readable description of the database schema.

        Returns:
            String containing the database schema description
        """
        try:
            schema_parts = []

            for model in self.models:
                table_info = self._get_table_info(model)
                schema_parts.append(table_info)

            return "\n\n".join(schema_parts)

        except Exception as e:
            logger.error("Error retrieving database schema", error=str(e))
            # Fallback to basic schema if dynamic retrieval fails
            return self._get_fallback_schema()

    def _get_table_info(self, model: Any) -> str:
        """Get table information for a SQLAlchemy model.

        Args:
            model: SQLAlchemy model class

        Returns:
            String describing the table structure
        """
        table_name = model.__tablename__
        columns = []
        relationships = []

        # Get column information
        for column in model.__table__.columns:
            column_info = self._format_column_info(column)
            columns.append(column_info)

        # Get relationship information
        if hasattr(model, "__mapper__"):
            for rel_name, relationship in model.__mapper__.relationships.items():
                rel_info = f"    {rel_name} -> {relationship.mapper.class_.__name__}"
                relationships.append(rel_info)

        # Format table description
        table_desc = f"Table: {table_name}\nColumns:"
        for col in columns:
            table_desc += f"\n    {col}"

        if relationships:
            table_desc += "\nRelationships:"
            for rel in relationships:
                table_desc += f"\n{rel}"

        return table_desc

    def _format_column_info(self, column) -> str:
        """Format column information for schema description.

        Args:
            column: SQLAlchemy column object

        Returns:
            Formatted column description
        """
        col_type = str(column.type)
        col_name = column.name

        # Handle enum types with specific values
        if hasattr(column.type, "enums") and column.type.enums:
            enum_values = ", ".join(column.type.enums)
            col_type = f"ENUM({enum_values})"
        elif "enum" in col_type.lower():
            # Try to extract enum class name and get values
            if "projectstatus" in col_type.lower():
                col_type = "ENUM(planning, active, on_hold, completed, cancelled)"
            elif "allocationstatus" in col_type.lower():
                col_type = "ENUM(active, completed, cancelled)"
            elif "allocationpercentage" in col_type.lower():
                col_type = "ENUM(25, 50, 75, 100)"
            elif "skillproficiencylevel" in col_type.lower():
                col_type = "ENUM(BEGINNER, NOVICE, INTERMEDIATE, ADVANCED, EXPERT)"
            elif "skillsource" in col_type.lower():
                col_type = "ENUM(PAT, MANUAL, SEED, SELF_ASSESSMENT, MANAGER_ASSESSMENT)"
            elif "projecttype" in col_type.lower():
                col_type = "ENUM(customer, internal)"
            elif "employeegroup" in col_type.lower():
                col_type = "ENUM(KD_INDIA, KD_US, DEV_PARTNER, INDEPENDENT)"
            elif "employeetype" in col_type.lower():
                col_type = "ENUM(FULL_TIME, CONTRACTOR, CONSULTANT, INTERN)"

        # Add constraints information
        constraints = []
        if column.primary_key:
            constraints.append("primary key")
        if column.foreign_keys:
            fk = list(column.foreign_keys)[0]
            constraints.append(f"foreign key -> {fk.column}")
        if not column.nullable:
            constraints.append("not null")
        if column.unique:
            constraints.append("unique")
        if column.index:
            constraints.append("indexed")

        constraint_str = f" ({', '.join(constraints)})" if constraints else ""

        return f"{col_name} ({col_type}){constraint_str}"

    def _get_fallback_schema(self) -> str:
        """Get fallback schema description if dynamic retrieval fails.

        Returns:
            Hardcoded schema description with all business fields
        """
        return """
        Table: users
        Columns:
            id (UUID, primary key)
            email (string, unique, not null)
            username (string, unique, not null)
            full_name (string)
            bio (text)
            is_active (boolean, default true)
            is_superuser (boolean, default false)
            created_at (timestamp)
            updated_at (timestamp)

        Table: designations
        Columns:
            id (UUID, primary key)
            code (string, unique, not null) -- Short codes like 'SSE', 'TL', 'PM', 'SDE'
            title (string, not null) -- Full titles like 'Senior Software Engineer', 'Technical Lead'
            level (integer) -- Hierarchy level 1-5
            is_leadership (boolean, default false)
            is_active (boolean, default true)
            created_at (timestamp)
            updated_at (timestamp)

        Table: employees
        Columns:
            id (UUID, primary key)
            email (string, unique, not null)
            name (string, not null)
            designation_id (UUID, foreign key -> designations.id)
            capacity_percent (integer, default 100) -- e.g. 100, 70, 50
            onboarded_at (date)
            is_active (boolean, default true)
            employee_group (ENUM: KD_INDIA, KD_US, DEV_PARTNER, INDEPENDENT) -- Organization group
            organization (string) -- Company/partner name like 'Kickdrum India', 'TechPartner Solutions'
            employee_type (ENUM: FULL_TIME, CONTRACTOR, CONSULTANT, INTERN) -- Employment type
            location (string) -- Work location like 'Bangalore', 'New York', 'Remote'
            cost_per_hour (decimal) -- Internal hourly cost rate
            billing_rate (decimal) -- Client billing rate per hour
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            designation_ref -> Designation
            skills -> EmployeeSkill
            embeddings -> EmployeeEmbedding
            allocations -> Allocation
            managed_projects -> Project (as project manager)

        Table: projects
        Columns:
            id (UUID, primary key)
            name (string, not null)
            description (text)
            duration_months (integer)
            tech_stack (array of strings) -- Technologies used
            project_type (ENUM: customer, internal)
            status (ENUM: planning, active, on_hold, completed, cancelled)
            customer_name (string) -- Client/customer name
            project_cost (decimal) -- Total project cost
            monthly_cost (decimal) -- Monthly project cost
            start_date (date) -- Project start date
            end_date (date) -- Project end date
            project_manager_id (UUID, foreign key -> employees.id) -- Project manager
            required_roles (array of strings) -- Required job roles
            required_skills (array of strings) -- Required technical skills
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            allocations -> Allocation
            project_manager -> Employee

        Table: allocations
        Columns:
            id (UUID, primary key)
            employee_id (UUID, foreign key -> employees.id)
            project_id (UUID, foreign key -> projects.id)
            percent_allocated (integer) -- Percentage like 25, 50, 75, 100
            start_date (date, not null)
            end_date (date, not null)
            status (ENUM: active, completed, cancelled)
            hourly_rate (decimal) -- Hourly rate for this specific allocation
            monthly_cost (decimal) -- Monthly cost for this allocation
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee
            project -> Project

        Table: employee_skills
        Columns:
            id (UUID, primary key)
            employee_id (UUID, foreign key -> employees.id)
            skill_name (string, not null) -- Technical skill like 'React', 'Java', 'AWS'
            summary (text) -- Description of experience
            experience_months (integer, default 0) -- Months of experience
            last_used (date) -- When last used this skill
            source (ENUM: PAT, MANUAL, SEED, SELF_ASSESSMENT, MANAGER_ASSESSMENT)
            proficiency_level (ENUM: BEGINNER, NOVICE, INTERMEDIATE, ADVANCED, EXPERT)
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee

        Table: employee_embeddings
        Columns:
            employee_id (UUID, primary key, foreign key -> employees.id)
            source (string, primary key) -- Source like 'skills', 'projects', 'profile'
            summary (text, not null) -- Text that was embedded
            embedding (vector[1536]) -- OpenAI embedding vector
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee

        IMPORTANT BUSINESS FIELD USAGE:
        
        1. EMPLOYEE ORGANIZATION QUERIES:
           - employee_group: Filter by 'KD_INDIA', 'KD_US', 'DEV_PARTNER', 'INDEPENDENT'
           - organization: Filter by company names like 'Kickdrum India', 'TechPartner Solutions'
           - location: Filter by work locations like 'Bangalore', 'New York', 'Remote'
           - employee_type: Filter by 'FULL_TIME', 'CONTRACTOR', 'CONSULTANT', 'INTERN'
        
        2. FINANCIAL QUERIES:
           - cost_per_hour: Employee's standard internal cost rate
           - billing_rate: Employee's standard client billing rate
           - hourly_rate (allocations): Project-specific hourly rate (may differ from employee base rate)
           - monthly_cost (allocations): Calculated monthly cost for specific allocation
           - project_cost: Total cost of entire project
           - monthly_cost (projects): Monthly cost of entire project
        
        3. PROJECT MANAGEMENT QUERIES:
           - customer_name: Client/customer name for projects
           - project_manager_id: Employee who manages the project
           - start_date/end_date: Project timeline dates
        
        EXAMPLE BUSINESS QUERIES:
        - "Show me KD India employees" → WHERE employee_group = 'KD_INDIA'
        - "Find contractors in Bangalore" → WHERE employee_type = 'CONTRACTOR' AND location = 'Bangalore'
        - "What's the total cost of Mobile Banking App?" → SELECT project_cost FROM projects WHERE name = 'Mobile Banking App'
        - "Show monthly costs by organization" → GROUP BY employee_group, SUM(monthly_cost)
        - "Who manages the Healthcare project?" → JOIN projects p, employees e WHERE p.project_manager_id = e.id
        """

    async def get_table_names(self) -> list[str]:
        """Get list of all table names.

        Returns:
            List of table names
        """
        return [model.__tablename__ for model in self.models]

    async def get_table_columns(self, table_name: str) -> list[str]:
        """Get column names for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            List of column names
        """
        for model in self.models:
            if model.__tablename__ == table_name:
                return [column.name for column in model.__table__.columns]
        return []
