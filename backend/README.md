# Backend (FastAPI)

This is the backend for the Resource Wise AI-powered resource allocation system.

## Getting Started

1. **Set up a Python virtual environment (recommended):**
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install Poetry (if not already installed):**
   ```sh
   curl -sSL https://install.python-poetry.org | python3 -
   # or follow instructions at https://python-poetry.org/docs/#installation
   ```
3. **Install dependencies:**
   ```sh
   poetry install
   ```
4. **Copy environment variables:**
   ```sh
   cp .env.example .env
   ```
5. **Run the FastAPI server:**
   ```sh
   poetry run uvicorn main:app --reload
   ```

## Structure
- `main.py` – FastAPI entrypoint
- `routers/` – API route modules
- `models/` – Database models (ORM or Pydantic)
- `schemas/` – Pydantic schemas
- `shared/` – Shared utilities

## API Docs
- OpenAPI/Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

*This is a placeholder README. Update as the project evolves.*
