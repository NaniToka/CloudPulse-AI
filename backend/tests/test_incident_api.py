"""
API integration tests for Incident Management Center endpoints (/api/v1/incidents).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"incapi-{uuid.uuid4().hex[:8]}@example.com",
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
async def test_get_active_and_stats(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Active
    active_resp = await client.get("/api/v1/incidents/active", headers=headers)
    assert active_resp.status_code == 200
    assert isinstance(active_resp.json(), list)

    # Stats
    stats_resp = await client.get("/api/v1/incidents/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "open_incidents" in stats
    assert "critical_incidents" in stats
    assert "avg_resolution_time_minutes" in stats
    assert "sla_compliance_percent" in stats


@pytest.mark.asyncio
async def test_create_get_acknowledge_and_resolve(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Create Incident
    create_payload = {
        "title": "API Gateway 504 Gateway Timeout Burst",
        "description": "Upstream microservice connection reset under load test.",
        "severity": "CRITICAL",
        "priority": "Critical",
        "status": "DETECTED",
        "affected_service": "api-gateway",
        "affected_services": ["api-gateway", "database-cluster"],
        "affected_region": "us-east-1",
        "assigned_engineer": "DevOps Engineer",
        "auto_analyze": True,
    }

    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    inc_data = create_resp.json()

    incident_id = inc_data["id"]
    assert inc_data["title"] == create_payload["title"]
    assert inc_data["confidence_score"] >= 0.85

    # 2. Get Details
    get_resp = await client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == incident_id

    # 3. Acknowledge
    ack_resp = await client.post(
        f"/api/v1/incidents/{incident_id}/acknowledge",
        json={"assigned_to": "Sarah Chen", "notes": "Investigating active connection count"},
        headers=headers,
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "INVESTIGATING"

    # 4. Re-analyze RCA
    rca_resp = await client.post(f"/api/v1/incidents/{incident_id}/analyze", headers=headers)
    assert rca_resp.status_code == 200
    assert "root_cause" in rca_resp.json()

    # 5. Resolve
    resolve_payload = {
        "resolution_notes": "PgBouncer reset and scaled PostgreSQL max_connections to 500.",
        "resolved_by": "Sarah Chen (SRE Lead)",
    }
    resolve_resp = await client.post(
        f"/api/v1/incidents/{incident_id}/resolve",
        json=resolve_payload,
        headers=headers,
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "RESOLVED"
    assert resolve_resp.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_correlate_api_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {
        "alerts": [
            {
                "service": "postgres-primary",
                "event_type": "metric_anomaly",
                "title": "Postgres connection pool saturation",
                "severity": "CRITICAL",
            },
            {
                "service": "payment-api",
                "event_type": "trace_failure",
                "title": "HTTP 500 downstream error on payment",
                "severity": "HIGH",
            },
        ],
        "time_window_minutes": 15,
    }

    resp = await client.post("/api/v1/incidents/correlate", json=payload, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["correlated_incidents_count"] >= 1
    assert data["raw_alerts_processed"] == 2


@pytest.mark.asyncio
async def test_remediate_api_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)

    # First create incident
    create_payload = {
        "title": "Redis Cache OOM Crash",
        "severity": "HIGH",
        "status": "INVESTIGATING",
        "affected_service": "redis-cluster",
        "auto_analyze": True,
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    inc_id = create_resp.json()["id"]

    # Trigger remediation
    rem_payload = {
        "action_id": "act-scale-redis",
        "authorized_by": "Alex SRE",
        "override_parameters": {"replicas": 3},
    }
    rem_resp = await client.post(
        f"/api/v1/incidents/{inc_id}/remediate", json=rem_payload, headers=headers
    )
    assert rem_resp.status_code == 200, rem_resp.text
    data = rem_resp.json()
    assert data["status"] == "EXECUTED"
    assert "workflow_execution_id" in data
