"""Main FastAPI application entry point"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.routers import ai, allocations, chat, employees, health, projects

# Configure structured logging for readable console output
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Resource Wise API")

    # Create database tables
    await create_tables()

    yield

    logger.info("Shutting down Resource Wise API")


# Create FastAPI app
app = FastAPI(
    title="Resource Wise API",
    description="AI-Powered Resource Allocation System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(employees.router, prefix="/api/v1", tags=["employees"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(allocations.router, prefix="/api/v1", tags=["allocations"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Resource Wise API", "version": "0.1.0", "docs": "/docs"}
