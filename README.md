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
- Node.js (v18+ recommended)
- Python 3.9+
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

## Contributing
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
- PRs and issues welcome!

---

*This project is scaffolded for a hackathon and is intended for rapid prototyping and extension.*
