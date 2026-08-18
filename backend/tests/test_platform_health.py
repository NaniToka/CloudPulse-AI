"""
Tests for Platform Health, Engineering Quality & System Readiness API endpoints.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.platform_health_service import platform_health_service


async def register_user_headers(client: AsyncClient) -> dict[str, str]:
    """Helper to register a unique user and return Bearer auth headers."""
    payload = {
        "email": f"health-user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "Password123!",
        "first_name": "Health",
        "last_name": "Auditor",
        "organization_name": "Health Corp",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_platform_health_summary(client: AsyncClient) -> None:
    """Test GET /api/v1/platform/health returns valid summary and score."""
    response = await client.get("/api/v1/platform/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "overall_health_score" in data
    assert 0 <= data["overall_health_score"] <= 100
    assert "dependencies" in data
    assert "database" in data["dependencies"]
    assert "redis" in data["dependencies"]


@pytest.mark.asyncio
async def test_platform_health_detailed_unauthenticated(client: AsyncClient) -> None:
    """Test GET /api/v1/platform/health/detailed requires authentication (403/401)."""
    response = await client.get("/api/v1/platform/health/detailed")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_platform_health_detailed_authenticated(client: AsyncClient) -> None:
    """Test GET /api/v1/platform/health/detailed returns detailed system metrics and performance."""
    headers = await register_user_headers(client)
    response = await client.get(
        "/api/v1/platform/health/detailed",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_health_score" in data
    assert "dependencies" in data
    assert "system_metrics" in data
    assert "api_performance" in data
    assert "system_events" in data
    assert "environment_info" in data

    metrics = data["system_metrics"]
    assert "cpu_usage_pct" in metrics
    assert "process_memory_mb" in metrics
    assert "total_requests" in metrics

    env = data["environment_info"]
    assert "environment" in env
    assert "ai_mode_label" in env


@pytest.mark.asyncio
async def test_platform_readiness(client: AsyncClient) -> None:
    """Test GET /api/v1/platform/readiness returns ready probe."""
    response = await client.get("/api/v1/platform/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["ready"] is True
    assert "database" in data["dependencies"]


@pytest.mark.asyncio
async def test_platform_liveness(client: AsyncClient) -> None:
    """Test GET /api/v1/platform/liveness returns alive probe."""
    response = await client.get("/api/v1/platform/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert data["alive"] is True


@pytest.mark.asyncio
async def test_request_correlation_headers(client: AsyncClient) -> None:
    """Test that X-Request-ID and X-Correlation-ID are attached to response headers."""
    response = await client.get("/api/v1/platform/liveness")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-correlation-id" in response.headers


@pytest.mark.asyncio
async def test_platform_health_service_database_failure() -> None:
    """Test platform health scoring when database check fails."""
    unhealthy_db = {
        "status": "unhealthy",
        "latency_ms": 12.5,
        "last_checked": "2026-08-18T22:50:00Z",
        "message": "PostgreSQL database connection error",
    }
    with patch.object(
        platform_health_service, "check_database", new_callable=AsyncMock
    ) as mock_db:
        mock_db.return_value = unhealthy_db
        result = await platform_health_service.get_detailed_platform_health()
        assert result["dependencies"]["database"]["status"] == "unhealthy"
        assert result["overall_health_score"] < 100
