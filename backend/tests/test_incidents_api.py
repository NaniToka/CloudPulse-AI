"""
API tests for Incident Management Center endpoints (/api/v1/incidents).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"incuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Incident",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/incidents", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_get_active_incidents(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/incidents/active", headers=headers)
    assert response.status_code == 200, response.text
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0


@pytest.mark.asyncio
async def test_get_incident_stats(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/incidents/stats", headers=headers)
    assert response.status_code == 200, response.text
    stats = response.json()

    assert "open_incidents" in stats
    assert "critical_incidents" in stats
    assert "avg_resolution_time_minutes" in stats
    assert "sla_compliance_percent" in stats


@pytest.mark.asyncio
async def test_create_and_get_incident(client: AsyncClient):
    headers = await get_auth_headers(client)

    create_payload = {
        "title": "API Gateway 504 Gateway Timeout Burst",
        "description": "Upstream microservice connection reset under load test.",
        "severity": "P1",
        "priority": "High",
        "status": "Open",
        "affected_service": "api-gateway",
        "affected_region": "us-east-1",
        "assigned_engineer": "DevOps Engineer",
        "auto_analyze": True,
    }

    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    inc_data = create_resp.json()

    assert inc_data["title"] == create_payload["title"]
    assert inc_data["severity"] == "P1"
    assert inc_data["ai_summary"] is not None
    assert "id" in inc_data

    incident_id = inc_data["id"]

    # GET details
    get_resp = await client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == incident_id


@pytest.mark.asyncio
async def test_update_and_resolve_incident(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Create incident
    create_payload = {
        "title": "Database Read Replica Latency Spike",
        "description": "Read queries exceeding 1200ms threshold.",
        "severity": "P2",
        "priority": "Medium",
        "status": "Open",
        "affected_service": "db-read-replica",
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    inc_id = create_resp.json()["id"]

    # PUT update
    update_payload = {
        "status": "Investigating",
        "severity": "P1",
        "assigned_engineer": "Senior DBA",
        "assigned_to": "Senior DBA",
    }
    update_resp = await client.put(
        f"/api/v1/incidents/{inc_id}", json=update_payload, headers=headers
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["status"] == "Investigating"
    assert updated_data["severity"] == "P1"
    assert updated_data["assigned_engineer"] == "Senior DBA"

    # POST resolve
    resolve_payload = {
        "resolution_notes": "Restarted read replica node and rebalanced connection pool.",
        "resolved_by": "Senior DBA",
    }
    resolve_resp = await client.post(
        f"/api/v1/incidents/{inc_id}/resolve", json=resolve_payload, headers=headers
    )
    assert resolve_resp.status_code == 200
    resolved_data = resolve_resp.json()
    assert resolved_data["status"] == "Resolved"
    assert resolved_data["resolution_notes"] == resolve_payload["resolution_notes"]
    assert resolved_data["resolved_at"] is not None


@pytest.mark.asyncio
async def test_incident_analytics(client: AsyncClient):
    headers = await get_auth_headers(client)

    response = await client.get("/api/v1/incidents/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "incidents_by_severity" in data
    assert "mean_time_to_resolve_minutes" in data
    assert "monthly_trend" in data
    assert "resolution_rate_percent" in data
    assert "active_incidents" in data
    assert "resolved_incidents" in data


@pytest.mark.asyncio
async def test_reanalyze_incident(client: AsyncClient):
    headers = await get_auth_headers(client)

    create_payload = {
        "title": "Elasticsearch Index Read Lock",
        "description": "Log ingestion failing due to read-only index block.",
        "severity": "P2",
        "priority": "High",
        "status": "Open",
        "affected_service": "elasticsearch",
        "auto_analyze": False,
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    inc_id = create_resp.json()["id"]

    analyze_resp = await client.post(f"/api/v1/incidents/{inc_id}/analyze", headers=headers)
    assert analyze_resp.status_code == 200
    ai_res = analyze_resp.json()
    assert "ai_summary" in ai_res
    assert "ai_root_cause" in ai_res
    assert "ai_suggested_resolution" in ai_res


@pytest.mark.asyncio
async def test_delete_incident(client: AsyncClient):
    headers = await get_auth_headers(client)

    create_payload = {
        "title": "Temporary Test Incident",
        "severity": "P3",
        "priority": "Low",
        "status": "Open",
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    inc_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/incidents/{inc_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/incidents/{inc_id}", headers=headers)
    assert get_resp.status_code == 404
