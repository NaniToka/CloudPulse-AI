"""
API tests for Real-Time Observability Platform (/api/v1/metrics).
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"metricuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Metric",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_current_metrics(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/metrics/current", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "current" in data
    assert data["is_live"] is True
    assert "cpu_usage" in data["current"]
    assert "memory_usage" in data["current"]
    assert "network_traffic_mbps" in data["current"]
    assert "k8s_pods" in data["current"]


@pytest.mark.asyncio
async def test_get_metrics_history(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/metrics/history?limit=50", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "history" in data
    assert "total_points" in data
    assert len(data["history"]) > 0
