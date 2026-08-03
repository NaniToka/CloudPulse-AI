"""
CloudPulse AI — FastAPI application entry point.

Startup sequence
----------------
1. ``setup_logging()`` — configure structlog before anything else logs.
2. FastAPI app is instantiated with metadata and response class.
3. Middleware is registered (order matters for CORS + GZip).
4. Global exception handlers are registered.
5. API routers are mounted under ``/api/v1``.
6. ``/health`` route is added.
7. ``lifespan`` context manager handles DB table creation on startup and
   engine disposal on shutdown.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from app.api.errors import register_exception_handlers
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine

# Configure logging as the very first action so all subsequent imports
# that obtain loggers receive a properly configured instance.
setup_logging()

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events.

    Startup: ensure all tables exist (create_all is idempotent and safe in dev;
             in production, Alembic migrations should be run separately).
    Shutdown: dispose the async engine connection pool cleanly.
    """
    from app.db.base import Base  # noqa: PLC0415 — deferred to avoid circular imports

    log.info("startup", app=settings.APP_NAME, env=settings.APP_ENV)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("database_ready")

    yield

    await engine.dispose()
    log.info("shutdown")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Premium enterprise infrastructure observability platform powered by AI. "
        "Authenticate with a Bearer JWT token obtained from POST /api/v1/auth/login."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware  (registration order = outermost → innermost execution)
# ---------------------------------------------------------------------------

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],   # allow browser to read SSE session header
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# System routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"], summary="Health check")
async def health_check() -> dict:
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
    }
