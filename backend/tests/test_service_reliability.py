"""
Pytest Unit Test Suite for Enterprise Service Reliability Engine & SLO Intelligence 2.0.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import service_reliability_engine


@pytest.mark.asyncio
async def test_multi_window_burn_rates():
    """Test 5m, 30m, 1h, 6h, 24h, 7d multi-window burn rates and severity."""
    mw = service_reliability_engine.calculate_multi_window_burn_rates(
        target_slo=99.9,
        observed_error_rate_pct=0.5,
    )
    assert "base_burn_rate_x" in mw
    assert mw["base_burn_rate_x"] > 0
    windows = mw["windows"]
    assert "5m" in windows
    assert "1h" in windows
    assert "7d" in windows
    assert windows["1h"]["severity"] in ["NORMAL", "ELEVATED", "HIGH", "CRITICAL"]


@pytest.mark.asyncio
async def test_reliability_risk_scoring():
    """Test deterministic 0-100 reliability risk score and level classification."""
    risk = service_reliability_engine.calculate_reliability_risk_score(
        availability_pct=98.4,
        error_rate_pct=1.6,
        latency_p95_ms=780.0,
        target_slo=99.9,
        remaining_budget_pct=15.0,
        burn_rate_x=5.2,
        has_active_incident=True,
    )
    assert 0.0 <= risk["risk_score"] <= 100.0
    assert risk["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(risk["top_factors"]) >= 1


@pytest.mark.asyncio
async def test_service_prioritization():
    """Test deterministic prioritization ranking of services."""
    evals = [
        {"service_name": "healthy-svc", "risk_score": 10.0, "burn_rate": 1.0, "status": "HEALTHY"},
        {"service_name": "breached-svc", "risk_score": 85.0, "burn_rate": 6.5, "status": "BREACHED"},
    ]
    prio = service_reliability_engine.prioritize_service_investigation(evals)
    assert len(prio) == 2
    assert prio[0]["service_name"] == "breached-svc"
    assert prio[0]["priority_rank"] == 1
    assert prio[0]["priority_label"] == "Priority 1"


@pytest.mark.asyncio
async def test_deterministic_slo_forecasting():
    """Test SLO forecasting and INSUFFICIENT_DATA state when samples < 4."""
    # Insufficient data check
    fc_insufficient = service_reliability_engine.forecast_service_slo(
        target_slo=99.9,
        current_availability_pct=99.95,
        remaining_budget_pct=80.0,
        burn_rate_x=1.0,
        sample_count=2,
    )
    assert fc_insufficient["forecast_status"] == "INSUFFICIENT_DATA"

    # Valid forecast
    fc_valid = service_reliability_engine.forecast_service_slo(
        target_slo=99.9,
        current_availability_pct=99.95,
        remaining_budget_pct=80.0,
        burn_rate_x=1.0,
        sample_count=10,
    )
    assert fc_valid["forecast_status"] == "VALID"
    assert "projected_month_end_slo_pct" in fc_valid


@pytest.mark.asyncio
async def test_service_profile_evaluation():
    """Test complete single-service reliability profile evaluation."""
    t = {
        "service": "payment-service",
        "provider": "AWS",
        "region": "us-east-1",
        "target_slo": 99.9,
        "total_events": 420000,
        "good_events": 413280,
        "bad_events": 6720,
        "availability_pct": 98.40,
        "error_rate_pct": 1.60,
        "latency_p50_ms": 340.0,
        "latency_p95_ms": 780.0,
        "latency_p99_ms": 1450.0,
        "status": "BREACHED",
    }
    profile = service_reliability_engine.evaluate_service_profile(t)
    assert profile["service_id"] == "payment-service"
    assert profile["status"] == "BREACHED"
    assert profile["risk_score"] > 0
    assert "multi_window_burn_rates" in profile


@pytest.mark.asyncio
async def test_generate_reliability_recommendations():
    """Test deterministic SRE recommendations generation."""
    evals = [
        {
            "service_name": "payment-service",
            "status": "BREACHED",
            "burn_rate": 5.2,
            "latency_p95_ms": 780.0,
            "error_budget_remaining_pct": 15.0,
            "availability_pct": 98.4,
            "slo_target": 99.9,
            "error_rate_pct": 1.6,
            "risk_score": 85.0,
        }
    ]
    recs = service_reliability_engine.generate_reliability_recommendations(evals)
    assert len(recs) == 1
    assert recs[0]["service"] == "payment-service"
    assert recs[0]["priority"] == "CRITICAL"


@pytest.mark.asyncio
async def test_analyze_reliability_ai_fallback(db_session: AsyncSession):
    """Test AI reliability analysis fallback when Gemini key is absent."""
    evals = [
        {
            "service_name": "payment-service",
            "status": "BREACHED",
            "burn_rate": 5.2,
            "latency_p95_ms": 780.0,
            "error_budget_remaining_pct": 15.0,
            "availability_pct": 98.4,
            "slo_target": 99.9,
            "error_rate_pct": 1.6,
            "reliability_score": 52.0,
            "risk_score": 85.0,
        }
    ]
    result = await service_reliability_engine.analyze_reliability_ai(
        db_session,
        user_id="test-user-id",
        services_evals=evals,
    )
    assert result["analysis_engine"] in ["Local Reliability Intelligence", "Gemini AI"]
    assert "executive_summary" in result


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"reliability-user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "SRE",
        "last_name": "Reliability",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    if resp.status_code != 201:
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        token = resp.json()["access_token"]
    else:
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_api_reliability_overview_and_endpoints(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test all /api/v1/reliability/* REST API endpoints."""
    # 1. GET /reliability/overview
    resp = await client.get(
        "/api/v1/reliability/overview",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_reliability_score" in data
    assert "services_healthy" in data

    # 2. GET /reliability/services
    resp = await client.get(
        "/api/v1/reliability/services",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    svcs = resp.json()
    assert len(svcs) >= 1

    # 3. GET /reliability/services/{service_id}
    resp = await client.get(
        "/api/v1/reliability/services/payment-service",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["profile"]["service_name"] == "payment-service"
    assert "error_budget" in detail
    assert "multi_window_burn_rates" in detail

    # 4. GET /reliability/slo
    resp = await client.get(
        "/api/v1/reliability/slo",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 5. GET /reliability/error-budget
    resp = await client.get(
        "/api/v1/reliability/error-budget",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 6. GET /reliability/burn-rate
    resp = await client.get(
        "/api/v1/reliability/burn-rate",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 7. GET /reliability/risks
    resp = await client.get(
        "/api/v1/reliability/risks",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 8. GET /reliability/forecast
    resp = await client.get(
        "/api/v1/reliability/forecast",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 9. GET /reliability/dependencies
    resp = await client.get(
        "/api/v1/reliability/dependencies",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 10. GET /reliability/incidents
    resp = await client.get(
        "/api/v1/reliability/incidents",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 11. GET /reliability/recommendations
    resp = await client.get(
        "/api/v1/reliability/recommendations",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # 12. POST /reliability/analyze
    resp = await client.post(
        "/api/v1/reliability/analyze",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert "analysis_engine" in resp.json()
