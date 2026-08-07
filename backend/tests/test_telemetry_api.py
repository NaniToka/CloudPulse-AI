"""
Unit tests for Unified Telemetry Intelligence Platform API.
"""
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_logs(async_client: AsyncClient, token_headers: dict[str, str]):
    payload = {
        "source": "kubernetes-pod-1",
        "level": "ERROR",
        "message": "Connection timeout 504 on upstream database.",
        "service_name": "checkout-service"
    }
    response = await async_client.post("/api/v1/telemetry/logs", json=payload, headers=token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["source"] == "kubernetes-pod-1"
    assert data["severity"] == "ERROR"
    assert data["event_type"] == "log_error"
    assert "metadata_" in data
    assert data["metadata_"]["is_error"] is True


@pytest.mark.asyncio
async def test_ingest_metrics_anomaly(async_client: AsyncClient, token_headers: dict[str, str]):
    payload = {
        "resource_id": "i-0987654321",
        "metric_name": "system_cpu_usage_pct",
        "value": 98.5,
        "unit": "percent"
    }
    response = await async_client.post("/api/v1/telemetry/metrics", json=payload, headers=token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["resource_id"] == "i-0987654321"
    assert data["value"] == 98.5


@pytest.mark.asyncio
async def test_ingest_traces_bottleneck(async_client: AsyncClient, token_headers: dict[str, str]):
    payload = {
        "service_name": "api-gateway",
        "spans": [
            {"operation": "GET /users", "duration_ms": 150.0, "status": "OK"},
            {"operation": "db.users.find", "duration_ms": 650.0, "status": "TIMEOUT"}
        ]
    }
    response = await async_client.post("/api/v1/telemetry/traces", json=payload, headers=token_headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[1]["duration"] == 650.0
    assert data[1]["status"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_get_telemetry_events(async_client: AsyncClient, token_headers: dict[str, str]):
    response = await async_client.get("/api/v1/telemetry/events?limit=10", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_telemetry_health(async_client: AsyncClient, token_headers: dict[str, str]):
    response = await async_client.get("/api/v1/telemetry/health", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "events_ingested_total" in data


@pytest.mark.asyncio
async def test_get_telemetry_ai_summary(async_client: AsyncClient, token_headers: dict[str, str]):
    response = await async_client.get("/api/v1/telemetry/ai-summary", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "root_cause_analysis" in data
    assert "recommended_mitigations" in data
    assert isinstance(data["impacted_services"], list)
