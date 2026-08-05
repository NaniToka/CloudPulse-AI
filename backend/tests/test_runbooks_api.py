"""
API tests for Auto Remediation Center & Runbook Generator (/api/v1/runbooks).
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"rbuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Runbook",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_runbooks(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/runbooks", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_generate_and_get_runbook(client: AsyncClient):
    headers = await get_auth_headers(client)

    gen_payload = {
        "service_name": "auth-service",
        "severity": "P0",
        "title": "Test Auto Remediation Runbook",
    }

    response = await client.post("/api/v1/runbooks/generate", json=gen_payload, headers=headers)
    assert response.status_code == 201, response.text
    rb = response.json()

    assert "id" in rb
    assert rb["service_name"] == "auth-service"
    assert rb["severity"] == "P0"
    assert len(rb["steps"]) > 0

    # GET by ID
    rb_id = rb["id"]
    get_resp = await client.get(f"/api/v1/runbooks/{rb_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rb_id


@pytest.mark.asyncio
async def test_approve_and_execute_runbook(client: AsyncClient):
    headers = await get_auth_headers(client)

    list_resp = await client.get("/api/v1/runbooks", headers=headers)
    rb_id = list_resp.json()["items"][0]["id"]

    # Approve
    app_resp = await client.post(
        f"/api/v1/runbooks/{rb_id}/approve",
        json={"approved_by": "Senior SRE Lead"},
        headers=headers,
    )
    assert app_resp.status_code == 200, app_resp.text
    assert app_resp.json()["status"] == "Approved"

    # Execute
    exec_resp = await client.post(f"/api/v1/runbooks/{rb_id}/execute", headers=headers)
    assert exec_resp.status_code == 200, exec_resp.text
    assert exec_resp.json()["status"] == "Completed"
