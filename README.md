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
- **Node.js** (v22+ required; enforced via `package.json` and `.npmrc`)
- **Python 3.13** (strictly required; managed via uv)
- **uv** (modern Python package manager - replaces pip, pyenv, virtualenv)

### Initial Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd resource-wise
   ```

2. **Install uv (if not already installed):**
   ```sh
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or via Homebrew
   brew install uv
   ```

3. **Frontend:**
   ```sh
   cd frontend
   # Install dependencies
   npm install
   # Copy environment variables
   cp .env.example .env
   ```

4. **Backend:**
   ```sh
   cd backend
   # Install Python 3.13 and dependencies (uv handles everything automatically)
   uv sync --dev
   # Copy environment variables
   cp .env.example .env
   ```

5. **Shared Config:**
   - Contains shared JSON data and OpenAPI schema.

## Development Tools

This project uses modern, high-performance tooling:

### Backend (Python)
- **📦 uv**: Ultra-fast package manager (10-100x faster than pip)
- **🦀 Ruff**: Ultra-fast linter and formatter (10-100x faster than Black + flake8)
- **🐍 Python 3.13**: Latest Python with enhanced performance

### Frontend (TypeScript/JavaScript)
- **🎨 Prettier**: Code formatter
- **🔍 ESLint**: Linter for code quality

## Pre-commit Hooks (Formatting & Linting)

This repo uses [Husky](https://typicode.github.io/husky/#/) to enforce code formatting and linting for both backend (Python) and frontend (TypeScript/JavaScript).

### Tools Used
- **Backend (Python):**
  - [Ruff](https://github.com/astral-sh/ruff) (ultra-fast linter + formatter + import sorter)
  
- **Frontend (TypeScript/JavaScript):**
  - [Prettier](https://prettier.io/) (formatter)
  - [ESLint](https://eslint.org/) (linter)

### Setup

#### 1. Install Dependencies
Run the following command to install required dependencies:
```sh
npm install
```

#### 2. Setup Husky (Git Hooks)
To ensure hooks are executable, run:
```sh
chmod +x .husky/pre-commit
chmod +x .husky/commit-msg
```

### What runs on commit?
- **Backend (Python):**
  - Ruff (linter with auto-fix)
  - Ruff (formatter)
  
- **Frontend (TypeScript/JavaScript):**
  - Prettier (formatter)
  - ESLint (linter)

## Quick Start Commands

### Backend
```sh
cd backend

# Run development server
uv run uvicorn main:app --reload

# Run linter
uv run ruff check .

# Run formatter  
uv run ruff format .

# Add new dependency
uv add fastapi-users

# Add dev dependency
uv add --dev pytest
```

### Frontend
```sh
cd frontend

# Run development server
npm run dev

# Run linter
npm run lint

# Run formatter
npm run prettier:apply
```

## Why Modern Tooling?

### uv Benefits:
- **⚡ 10-100x faster** package installation than pip
- **🔄 Automatic** Python version management
- **🔒 Lock files** for reproducible builds
- **🛠️ Unified** tool replacing pip, pyenv, virtualenv

### Ruff Benefits:
- **⚡ 10-100x faster** than Black + flake8 + isort combined
- **🦀 Written in Rust** for maximum performance
- **📏 800+ built-in rules** with zero configuration
- **🔧 Auto-fix** capabilities for most issues

