"""
Pytest suite for Executive Cloud Operations Command Center:
- Cloud Operations Health Score Calculation
- Executive Summary (AI & Local Operations)
- Top Priorities & Prioritization Engine
- Operational Trends Analysis
- Provider & Service Aggregation
- REST API Endpoints (/executive/overview, /health, /summary, /priorities, /trends, /providers, /services, /risks, /changes, /timeline, /export/pdf, /export/csv)
"""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.services.executive_engine import (
    calculate_cloud_operations_health_score,
    calculate_top_priorities,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"exec-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Executive",
        "last_name": "CTO",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_api_executive_overview(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/executive/overview endpoint."""
    resp = await client.get("/api/v1/executive/overview", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "health_score" in data
    assert "summary" in data
    assert "metrics" in data
    assert "top_priorities" in data
    assert "provider_health" in data
    assert "operational_trends" in data
    assert "risk_matrix" in data
    assert "what_changed" in data
    assert "mode_indicator" in data
    assert "DEMO / LOCAL MODE" in data["mode_indicator"]


@pytest.mark.asyncio
async def test_api_executive_health_and_summary(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/executive/health and /summary."""
    health_resp = await client.get("/api/v1/executive/health", headers=auth_headers)
    assert health_resp.status_code == 200, health_resp.text
    h_data = health_resp.json()
    assert "overall_score" in h_data
    assert h_data["risk_level"] in ("HEALTHY", "LOW_RISK", "MODERATE_RISK", "HIGH_RISK", "CRITICAL")
    assert len(h_data["components"]) == 6

    sum_resp = await client.get("/api/v1/executive/summary", headers=auth_headers)
    assert sum_resp.status_code == 200, sum_resp.text
    s_data = sum_resp.json()
    assert "summary_text" in s_data
    assert "source" in s_data


@pytest.mark.asyncio
async def test_api_executive_priorities_filtering(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/executive/priorities with domain filtering."""
    resp = await client.get("/api/v1/executive/priorities", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "priorities" in data
    assert len(data["priorities"]) >= 1

    # Filter by domain
    finops_resp = await client.get("/api/v1/executive/priorities?domain=FINOPS", headers=auth_headers)
    assert finops_resp.status_code == 200, finops_resp.text
    f_data = finops_resp.json()
    for p in f_data["priorities"]:
        assert p["domain"].upper() == "FINOPS"


@pytest.mark.asyncio
async def test_api_executive_providers_and_services(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/executive/providers and /services."""
    prov_resp = await client.get("/api/v1/executive/providers", headers=auth_headers)
    assert prov_resp.status_code == 200, prov_resp.text
    p_data = prov_resp.json()
    assert "providers" in p_data
    assert len(p_data["providers"]) == 4

    svc_resp = await client.get("/api/v1/executive/services", headers=auth_headers)
    assert svc_resp.status_code == 200, svc_resp.text
    s_data = svc_resp.json()
    assert "services" in s_data
    assert len(s_data["services"]) >= 1


@pytest.mark.asyncio
async def test_api_executive_risks_changes_timeline(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /executive/risks, /changes, /timeline, /alerts, /recommendations."""
    risks_resp = await client.get("/api/v1/executive/risks", headers=auth_headers)
    assert risks_resp.status_code == 200, risks_resp.text
    assert len(risks_resp.json()["matrix"]) >= 5

    changes_resp = await client.get("/api/v1/executive/changes", headers=auth_headers)
    assert changes_resp.status_code == 200, changes_resp.text
    assert len(changes_resp.json()["changes"]) >= 1

    tl_resp = await client.get("/api/v1/executive/timeline", headers=auth_headers)
    assert tl_resp.status_code == 200, tl_resp.text
    assert "events" in tl_resp.json()

    alerts_resp = await client.get("/api/v1/executive/alerts", headers=auth_headers)
    assert alerts_resp.status_code == 200, alerts_resp.text
    assert "alerts" in alerts_resp.json()

    recs_resp = await client.get("/api/v1/executive/recommendations", headers=auth_headers)
    assert recs_resp.status_code == 200, recs_resp.text
    assert "recommendations" in recs_resp.json()


@pytest.mark.asyncio
async def test_api_executive_export_pdf_and_csv(client: AsyncClient, auth_headers: dict[str, str]):
    """Test POST /api/v1/executive/export/pdf and /csv."""
    pdf_resp = await client.post("/api/v1/executive/export/pdf", headers=auth_headers)
    assert pdf_resp.status_code == 200, f"PDF failed: {pdf_resp.status_code} - {pdf_resp.text}"
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 100

    csv_resp = await client.post("/api/v1/executive/export/csv", headers=auth_headers)
    assert csv_resp.status_code == 200, f"CSV failed: {csv_resp.status_code} - {csv_resp.text}"
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "Cloud Operations Health Score" in csv_resp.text
