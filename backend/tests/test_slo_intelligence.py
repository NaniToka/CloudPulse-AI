"""
Pytest suite for Enterprise SLO, SLA & Error Budget Intelligence Center:
- SLI Calculations (Availability, Error Rate, Latency Percentiles, Throughput)
- SLO Engine Compliance Evaluation (HEALTHY, AT_RISK, BREACHED)
- Error Budget Engine Calculations (Total, Consumed, Remaining Budget %)
- Burn Rate Engine Severity Multipliers (NORMAL, ELEVATED, HIGH, CRITICAL)
- SLO Reliability Forecasting Engine (Month-End SLO, Exhaustion Date)
- SLO Violation Detection Engine
- Service & Platform Reliability Score Engine (0-100)
- Incident Correlation Engine
- Objectives CRUD & REST API Endpoints (/slo/overview, /services, /indicators, /objectives, /error-budget, /burn-rate, /violations, /forecast, /reliability, /incidents, /analyze)
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.slo import (
    burn_rate_engine,
    error_budget_engine,
    forecasting_engine,
    reliability_score_engine,
    sli_engine,
    slo_engine,
    violation_engine,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"slo-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Slo",
        "last_name": "Admin",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_sli_engine_calculation():
    """Test SLI engine calculations for availability, error rate, and percentiles."""
    lat_samples = [10.0, 20.0, 30.0, 45.0, 60.0, 85.0, 120.0, 200.0, 350.0, 500.0]
    sli = sli_engine.calculate_sli(
        total_events=1000,
        good_events=995,
        bad_events=5,
        latency_samples_ms=lat_samples,
    )
    assert sli["availability_pct"] == 99.5
    assert sli["error_rate_pct"] == 0.5
    assert sli["latency_p50_ms"] == 85.0
    assert sli["latency_p95_ms"] == 500.0


@pytest.mark.asyncio
async def test_slo_engine_compliance():
    """Test SLO compliance evaluation engine."""
    healthy = slo_engine.evaluate_slo_compliance("availability", target_slo=99.9, current_sli=99.98)
    assert healthy["status"] == "HEALTHY"
    assert healthy["compliance_pct"] == 100.0

    breached = slo_engine.evaluate_slo_compliance("availability", target_slo=99.9, current_sli=98.4)
    assert breached["status"] == "BREACHED"

    err_breached = slo_engine.evaluate_slo_compliance("error_rate", target_slo=1.0, current_sli=3.2)
    assert err_breached["status"] == "BREACHED"


@pytest.mark.asyncio
async def test_error_budget_engine_calculation():
    """Test error budget calculations over 30d window."""
    eb = error_budget_engine.calculate_error_budget(target_slo=99.9, current_availability_pct=99.98, window_days=30)
    assert eb["total_budget_sec"] == 2592.0
    assert eb["remaining_budget_pct"] == 80.0
    assert eb["status"] == "HEALTHY"

    eb_breached = error_budget_engine.calculate_error_budget(target_slo=99.9, current_availability_pct=98.4, window_days=30)
    assert eb_breached["remaining_budget_pct"] == 0.0
    assert eb_breached["status"] == "EXHAUSTED"


@pytest.mark.asyncio
async def test_burn_rate_engine_severity():
    """Test burn rate multiplier and severity classification."""
    br_normal = burn_rate_engine.calculate_burn_rate(target_slo=99.9, observed_error_rate_pct=0.05)
    assert br_normal["severity"] == "NORMAL"
    assert br_normal["burn_rate_x"] == 0.5

    br_critical = burn_rate_engine.calculate_burn_rate(target_slo=99.9, observed_error_rate_pct=1.5)
    assert br_critical["severity"] == "CRITICAL"
    assert br_critical["burn_rate_x"] == 15.0


@pytest.mark.asyncio
async def test_forecasting_engine_projections():
    """Test SLO forecasting engine projections."""
    fc = forecasting_engine.calculate_slo_forecast(
        target_slo=99.9,
        current_availability_pct=99.95,
        remaining_budget_pct=80.0,
        burn_rate_x=1.2,
    )
    assert fc["is_compliant_projected"] is True
    assert fc["confidence_pct"] == 94.5


@pytest.mark.asyncio
async def test_violation_engine_detection():
    """Test violation detection engine."""
    viols = violation_engine.detect_slo_violations()
    assert len(viols) >= 2
    services_with_viols = [v["service"] for v in viols]
    assert "payment-service" in services_with_viols
    assert "analytics-service" in services_with_viols


@pytest.mark.asyncio
async def test_reliability_score_engine():
    """Test reliability score calculation."""
    score = reliability_score_engine.calculate_service_reliability_score(
        availability_pct=99.98,
        error_rate_pct=0.02,
        latency_p95_ms=38.0,
        target_slo=99.9,
    )
    assert score["reliability_score"] >= 90.0
    assert score["status"] == "EXCELLENT"

    ov = reliability_score_engine.calculate_platform_reliability_overview()
    assert ov["platform_reliability_score"] > 0.0
    assert ov["total_services"] == 7


@pytest.mark.asyncio
async def test_api_slo_overview_and_services(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /slo/overview, GET /slo/services, and GET /slo/indicators."""
    ov_resp = await client.get("/api/v1/slo/overview", headers=auth_headers)
    assert ov_resp.status_code == 200, ov_resp.text
    assert ov_resp.json()["total_services"] == 7

    svc_resp = await client.get("/api/v1/slo/services", headers=auth_headers)
    assert svc_resp.status_code == 200, svc_resp.text
    assert len(svc_resp.json()) == 7

    single_resp = await client.get("/api/v1/slo/services/api-gateway", headers=auth_headers)
    assert single_resp.status_code == 200, single_resp.text

    ind_resp = await client.get("/api/v1/slo/indicators", headers=auth_headers)
    assert ind_resp.status_code == 200, ind_resp.text


@pytest.mark.asyncio
async def test_api_slo_objectives_crud(client: AsyncClient, auth_headers: dict[str, str], db_session: AsyncSession):
    """Test SLO Objectives CRUD REST endpoints."""
    create_payload = {
        "service": "checkout-service",
        "name": "Checkout API 99.9% Availability",
        "description": "Ensure checkout API availability target",
        "indicator_type": "availability",
        "target": 99.9,
        "window": "30d",
        "enabled": True,
    }
    create_resp = await client.post("/api/v1/slo/objectives", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    obj_id = create_resp.json()["id"]

    list_resp = await client.get("/api/v1/slo/objectives", headers=auth_headers)
    assert list_resp.status_code == 200, list_resp.text

    put_resp = await client.put(
        f"/api/v1/slo/objectives/{obj_id}",
        json={"target": 99.95, "name": "Updated Checkout Target"},
        headers=auth_headers,
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["target"] == 99.95

    del_resp = await client.delete(f"/api/v1/slo/objectives/{obj_id}", headers=auth_headers)
    assert del_resp.status_code == 204, del_resp.text


@pytest.mark.asyncio
async def test_api_slo_error_budget_and_burn_rate(client: AsyncClient, auth_headers: dict[str, str]):
    """Test Error Budget, Burn Rate, Violations, Forecast, and Analyze endpoints."""
    eb_resp = await client.get("/api/v1/slo/error-budget", headers=auth_headers)
    assert eb_resp.status_code == 200, eb_resp.text

    br_resp = await client.get("/api/v1/slo/burn-rate", headers=auth_headers)
    assert br_resp.status_code == 200, br_resp.text

    v_resp = await client.get("/api/v1/slo/violations", headers=auth_headers)
    assert v_resp.status_code == 200, v_resp.text

    fc_resp = await client.get("/api/v1/slo/forecast", headers=auth_headers)
    assert fc_resp.status_code == 200, fc_resp.text

    inc_resp = await client.get("/api/v1/slo/incidents", headers=auth_headers)
    assert inc_resp.status_code == 200, inc_resp.text

    anz_resp = await client.post("/api/v1/slo/analyze", headers=auth_headers)
    assert anz_resp.status_code == 200, anz_resp.text
    assert "SRE Intelligence Analysis Complete" in anz_resp.json()["analysis_summary"]
