# Resource Wise: AI-Powered Resource Allocation System

## Overview
Resource Wise is a mono-repo for an AI-powered resource allocation system designed for rapid prototyping and extensibility. It is structured for a 3-day hackathon, with a clean separation between frontend, backend, and shared configuration/data.

## Architecture

- **frontend/**: Next.js (React + TypeScript) app for the user interface.
- **backend/**: FastAPI (Python) app for API and business logic.
- **shared-config/**: Shared JSON data and OpenAPI schema for use by both frontend and backend.

## Folder Structure

```
frontend/        # Next.js app (React + TypeScript)
backend/         # FastAPI app (Python)
shared-config/   # Shared JSON data and OpenAPI spec
```

## Setup Instructions

### Prerequisites
- Node.js (v22+ required; enforced via `package.json` and `.npmrc`)
- Python 3.11+ (required; enforced via Poetry)
- (Optional) Poetry for Python dependency management

### Initial Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd resource-wise
   ```

2. **Frontend:**
   ```sh
   cd frontend
   # Install dependencies (skip for now)
   # npm install
   # Copy environment variables
   cp .env.example .env
   ```

3. **Backend:**
   ```sh
   cd backend
   # Install dependencies (skip for now)
   # pip install -r requirements.txt
   # or
   # poetry install
   # Copy environment variables
   cp .env.example .env
   ```

4. **Shared Config:**
   - Contains shared JSON data and OpenAPI schema.

## Pre-commit Hooks (Formatting & Linting)

This repo uses [pre-commit](https://pre-commit.com/) to enforce code formatting and linting for both backend (Python) and frontend (TypeScript/JavaScript).

### Setup

1. **Install pre-commit** (if not already):
   ```sh
   pip install pre-commit
   # or with Poetry (in backend):
   poetry add --group dev pre-commit
   ```
2. **Install the git hooks:**
   ```sh
   pre-commit install
   ```
3. **Run all hooks manually (optional):**
   ```sh
   pre-commit run --all-files
   ```

### What runs on commit?
- **Backend (Python):**
  - [Black](https://github.com/psf/black) (formatter)
  - [Flake8](https://github.com/pycqa/flake8) (linter)
- **Frontend (TypeScript/JavaScript):**
  - [Prettier](https://prettier.io/) (formatter)
  - [ESLint](https://eslint.org/) (linter)

Prettier and ESLint will respect configuration files in the `frontend/` directory.

## Contributing
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
- PRs and issues welcome!

---

*This project is scaffolded for a hackathon and is intended for rapid prototyping and extension.*
