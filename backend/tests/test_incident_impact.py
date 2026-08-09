"""
Unit & Integration tests for Incident Blast Radius & Impact Analysis.
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"incimpact-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Impact",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_incident_impact_and_blast_radius(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Create incident with multiple affected services
    create_payload = {
        "title": "PostgreSQL Primary Connection Exhaustion Outage",
        "severity": "CRITICAL",
        "priority": "Critical",
        "status": "INVESTIGATING",
        "affected_service": "database-cluster",
        "affected_services": ["database-cluster", "payment-service", "order-worker", "api-gateway"],
        "affected_resources": ["postgres-primary-instance"],
        "auto_analyze": True,
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    incident_id = create_resp.json()["id"]

    # 2. Query Blast Radius & Impact endpoint
    impact_resp = await client.get(f"/api/v1/incidents/{incident_id}/impact", headers=headers)
    assert impact_resp.status_code == 200, impact_resp.text
    impact = impact_resp.json()

    assert impact["root_component"] == "database-cluster"
    assert len(impact["affected_services"]) == 4
    assert impact["dependency_depth"] >= 1
    assert "CRITICAL" in impact["estimated_user_impact"]
    assert "financial_risk_estimate" in impact
    assert "topology_graph" in impact
    assert len(impact["topology_graph"]["nodes"]) >= 4
