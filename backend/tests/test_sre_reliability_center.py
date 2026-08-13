"""
Pytest Suite for Enterprise SRE & Reliability Intelligence Center:
- SLI & SLO Engine Evaluation
- Error Budget & Multi-Window Burn Rate Calculation
- SRE Reliability Scoring Engine (0-100 & Rating)
- Reliability Risk Detection Engine
- Reliability Forecast Engine (24h, 7d, 30d)
- Actionable SRE Recommendation Engine
- REST API Endpoints (/sre/overview, /sre/services, /sre/slis, /sre/slos, /sre/error-budgets, /sre/burn-rates, /sre/risks, /sre/incidents, /sre/dependencies, /sre/forecast, /sre/recommendations, /sre/analyze)
"""

import uuid

import pytest
from httpx import AsyncClient

from app.services.sre_engine import (
    calculate_burn_rates,
    calculate_error_budget,
    calculate_reliability_score,
    calculate_sli_metrics,
    detect_reliability_risks,
    evaluate_slo,
    forecast_reliability_trends,
    generate_sre_recommendations,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"sreuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "SRE",
        "last_name": "Engineer",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_sli_calculation_engine():
    """Verify SLI metrics calculation (availability %, error rate %, latency p50/p95/p99, throughput)."""
    res = calculate_sli_metrics(
        total_requests=10000,
        failed_requests=15,
        latency_samples_ms=[20.0, 35.0, 45.0, 120.0, 350.0],
        duration_seconds=3600.0,
    )
    assert res["total_requests"] == 10000
    assert res["failed_requests"] == 15
    assert res["availability"] == 99.85
    assert res["error_rate"] == 0.15
    assert res["throughput_rps"] == 2.78
    assert res["latency_p95_ms"] > 0


@pytest.mark.asyncio
async def test_slo_evaluation_engine():
    """Verify SLO target evaluation across Availability, Latency, and Error Rate."""
    avail_res = evaluate_slo(indicator_type="availability", target=99.9, current_sli=99.95)
    assert avail_res["status"] == "HEALTHY"
    assert avail_res["compliance_percentage"] == 100.0

    breach_res = evaluate_slo(indicator_type="availability", target=99.9, current_sli=99.82)
    assert breach_res["status"] == "BREACHED"

    lat_res = evaluate_slo(indicator_type="latency", target=95.0, current_sli=520.0, target_threshold_ms=500.0)
    assert lat_res["status"] == "BREACHED"


@pytest.mark.asyncio
async def test_error_budget_and_burn_rates():
    """Verify error budget allocation and 1h, 6h, 24h, 7d burn rate calculation."""
    eb = calculate_error_budget(target_slo=99.9, current_availability=99.82)
    assert eb["total_budget_pct"] == 0.1
    assert eb["consumed_pct"] == 100.0  # 0.18% error vs 0.10% budget
    assert eb["remaining_pct"] == 0.0

    burn = calculate_burn_rates(eb, recent_error_rate=0.18)
    assert burn["status"] == "CRITICAL"
    assert burn["burn_1h"] > 1.0


@pytest.mark.asyncio
async def test_reliability_scoring_engine():
    """Verify deterministic 0-100 reliability score and rating assignment."""
    exc_score = calculate_reliability_score(
        availability=99.99,
        latency_p95_ms=45.0,
        error_rate=0.01,
        slo_status="HEALTHY",
        burn_rate_status="NORMAL",
        active_incidents_count=0,
    )
    assert exc_score["score"] >= 95.0
    assert exc_score["rating"] == "EXCELLENT"

    crit_score = calculate_reliability_score(
        availability=98.5,
        latency_p95_ms=650.0,
        error_rate=1.5,
        slo_status="BREACHED",
        burn_rate_status="CRITICAL",
        active_incidents_count=2,
    )
    assert crit_score["score"] < 70.0
    assert crit_score["rating"] == "CRITICAL"


@pytest.mark.asyncio
async def test_reliability_risk_detection():
    """Verify risk detection logic for SLO breach and rapid burn rate."""
    risks = detect_reliability_risks(
        service_name="api-gateway",
        availability=99.82,
        latency_p95_ms=480.0,
        error_rate=0.18,
        slo_status="BREACHED",
        remaining_budget_pct=12.0,
        burn_status="CRITICAL",
        incidents_count=1,
    )
    assert len(risks) >= 3
    risk_names = {r["risk"] for r in risks}
    assert "SLO Target Breached" in risk_names
    assert "Rapid Error Budget Exhaustion" in risk_names


@pytest.mark.asyncio
async def test_reliability_forecasting_and_recommendations():
    """Verify forecasting and recommendation generation."""
    history = [
        {"availability": 99.92, "error_rate": 0.08, "latency_p95_ms": 42.0},
        {"availability": 99.88, "error_rate": 0.12, "latency_p95_ms": 48.0},
    ]
    fc = forecast_reliability_trends(history)
    assert fc["status"] == "VALID"
    assert "forecast_24h" in fc
    assert fc["confidence"] > 0.8

    recs = generate_sre_recommendations(
        service_name="api-gateway",
        availability=99.82,
        latency_p95_ms=520.0,
        error_rate=0.85,
        slo_status="BREACHED",
        burn_status="CRITICAL",
    )
    assert len(recs) >= 2


# ── REST API Integration Tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_get_sre_overview(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/sre/overview."""
    resp = await client.get("/api/v1/sre/overview", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "overall_score" in data
    assert "overall_rating" in data
    assert "services_healthy" in data


@pytest.mark.asyncio
async def test_api_get_sre_services(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/sre/services with sorting."""
    resp = await client.get("/api/v1/sre/services?sort_by=worst_reliability", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "services" in data
    assert len(data["services"]) >= 1


@pytest.mark.asyncio
async def test_api_get_sre_slis_and_slos(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/sre/slis and GET /api/v1/sre/slos."""
    sli_resp = await client.get("/api/v1/sre/slis", headers=auth_headers)
    assert sli_resp.status_code == 200, sli_resp.text
    assert "availability" in sli_resp.json()

    slo_resp = await client.get("/api/v1/sre/slos", headers=auth_headers)
    assert slo_resp.status_code == 200, slo_resp.text
    assert "slos" in slo_resp.json()


@pytest.mark.asyncio
async def test_api_slo_crud_lifecycle(client: AsyncClient, auth_headers: dict[str, str]):
    """Test POST /api/v1/sre/slos and PUT /api/v1/sre/slos/{id}."""
    create_payload = {
        "service": "checkout-service",
        "name": "Checkout Availability 99.9%",
        "description": "High priority checkout flow availability target",
        "indicator_type": "availability",
        "target": 99.9,
        "window": "30d",
        "enabled": True,
    }
    create_resp = await client.post("/api/v1/sre/slos", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["service"] == "checkout-service"

    slo_id = created["id"]
    update_resp = await client.put(
        f"/api/v1/sre/slos/{slo_id}",
        json={"target": 99.95, "description": "Updated target to 99.95%"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["target"] == 99.95


@pytest.mark.asyncio
async def test_api_get_error_budgets_and_burn_rates(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/sre/error-budgets and GET /api/v1/sre/burn-rates."""
    eb_resp = await client.get("/api/v1/sre/error-budgets", headers=auth_headers)
    assert eb_resp.status_code == 200, eb_resp.text
    assert len(eb_resp.json()) >= 1

    burn_resp = await client.get("/api/v1/sre/burn-rates", headers=auth_headers)
    assert burn_resp.status_code == 200, burn_resp.text
    assert len(burn_resp.json()) >= 1


@pytest.mark.asyncio
async def test_api_get_risks_incidents_dependencies_forecast_recs(client: AsyncClient, auth_headers: dict[str, str]):
    """Test risks, incidents, dependencies, forecast, and recommendations endpoints."""
    risks_resp = await client.get("/api/v1/sre/risks", headers=auth_headers)
    assert risks_resp.status_code == 200, risks_resp.text
    assert "risks" in risks_resp.json()

    inc_resp = await client.get("/api/v1/sre/incidents", headers=auth_headers)
    assert inc_resp.status_code == 200, inc_resp.text
    assert "incidents" in inc_resp.json()

    dep_resp = await client.get("/api/v1/sre/dependencies", headers=auth_headers)
    assert dep_resp.status_code == 200, dep_resp.text
    assert "dependencies" in dep_resp.json()

    fc_resp = await client.get("/api/v1/sre/forecast", headers=auth_headers)
    assert fc_resp.status_code == 200, fc_resp.text
    assert "forecast_24h" in fc_resp.json()

    recs_resp = await client.get("/api/v1/sre/recommendations", headers=auth_headers)
    assert recs_resp.status_code == 200, recs_resp.text
    assert "recommendations" in recs_resp.json()


@pytest.mark.asyncio
async def test_api_analyze_sre(client: AsyncClient, auth_headers: dict[str, str]):
    """Test POST /api/v1/sre/analyze endpoint."""
    resp = await client.post("/api/v1/sre/analyze", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "executive_summary" in data
    assert "analysis_engine" in data
