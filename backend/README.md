# Resource Wise Backend

AI-Powered Resource Allocation System backend built with FastAPI, PostgreSQL, and OpenAI.

## Architecture

```
backend/
├── app/
│   ├── core/           # Core configuration and database
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic models (request/response)
│   ├── services/       # Business logic layer
│   ├── repositories/   # Data access layer
│   ├── routers/        # API endpoints
│   ├── dependencies/   # Dependency injection
│   └── main.py         # FastAPI application entry point
├── alembic/            # Database migrations
├── tests/              # Test files
└── pyproject.toml      # Project dependencies
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Python SQL toolkit and ORM
- **PostgreSQL**: Database with pgvector extension for embeddings
- **Alembic**: Database migration tool
- **OpenAI**: AI embeddings and chat completions
- **Pydantic**: Data validation and serialization
- **Structlog**: Structured logging
- **uv**: Fast Python package installer and resolver

## Prerequisites

- Python 3.13+
- Docker & Docker Compose (for database)
- OpenAI API key (optional for development)

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies using uv
uv sync
```

### 2. Environment Configuration

Create `.env` file from template and edit with your values:

```bash
# Copy environment template
cp env.template .env
```

Edit `.env` file with your actual values:

```env
# Application Settings
APP_NAME=Resource Wise API
APP_VERSION=0.1.0
DEBUG=true

# Database Configuration (Docker setup)
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=admin
DB_NAME=resourcewise
DB_DRIVER=postgresql+asyncpg
DATABASE_ECHO=true

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Database Setup

#### **Option A: Using Docker (Recommended)**

```bash
# Start PostgreSQL with pgvector using Docker Compose
cd ../docker
docker-compose up -d

# Verify database is running
docker-compose logs postgres

# The database will be available at:
# Host: localhost, Port: 5432, User: admin, Password: admin, Database: resourcewise
```

#### **Option B: Local PostgreSQL Installation**

```bash
# Create PostgreSQL database
createdb resourcewise

# Enable required extensions (run as postgres superuser)
psql resourcewise -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql resourcewise -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

#### **Run Database Migrations**

```bash
# Apply all migrations to create tables
uv run alembic upgrade head

# Verify tables were created
psql -h localhost -p 5432 -U admin -d resourcewise -c "\dt"
```

### 4. Run the Application

```bash
# Development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### Main Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - AI chat interface
- `GET /api/v1/employees` - List employees
- `GET /api/v1/projects` - List projects
- `GET /api/v1/allocations` - List allocations

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration and database setup
│   │   ├── config.py   # Environment configuration
│   │   └── database.py # Database connection and session management
│   ├── models/         # SQLAlchemy database models
│   │   ├── base.py     # Base model with audit fields
│   │   ├── user.py     # User authentication model
│   │   ├── employee.py # Employee profiles
│   │   ├── project.py  # Project information
│   │   ├── allocation.py # Employee-project assignments
│   │   ├── skill.py    # Skills and embeddings
│   │   ├── designation.py # Employee roles/levels
│   │   └── enums.py    # Enum definitions
│   ├── routers/        # FastAPI route handlers
│   │   ├── health.py   # Health check endpoints
│   │   ├── employees.py # Employee management
│   │   ├── projects.py # Project management
│   │   ├── allocations.py # Allocation management
│   │   └── chat.py     # AI chat interface
│   └── main.py         # FastAPI application entry point
├── alembic/            # Database migration files
│   ├── versions/       # Migration scripts (timestamped)
│   └── env.py          # Alembic environment configuration
├── scripts/            # Utility scripts
│   └── seed_data.py    # Database seeding script
├── docker/             # Docker configuration
│   ├── docker-compose.yml # PostgreSQL with pgvector
│   └── init-db.sql     # Database initialization
├── pyproject.toml      # Project dependencies and configuration
├── alembic.ini         # Alembic configuration
└── env.template        # Environment variables template
```

## Database Models

### Core Models

- **User**: Authentication and audit tracking
- **Designation**: Employee roles and hierarchy levels
- **Employee**: User profiles with skills and capacity
- **Project**: Project details with requirements and tech stack
- **Allocation**: Employee-project assignments with percentages
- **EmployeeSkill**: Skills with proficiency levels and sources
- **EmployeeEmbedding**: Vector embeddings for AI-powered semantic search

### Key Features

- **Audit Trail**: All models include created_at, updated_at, deleted_at, and user tracking
- **Soft Delete**: Records are marked as deleted rather than physically removed
- **Vector Search**: pgvector integration for AI-powered skill matching
- **Full-text Search**: pg_trgm with GIN indexes for fast text search
- **Enums**: Type-safe status and proficiency level definitions

## Development

### Running Tests

```bash
uv run pytest
```

### Database Migrations with Alembic

Alembic is used for database schema versioning and migrations. All migration files use timestamp prefixes for better organization.

#### **Migration Workflow**

When you make changes to SQLAlchemy models, follow this process:

**1. Make Model Changes**
```python
# Example: Adding a new field to Employee model
# app/models/employee.py
class Employee(BaseModel):
    # ... existing fields ...
    phone_number: str = Field(max_length=20, nullable=True)  # NEW FIELD
    emergency_contact: str = Field(max_length=255, nullable=True)  # NEW FIELD
```

**2. Generate Migration**
```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "add_phone_and_emergency_contact_to_employee"

# Creates file: 20250612_1735_abc123_add_phone_and_emergency_contact_to_employee.py
```

**3. Review Generated Migration**
Always review the generated migration file before applying:
```python
def upgrade() -> None:
    op.add_column('employees', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact', sa.String(length=255), nullable=True))

def downgrade() -> None:
    op.drop_column('employees', 'emergency_contact')
    op.drop_column('employees', 'phone_number')
```

**4. Apply Migration**
```bash
# Apply all pending migrations
uv run alembic upgrade head

# Verify changes in database
psql -h localhost -p 5432 -U admin -d resourcewise -c "\d employees"
```

#### **Common Migration Commands**

```bash
# Check current migration status
uv run alembic current

# View migration history
uv run alembic history

# Apply specific migration
uv run alembic upgrade <revision_id>

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# Show SQL without executing
uv run alembic upgrade head --sql

# Create empty migration for manual changes
uv run alembic revision -m "manual_data_migration"
```

#### **Migration File Naming**

Migration files use timestamp prefixes:
```
20250612_1735_abc123def_add_phone_and_emergency_contact_to_employee.py
│        │     │       │
│        │     │       └── Description (slug)
│        │     └── Revision ID (auto-generated)
│        └── Time (17:35)
└── Date (2025-06-12)
```

#### **Best Practices**

- **Always review** generated migrations before applying
- **Test migrations** on development data first
- **Backup database** before major schema changes
- **Use descriptive names** for migration messages
- **Handle data migrations** manually when needed

#### **Example: Complex Migration**

For data transformations, create custom migrations:
```python
def upgrade() -> None:
    # Add new column
    op.add_column('employees', sa.Column('full_name', sa.String(500)))
    
    # Migrate existing data
    connection = op.get_bind()
    connection.execute(
        text("UPDATE employees SET full_name = first_name || ' ' || last_name")
    )
    
    # Drop old columns
    op.drop_column('employees', 'first_name')
    op.drop_column('employees', 'last_name')
```

#### **Troubleshooting**

**Migration Not Detected:**
```bash
# Ensure all models are imported in alembic/env.py
# Check that model changes are saved before generating migration
uv run alembic revision --autogenerate -m "description" --verbose
```

**Database Connection Issues:**
```bash
# Verify database is running
docker-compose -f ../docker/docker-compose.yml ps

# Test connection manually
psql -h localhost -p 5432 -U admin -d resourcewise -c "SELECT version();"
```

**Migration Conflicts:**
```bash
# If multiple developers create migrations simultaneously
uv run alembic merge -m "merge_migrations" <revision1> <revision2>
```

**Reset Database (Development Only):**
```bash
# Drop all tables and reapply migrations
uv run alembic downgrade base
uv run alembic upgrade head
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

## Production Deployment

### Environment Variables

Ensure all required environment variables are set:

```env
DEBUG=false
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=secure-db-password
DB_NAME=resourcewise
OPENAI_API_KEY=sk-...
ALLOWED_ORIGINS=https://yourdomain.com
```

### Docker Deployment

```bash
# Build image
docker build -t resource-wise-backend .

# Run container
docker run -p 8000:8000 --env-file .env resource-wise-backend
```

## Features

### AI-Powered Allocation

- OpenAI embeddings for skill matching
- Semantic search for employee-project matching
- Natural language project requirement parsing

### Database Features

- PostgreSQL with pgvector for embeddings
- Full-text search capabilities
- Optimized indexes for performance

### Security

- Input validation with Pydantic
- SQL injection protection
- CORS configuration

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

## API Documentation

Full API documentation is available at `/docs` when running the server.
