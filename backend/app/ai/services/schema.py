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
                col_type = "ENUM(1, 2, 3, 4, 5)"
            elif "skillsource" in col_type.lower():
                col_type = "ENUM(PAT, manual, seed, self_assessment, manager_assessment)"
            elif "projecttype" in col_type.lower():
                col_type = "ENUM(customer, internal)"

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
            Hardcoded schema description
        """
        return """
        Table: users
        Columns:
            id (UUID, primary key)
            email (string, unique, not null)
            name (string, not null)
            is_active (boolean, default true)
            created_at (timestamp)
            updated_at (timestamp)

        Table: designations
        Columns:
            id (UUID, primary key)
            code (string, unique, not null)
            title (string, not null)
            level (integer)
            created_at (timestamp)
            updated_at (timestamp)

        Table: employees
        Columns:
            id (UUID, primary key)
            email (string, unique, not null)
            name (string, not null)
            designation_id (UUID, foreign key -> designations.id)
            capacity_percent (integer, default 100)
            onboarded_at (date)
            is_active (boolean, default true)
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            designation_ref -> Designation
            skills -> EmployeeSkill
            embeddings -> EmployeeEmbedding
            allocations -> Allocation

        Table: projects
        Columns:
            id (UUID, primary key)
            name (string, not null)
            description (text)
            status (enum: PLANNING, ACTIVE, ON_HOLD, COMPLETED, CANCELLED)
            type (enum: INTERNAL, CLIENT, RESEARCH)
            start_date (date)
            end_date (date)
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            allocations -> Allocation

        Table: allocations
        Columns:
            id (UUID, primary key)
            employee_id (UUID, foreign key -> employees.id)
            project_id (UUID, foreign key -> projects.id)
            percentage (enum: TWENTY_FIVE, FIFTY, SEVENTY_FIVE, HUNDRED)
            status (enum: PLANNED, ACTIVE, COMPLETED, CANCELLED)
            start_date (date, not null)
            end_date (date)
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee
            project -> Project

        Table: employee_skills
        Columns:
            id (UUID, primary key)
            employee_id (UUID, foreign key -> employees.id)
            skill_name (string, not null)
            summary (text)
            experience_months (integer, default 0)
            last_used (date)
            source (enum: PAT, MANUAL, INFERRED)
            proficiency_level (enum: BEGINNER, INTERMEDIATE, ADVANCED, EXPERT, MASTER)
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee

        Table: employee_embeddings
        Columns:
            employee_id (UUID, primary key, foreign key -> employees.id)
            source (string, primary key)
            summary (text, not null)
            embedding (vector[1536])
            created_at (timestamp)
            updated_at (timestamp)
        Relationships:
            employee -> Employee
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
