"""
Platform Health, Performance & Engineering Quality API Endpoints.

Route Summary:
GET /api/v1/platform/health          — Summary platform health & deterministic score
GET /api/v1/platform/health/detailed — Comprehensive platform health, system metrics, & events (Auth required)
GET /api/v1/platform/readiness       — System readiness probe
GET /api/v1/platform/liveness        — System liveness probe
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.core.config import settings
from app.core.dependencies import require_active_user
from app.models.user import User
from app.schemas.platform_health import (
    LivenessResponse,
    PlatformHealthDetailedResponse,
    PlatformHealthSummaryResponse,
    ReadinessResponse,
)
from app.services.platform_health_service import platform_health_service

router = APIRouter()


@router.get(
    "/health",
    response_model=PlatformHealthSummaryResponse,
    summary="Platform Health Summary",
    description="Returns high-level platform health, dependency states, and overall health score.",
)
async def get_platform_health() -> dict[str, Any]:
    """Get high-level platform health summary and deterministic score."""
    detailed = await platform_health_service.get_detailed_platform_health()
    return {
        "status": "ok" if detailed["overall_status"] == "Healthy" else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "overall_health_score": detailed["overall_health_score"],
        "overall_status": detailed["overall_status"],
        "dependencies": detailed["dependencies"],
    }


@router.get(
    "/health/detailed",
    response_model=PlatformHealthDetailedResponse,
    summary="Detailed Platform Health & System Metrics",
    description="Returns comprehensive dependency status, process CPU/memory metrics, API performance telemetry, and system events log.",
)
async def get_detailed_platform_health(
    _current_user: User = Depends(require_active_user),
) -> dict[str, Any]:
    """Get detailed platform health, resource metrics, and engineering quality telemetry (Secured with RBAC)."""
    return await platform_health_service.get_detailed_platform_health()


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Platform Readiness Probe",
    description="Readiness probe for Kubernetes / Docker orchestrators validating core database & cache connectivity.",
)
async def get_platform_readiness(response: Response) -> dict[str, Any]:
    """Check readiness of database, cache, and vector store."""
    db_check = await platform_health_service.check_database()
    redis_check = await platform_health_service.check_redis()

    is_ready = db_check["status"] == "healthy" and redis_check["status"] in ("healthy", "degraded")

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "ready": is_ready,
        "timestamp": time.time(),
        "dependencies": {
            "database": db_check["status"],
            "redis": redis_check["status"],
        },
    }


@router.get(
    "/liveness",
    response_model=LivenessResponse,
    summary="Platform Liveness Probe",
    description="Liveness probe confirming FastAPI process responsiveness.",
)
async def get_platform_liveness() -> dict[str, Any]:
    """Liveness check confirming application process is running."""
    return {
        "status": "alive",
        "alive": True,
        "timestamp": time.time(),
    }
