"""
API tests for Autonomous AIOps Agent (/api/v1/aiops).
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"aiopsuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "AIOps",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_aiops_agent_status(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/aiops/status", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "agent_name" in data
    assert "status" in data
    assert "current_phase" in data
    assert data["health_status"] == "Healthy"


@pytest.mark.asyncio
async def test_trigger_and_list_recommendations(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Trigger Agent Loop
    analyze_payload = {"target_system": "Metrics"}
    response = await client.post("/api/v1/aiops/analyze", json=analyze_payload, headers=headers)
    assert response.status_code == 201, response.text
    rec = response.json()

    assert "id" in rec
    assert rec["title"] is not None
    assert rec["confidence_score"] > 0.0

    # List Recommendations
    list_resp = await client.get("/api/v1/aiops/recommendations", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    ldata = list_resp.json()
    assert "items" in ldata
    assert ldata["total"] > 0


@pytest.mark.asyncio
async def test_approve_and_history(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Get Pending Recommendation
    list_resp = await client.get("/api/v1/aiops/recommendations", headers=headers)
    rec_id = list_resp.json()["items"][0]["id"]

    # Approve Action
    approve_payload = {
        "recommendation_id": rec_id,
        "approved_by": "Lead AIOps Controller",
        "action": "Approve",
    }
    app_resp = await client.post("/api/v1/aiops/approve", json=approve_payload, headers=headers)
    assert app_resp.status_code == 200, app_resp.text
    assert app_resp.json()["status"] == "Executed"

    # Get Execution History
    hist_resp = await client.get("/api/v1/aiops/history", headers=headers)
    assert hist_resp.status_code == 200, hist_resp.text
    hdata = hist_resp.json()
    assert "total_executions" in hdata
    assert hdata["total_executions"] > 0
