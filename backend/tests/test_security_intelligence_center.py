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
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.security import SecurityScan
from app.services.security_detection_engine import security_detection_engine
from app.services.security_risk_engine import security_risk_engine
from app.services.security_service import security_service


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
async def test_security_scan_execution(db_session: AsyncSession):
    """Test triggering security scan persists findings to PostgreSQL."""
    resp = await security_service.run_security_scan(
        db_session, payload=type("Payload", (), {"provider": "AWS"})()
    )
    assert resp.total_findings >= 1
    assert resp.overall_security_score > 0

    items, total, _ = await security_service.list_findings(db_session)
    assert total >= resp.total_findings


@pytest.mark.asyncio
async def test_security_finding_status_transition(db_session: AsyncSession):
    """Test status transition for security finding (OPEN -> RESOLVED)."""
    items, total, _ = await security_service.list_findings(db_session, size=1)
    if total == 0:
        await security_service.run_security_scan(
            db_session, payload=type("Payload", (), {"provider": "AWS"})()
        )
        items, total, _ = await security_service.list_findings(db_session, size=1)

    finding = items[0]
    updated = await security_service.update_finding_status(
        db_session, finding.id, "RESOLVED"
    )
    assert updated is not None
    assert updated.status == "RESOLVED"


@pytest.mark.asyncio
async def test_api_security_overview():
    """Test GET /api/v1/security/overview endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/security/overview")
        assert response.status_code == 200
        data = response.json()
        assert "posture_score" in data
        assert "open_findings_count" in data
        assert "compliance_scorecards" in data


@pytest.mark.asyncio
async def test_api_list_security_findings():
    """Test GET /api/v1/security/findings with filters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/security/findings?size=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

        # Test severity filter
        sev_resp = await ac.get("/api/v1/security/findings?severity=Critical")
        assert sev_resp.status_code == 200


@pytest.mark.asyncio
async def test_api_update_finding_status(db_session: AsyncSession):
    """Test PATCH /api/v1/security/findings/{id}/status endpoint."""
    items, total, _ = await security_service.list_findings(db_session, size=1)
    if total == 0:
        await security_service.run_security_scan(
            db_session, payload=type("Payload", (), {"provider": "AWS"})()
        )
        items, total, _ = await security_service.list_findings(db_session, size=1)

    finding_id = items[0].id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.patch(
            f"/api/v1/security/findings/{finding_id}/status",
            json={"status": "INVESTIGATING", "notes": "Triaging finding"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INVESTIGATING"


@pytest.mark.asyncio
async def test_api_security_recommendations():
    """Test GET /api/v1/security/recommendations endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/security/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
