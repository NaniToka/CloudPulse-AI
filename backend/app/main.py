"""
CloudPulse AI — FastAPI application entry point.

Startup sequence
----------------
1. ``setup_logging()`` — configure structlog before anything else logs.
2. FastAPI app is instantiated with metadata and response class.
3. Middleware is registered (Correlation ID, Security Headers, Rate Limiting, CORS, GZip).
4. Global exception handlers are registered.
5. API routers are mounted under ``/api/v1``.
6. System routes: ``/health`` (Liveness), ``/ready`` (Readiness), ``/metrics`` (Prometheus).
7. ``lifespan`` context manager handles DB table creation on startup and
   engine disposal on shutdown.
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
from sqlalchemy import text

from app.api.errors import register_exception_handlers
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import (
    CorrelationIdMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.session import engine
from app.services.cache_service import cache_service
from app.services.metrics_collector import metrics_collector

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

    # Seed initial development user & baseline data
    from app.db.init_db import init_db  # noqa: PLC0415
    from app.db.session import AsyncSessionLocal  # noqa: PLC0415

    async with AsyncSessionLocal() as session:
        try:
            await init_db(session)
        except Exception as exc:
            log.warning("init_db_seeding_skipped", error=str(exc))

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
# Middleware (Outer to Inner)
# ---------------------------------------------------------------------------

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id", "X-Correlation-ID", "X-Request-ID", "traceparent"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=300)


@app.middleware("http")
async def track_request_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    metrics_collector.record_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_sec=duration,
    )
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# System & Observability Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["System"], summary="Liveness & Health Probe")
@app.get("/api/health", tags=["System"], summary="API Liveness Probe", include_in_schema=False)
@app.get("/api/v1/health", tags=["System"], summary="API v1 Liveness Probe", include_in_schema=False)
async def health_check() -> dict:
    """Enterprise structured health check reporting overall and dependency health."""
    db_status = "healthy"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    redis_status = "healthy"
    try:
        redis_ok = await cache_service.ping()
        if not redis_ok:
            redis_status = "in-memory-fallback"
    except Exception:
        redis_status = "in-memory-fallback"

    ai_provider = (
        "gemini-cloud-ai"
        if (settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in ("your_key_here", "your_gemini_api_key_here", ""))
        else "local-deterministic-engine"
    )

    is_healthy = db_status == "healthy"

    return {
        "status": "ok" if is_healthy else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "dependencies": {
            "database": db_status,
            "redis": redis_status,
            "ai": ai_provider,
        },
    }


@app.get("/version", tags=["System"], summary="Service Version")
@app.get("/api/v1/version", tags=["System"], summary="API v1 Version")
async def version_info() -> dict:
    """Returns semantic version and environment build metadata."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "api_version": "v1",
    }


@app.get("/ready", tags=["System"], summary="Readiness Probe")
async def readiness_check(response: Response) -> dict:
    """Kubernetes readiness probe — validates database and Redis connectivity."""
    db_ok = False
    redis_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        log.error("readiness_db_failed", error=str(e))

    try:
        redis_ok = await cache_service.ping()
    except Exception as e:
        log.error("readiness_redis_failed", error=str(e))

    # In local development, in-memory cache is active as a clean fallback
    is_ready = db_ok and (redis_ok or settings.APP_ENV == "development")
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "degraded",
        "database": "connected" if db_ok else "unhealthy",
        "redis": "connected" if redis_ok else ("in-memory-fallback" if settings.APP_ENV == "development" else "unhealthy"),
        "timestamp": time.time(),
    }


@app.get("/metrics", tags=["System"], summary="Prometheus Metrics")
async def prometheus_metrics() -> PlainTextResponse:
    """Prometheus exposition metrics endpoint for scraper scraping."""
    content = metrics_collector.render_prometheus()
    return PlainTextResponse(content=content, media_type="text/plain; version=0.0.4")
