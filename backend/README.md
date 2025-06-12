# Backend (FastAPI)

This is the backend for the Resource Wise AI-powered resource allocation system, built with FastAPI and modern Python tooling.

## Requirements

- **Python 3.13** (strictly required)
- **uv** (package manager and Python version manager)

## Getting Started

### 1. Install uv (if not already installed)
```sh
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via Homebrew
brew install uv
```

### 2. Set up the project
```sh
# Navigate to backend directory
cd backend

# Install Python 3.13 and create virtual environment (uv handles this automatically)
uv sync --dev

# Copy environment variables (if .env.example exists)
cp .env.example .env
```

### 3. Run the FastAPI server
```sh
# Development server with auto-reload
uv run uvicorn main:app --reload

# Or specify host and port
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Development Tools

This project uses modern Python tooling for enhanced developer experience:

### 📦 Package Management: **uv**
- **10-100x faster** than pip
- Automatic Python version management
- Lock file for reproducible builds (`uv.lock`)
- Replaces pip, pyenv, and virtualenv

### 🦀 Code Quality: **Ruff**
- **Ultra-fast** linter and formatter (written in Rust)
- Replaces Black, flake8, isort, and more
- **10-100x faster** than traditional tools
- Configured for 100-character line length

### Common Commands
```sh
# Install new dependency
uv add fastapi-users

# Install new dev dependency  
uv add --dev pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run linter with auto-fix
uv run ruff check --fix .

# Update dependencies
uv sync --upgrade

# Show outdated packages
uv tree --outdated
```

## Project Structure
```
backend/
├── main.py              # FastAPI entrypoint
├── routers/             # API route modules
├── models/              # Database models (ORM or Pydantic)
├── schemas/             # Pydantic schemas
├── shared/              # Shared utilities
├── pyproject.toml       # Project configuration & dependencies
├── uv.lock             # Lock file for reproducible builds
└── README.md           # This file
```

## API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Code Quality & Pre-commit

This project uses pre-commit hooks to ensure code quality:

```sh
# Install pre-commit hooks (if using)
uv run pre-commit install

# Run pre-commit manually
uv run pre-commit run --all-files
```

The pre-commit hooks automatically:
- ✅ Lint code with Ruff
- ✅ Format code with Ruff  
- ✅ Sort imports
- ✅ Check for common issues

## Why uv + Ruff?

### uv Benefits:
- **Speed**: 10-100x faster package installation
- **Simplicity**: One tool replaces pip, pyenv, virtualenv
- **Reliability**: Lock files ensure reproducible builds
- **Modern**: Built for the future of Python development

### Ruff Benefits:
- **Performance**: 10-100x faster than Black + flake8 + isort
- **Comprehensive**: 800+ built-in rules
- **Unified**: One tool for linting, formatting, and import sorting
- **Compatible**: Drop-in replacement for existing tools

---

*Built with ❤️ using FastAPI, uv, and Ruff*
