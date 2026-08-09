import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"telemuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Telemetry",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ingest_logs(client: AsyncClient):
    headers = await get_auth_headers(client)
    payload = {
        "source": "kubernetes-pod-1",
        "level": "ERROR",
        "message": "Connection timeout 504 on upstream database.",
        "service_name": "checkout-service",
    }
    response = await client.post("/api/v1/telemetry/logs", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["source"] == "kubernetes-pod-1"
    assert data["severity"] == "ERROR"
    assert data["event_type"] == "log_error"
    assert "metadata" in data
    assert data["metadata"]["is_error"] is True



@pytest.mark.asyncio
async def test_ingest_metrics_anomaly(client: AsyncClient):
    headers = await get_auth_headers(client)
    payload = {
        "resource_id": "i-0987654321",
        "metric_name": "system_cpu_usage_pct",
        "value": 98.5,
        "unit": "percent",
    }
    response = await client.post("/api/v1/telemetry/metrics", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["resource_id"] == "i-0987654321"
    assert data["value"] == 98.5


@pytest.mark.asyncio
async def test_ingest_traces_bottleneck(client: AsyncClient):
    headers = await get_auth_headers(client)
    payload = {
        "service_name": "api-gateway",
        "spans": [
            {"operation": "GET /users", "duration_ms": 150.0, "status": "OK"},
            {"operation": "db.users.find", "duration_ms": 650.0, "status": "TIMEOUT"},
        ],
    }
    response = await client.post("/api/v1/telemetry/traces", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[1]["duration"] == 650.0
    assert data[1]["status"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_get_telemetry_events(client: AsyncClient):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/telemetry/events?limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_telemetry_health(client: AsyncClient):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/telemetry/health", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "events_ingested_total" in data


@pytest.mark.asyncio
async def test_get_telemetry_ai_summary(client: AsyncClient):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/telemetry/ai-summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "root_cause_analysis" in data
    assert "recommended_mitigations" in data
    assert isinstance(data["impacted_services"], list)

