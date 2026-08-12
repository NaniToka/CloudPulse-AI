"""
Tests for AI Security & Cloud Compliance Center:
- Security Risk Engine
- Security Detection Engine (AWS, Azure, GCP, K8s)
- Finding CRUD & Filtering
- Status Transitions (OPEN -> INVESTIGATING -> MITIGATED -> RESOLVED -> ACCEPTED_RISK)
- API Endpoints (/overview, /findings, /findings/{id}, PATCH /findings/{id}/status, /recommendations, /scan)
"""

import uuid

import pytest
from httpx import AsyncClient

from app.services.security_detection_engine import security_detection_engine
from app.services.security_risk_engine import security_risk_engine


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"secuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Security",
        "last_name": "Tester",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_security_risk_engine_calculation():
    """Verify deterministic risk scoring calculation."""
    res = security_risk_engine.calculate_finding_risk(
        severity="CRITICAL",
        category="Storage",
        resource_type="s3_bucket",
        is_publicly_exposed=True,
        has_admin_privileges=True,
        confidence=0.95,
    )
    assert res["risk_score"] > 8.5
    assert res["confidence"] == 0.95
    assert len(res["reasoning_factors"]) >= 2


@pytest.mark.asyncio
async def test_security_detection_engine_fixtures():
    """Verify deterministic multi-cloud & K8s detection engine generates 16 findings."""
    findings = security_detection_engine.generate_findings()
    assert len(findings) >= 16

    providers = {f["provider"] for f in findings}
    assert "AWS" in providers
    assert "GCP" in providers
    assert "Azure" in providers
    assert "Kubernetes" in providers


@pytest.mark.asyncio
async def test_security_scan_execution(client: AsyncClient, auth_headers: dict[str, str]):
    """Test triggering security scan persists findings to database."""
    resp = await client.post(
        "/api/v1/security/scan",
        json={"provider": "AWS", "scan_name": "Test Cloud Scan"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["total_findings"] >= 1
    assert data["overall_security_score"] > 0


@pytest.mark.asyncio
async def test_api_security_overview(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/security/overview endpoint."""
    response = await client.get("/api/v1/security/overview", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "posture_score" in data
    assert "open_findings_count" in data
    assert "compliance_scorecards" in data


@pytest.mark.asyncio
async def test_api_list_security_findings(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/security/findings with filters."""
    response = await client.get("/api/v1/security/findings?size=10", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "items" in data
    assert "total" in data

    sev_resp = await client.get("/api/v1/security/findings?severity=Critical", headers=auth_headers)
    assert sev_resp.status_code == 200, sev_resp.text


@pytest.mark.asyncio
async def test_api_update_finding_status(client: AsyncClient, auth_headers: dict[str, str]):
    """Test PATCH /api/v1/security/findings/{id}/status endpoint."""
    list_resp = await client.get("/api/v1/security/findings?size=1", headers=auth_headers)
    assert list_resp.status_code == 200, list_resp.text
    items = list_resp.json()["items"]
    assert len(items) > 0

    finding_id = items[0]["id"]

    response = await client.patch(
        f"/api/v1/security/findings/{finding_id}/status",
        json={"status": "INVESTIGATING", "notes": "Triaging finding"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "INVESTIGATING"


@pytest.mark.asyncio
async def test_api_security_recommendations(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/security/recommendations endpoint."""
    response = await client.get("/api/v1/security/recommendations", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
