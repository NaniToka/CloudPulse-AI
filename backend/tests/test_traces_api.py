"""
API tests for Distributed Tracing Platform (/api/v1/traces and /api/v1/services).
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"traceuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Trace",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_traces(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/traces", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_get_trace_by_id(client: AsyncClient):
    headers = await get_auth_headers(client)

    list_resp = await client.get("/api/v1/traces", headers=headers)
    trace_id = list_resp.json()["items"][0]["trace_id"]

    response = await client.get(f"/api/v1/traces/{trace_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["trace_id"] == trace_id
    assert "spans" in data
    assert len(data["spans"]) > 0


@pytest.mark.asyncio
async def test_analyze_trace(client: AsyncClient):
    headers = await get_auth_headers(client)

    list_resp = await client.get("/api/v1/traces", headers=headers)
    trace_id = list_resp.json()["items"][0]["trace_id"]

    response = await client.post(f"/api/v1/traces/{trace_id}/analyze", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["trace_id"] == trace_id
    assert "bottleneck_detected" in data
    assert "slowest_service" in data
    assert "optimization_suggestions" in data


@pytest.mark.asyncio
async def test_get_service_map(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/services/map", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0


@pytest.mark.asyncio
async def test_get_service_metrics(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/services/api-gateway/metrics", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["service_name"] == "api-gateway"
    assert "avg_latency_ms" in data
    assert "requests_per_second" in data
