"""
API tests for AI Predictive Incident Detection Engine (/api/v1/predictions).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"preduser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Predict",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_predictions(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/predictions", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_get_prediction_stats(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/predictions/stats", headers=headers)
    assert response.status_code == 200, response.text
    stats = response.json()

    assert "predicted_failures" in stats
    assert "high_risk_services" in stats
    assert "avg_confidence_percent" in stats
    assert "prevented_downtime_hours" in stats


@pytest.mark.asyncio
async def test_get_risk_heatmap(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/predictions/heatmap", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "items" in data
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_trigger_predictive_analysis(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {
        "services": ["auth-service"],
        "lookback_hours": 24,
    }

    response = await client.post("/api/v1/predictions/analyze", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    pred = response.json()

    assert "id" in pred
    assert pred["service"] == "auth-service"
    assert "failure_probability" in pred
    assert "ai_explanation" in pred
    assert "ai_metrics_of_concern" in pred


@pytest.mark.asyncio
async def test_get_prediction_by_id_and_update_status(client: AsyncClient):
    headers = await get_auth_headers(client)

    # List first
    list_resp = await client.get("/api/v1/predictions", headers=headers)
    pred_id = list_resp.json()["items"][0]["id"]

    # GET single
    get_resp = await client.get(f"/api/v1/predictions/{pred_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == pred_id

    # PATCH status
    patch_resp = await client.patch(
        f"/api/v1/predictions/{pred_id}/status",
        json={"status": "Mitigated"},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "Mitigated"
