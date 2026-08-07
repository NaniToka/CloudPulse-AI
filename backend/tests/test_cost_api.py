"""
API tests for Cost Optimizer endpoints (/api/v1/cost).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"costuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Cost",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_cost_overview(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/cost/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "monthly_cost" in data
    assert "projected_cost" in data
    assert "efficiency_score" in data
    assert "daily_trend" in data
    assert "service_breakdown" in data
    assert "region_breakdown" in data
    assert data["monthly_cost"] > 0


@pytest.mark.asyncio
async def test_get_cost_services(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/cost/services", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "services" in data
    assert "total_cost" in data
    assert len(data["services"]) > 0


@pytest.mark.asyncio
async def test_get_cost_recommendations(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/cost/recommendations", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total_savings" in data
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_analyze_cost(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.post("/api/v1/cost/analyze", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "cost_summary" in data
    assert "highest_cost_services" in data
    assert "estimated_monthly_savings" in data
    assert "efficiency_score" in data


@pytest.mark.asyncio
async def test_get_cost_resources(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/cost/resources", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
