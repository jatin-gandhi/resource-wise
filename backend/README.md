# Backend (FastAPI)

This is the backend for the Resource Wise AI-powered resource allocation system.

## Getting Started

1. (Recommended) Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies (skip for now):
   ```sh
   pip install -r requirements.txt
   # or
   poetry install
   ```
3. Copy environment variables:
   ```sh
   cp .env.example .env
   ```
4. Run the FastAPI server:
   ```sh
   uvicorn main:app --reload
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
