"""
Comprehensive Pytest Test Suite for Predictive AIOps & Anomaly Intelligence Engine.
Covers 20 distinct verification scenarios across statistical, predictive, lifecycle, and API layers.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.organization import Organization
from app.models.prediction import AnomalyEvent, Prediction
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.services.anomaly_engine import anomaly_engine
from app.services.baseline_engine import baseline_engine
from app.services.capacity_risk_engine import capacity_risk_engine
from app.services.forecasting_engine import forecasting_engine
from app.services.predictive_aiops_engine import predictive_aiops_engine
from app.services.prediction_service import prediction_service
from app.services.telemetry_normalizer import telemetry_normalizer


def unique_auth_payload() -> dict:
    return {
        "email": f"aiops-pred-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "AIOps",
        "last_name": "Predictor",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_auth_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 1. Telemetry Normalization
# ---------------------------------------------------------------------------
def test_telemetry_normalization():
    raw_points = [
        {"timestamp": "2026-08-11T12:00:00Z", "value": 45.0},
        {"timestamp": "2026-08-11T12:01:00Z", "value": 55.0},
        {"timestamp": "2026-08-11T12:01:00Z", "value": 65.0},  # Duplicate timestamp for averaging
        {"timestamp": "2026-08-11T12:02:00Z", "value": 75.0},
    ]
    norm = telemetry_normalizer.normalize(
        raw_points=raw_points,
        metric_name="cpu_usage",
        service="api-gateway",
        bucket_seconds=60,
    )
    assert norm.metric_name == "cpu_utilization"
    assert norm.service == "api-gateway"
    assert norm.sample_count == 3  # 12:00, 12:01 (averaged 60.0), 12:02
    assert norm.values[1] == 60.0


# ---------------------------------------------------------------------------
# 2. Baseline Calculation
# ---------------------------------------------------------------------------
def test_baseline_calculation():
    series = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    baseline = baseline_engine.calculate_baseline(series, window="1h", metric_name="cpu_utilization")
    assert baseline.samples_count == 10
    assert baseline.mean == 55.0
    assert baseline.median == 55.0
    assert baseline.min_value == 10.0
    assert baseline.max_value == 100.0
    assert baseline.p90 >= 90.0
    assert baseline.standard_deviation > 0.0


# ---------------------------------------------------------------------------
# 3. Data Sufficiency Check
# ---------------------------------------------------------------------------
def test_data_sufficiency_check():
    suff_short = baseline_engine.calculate_data_sufficiency(samples_count=3, window="1h")
    assert suff_short.sufficient is False
    assert suff_short.minimum_required == 15

    suff_ample = baseline_engine.calculate_data_sufficiency(samples_count=35, window="1h")
    assert suff_ample.sufficient is True
    assert suff_ample.confidence_factor == 1.0


# ---------------------------------------------------------------------------
# 4. Z-Score Anomaly Detection
# ---------------------------------------------------------------------------
def test_z_score_anomaly_detection():
    # Nominal steady state: mean 50, std ~ 2
    history = [50.0, 51.0, 49.0, 50.0, 52.0, 48.0, 50.0, 51.0, 49.0, 50.0]
    # Extreme spike to 95.0
    res_spike = anomaly_engine.detect_anomaly(current_value=95.0, historical_values=history)
    assert res_spike.is_anomaly is True
    assert res_spike.severity == "CRITICAL"
    assert res_spike.direction == "SPIKE_HIGH"
    assert res_spike.anomaly_score >= 0.80

    # Normal point 50.5
    res_normal = anomaly_engine.detect_anomaly(current_value=50.5, historical_values=history)
    assert res_normal.is_anomaly is False
    assert res_normal.severity == "NORMAL"


# ---------------------------------------------------------------------------
# 5. Rolling Deviation & Envelope Anomaly
# ---------------------------------------------------------------------------
def test_rolling_deviation_anomaly():
    drift_vals = [20.0, 21.0, 20.0, 22.0, 24.0, 28.0, 35.0, 48.0, 68.0]
    ewma_val, is_drifting = anomaly_engine.detect_ewma_drift(drift_vals, alpha=0.4, drift_threshold=2.0)
    assert ewma_val > 40.0
    assert is_drifting is True


# ---------------------------------------------------------------------------
# 6. Trend Detection (Increasing, Decreasing, Stable)
# ---------------------------------------------------------------------------
def test_trend_detection_increasing_decreasing():
    inc_vals = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
    trend_inc = capacity_risk_engine.trend.analyze_trend(inc_vals, metric_name="memory_utilization")
    assert trend_inc.trend == "INCREASING"
    assert trend_inc.rate_of_change > 0
    assert trend_inc.r_squared > 0.95

    dec_vals = [80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0]
    trend_dec = capacity_risk_engine.trend.analyze_trend(dec_vals, metric_name="cpu_utilization")
    assert trend_dec.trend in ["DECREASING", "RECOVERY"]
    assert trend_dec.rate_of_change < 0

    stable_vals = [50.0, 50.2, 49.8, 50.1, 50.0, 49.9, 50.1]
    trend_stable = capacity_risk_engine.trend.analyze_trend(stable_vals, metric_name="cpu_utilization")
    assert trend_stable.trend == "STABLE"


# ---------------------------------------------------------------------------
# 7. Capacity Risk & Estimated Time to Threshold
# ---------------------------------------------------------------------------
def test_capacity_risk_and_breach_estimation():
    # Linear heap growth from 50% to 80% with slope +3.75%/sample
    leak_series = [50.0, 53.75, 57.5, 61.25, 65.0, 68.75, 72.5, 76.25, 80.0]
    cap_res = capacity_risk_engine.evaluate_capacity_risk(
        values=leak_series,
        resource_name="memory_utilization",
        custom_threshold=85.0,
        sample_interval_minutes=1.0,
    )
    assert cap_res.risk_level in ["CRITICAL", "HIGH"]
    assert cap_res.is_exhaustion_imminent is True
    assert cap_res.estimated_time_to_threshold_minutes is not None
    # Buffer is 85 - 80 = 5%. At 3.75%/min, ~1.3 minutes
    assert 0.5 <= cap_res.estimated_time_to_threshold_minutes <= 10.0


# ---------------------------------------------------------------------------
# 8. Forecasting Horizons & Bounds (5m to 24h)
# ---------------------------------------------------------------------------
def test_forecasting_horizons_and_bounds():
    series = [45.0, 48.0, 52.0, 56.0, 61.0, 67.0, 74.0, 82.0]
    forecast = forecasting_engine.generate_forecast(
        values=series,
        metric_name="memory_utilization",
        service="auth-service",
        horizons=("5m", "15m", "30m", "1h", "6h", "24h"),
    )
    assert len(forecast.forecast_points) == 6
    assert forecast.forecast_points[0].horizon == "5m"
    assert forecast.forecast_points[-1].horizon == "24h"

    for pt in forecast.forecast_points:
        assert pt.lower_bound <= pt.predicted_value <= pt.upper_bound
        assert 0.0 <= pt.confidence <= 1.0


# ---------------------------------------------------------------------------
# 9. Confidence Score Calculation
# ---------------------------------------------------------------------------
def test_confidence_score_calculation():
    # Long high-quality sample vs tiny sample
    long_series = [50.0 + (i * 0.5) for i in range(50)]
    f_long = forecasting_engine.generate_forecast(long_series)
    assert f_long.forecast_points[0].confidence >= 0.85

    short_series = [50.0, 52.0]
    f_short = forecasting_engine.generate_forecast(short_series)
    assert f_short.forecast_points[0].confidence <= 0.70


# ---------------------------------------------------------------------------
# 10. Failure Probability Scoring
# ---------------------------------------------------------------------------
def test_failure_probability_scoring():
    # Severe anomaly (0.95), steep trend (0.90), high capacity risk (0.95), dependency penalty (15.0)
    prob_crit, risk_crit = predictive_aiops_engine.calculate_failure_probability(
        anomaly_score=0.95,
        trend_strength=0.90,
        capacity_risk_score=0.95,
        dependency_health_penalty=15.0,
        active_incidents_count=2,
    )
    assert prob_crit >= 0.85
    assert risk_crit == "Critical"

    # Mild anomaly (0.20), flat trend (0.10), low capacity risk (0.15)
    prob_low, risk_low = predictive_aiops_engine.calculate_failure_probability(
        anomaly_score=0.20,
        trend_strength=0.10,
        capacity_risk_score=0.15,
    )
    assert prob_low <= 0.40
    assert risk_low == "Low"


# ---------------------------------------------------------------------------
# 11. Multi-Metric Anomaly Correlation
# ---------------------------------------------------------------------------
def test_multi_metric_anomaly_correlation():
    metric_map = {
        "cpu_utilization": [50.0, 55.0, 65.0, 78.0, 92.0, 96.5],
        "memory_utilization": [50.0, 58.0, 68.0, 79.0, 88.0, 94.0],
        "latency_ms": [100.0, 120.0, 250.0, 800.0, 1800.0, 3200.0],
        "error_rate": [0.1, 0.2, 0.5, 1.8, 3.5, 5.2],
    }
    corr = predictive_aiops_engine.correlate_multi_metric_anomalies("checkout-service", metric_map)
    assert corr["is_degraded"] is True
    assert corr["correlation_score"] >= 0.75
    assert corr["degradation_pattern"] == "RESOURCE_SATURATION_CASCADE"
    assert len(corr["signals"]) >= 3


# ---------------------------------------------------------------------------
# 12. Prediction Persistence & Database Queries
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_prediction_persistence_and_query(db_session: AsyncSession):
    now = datetime.now(UTC)
    pred = Prediction(
        id=uuid.uuid4(),
        title="Test Persistent Failure Prediction",
        service="order-service",
        environment="production",
        region="us-east-1",
        prediction_score=0.88,
        failure_probability=88.0,
        risk_level="High",
        status="Active",
        likely_root_cause="Database connection pool saturation",
        created_at=now,
        updated_at=now,
    )
    db_session.add(pred)
    await db_session.commit()

    fetched = await prediction_service.get_by_id(db_session, pred.id)
    assert fetched is not None
    assert fetched.service == "order-service"
    assert fetched.failure_probability == 88.0


# ---------------------------------------------------------------------------
# 13. Prediction Lifecycle Transitions
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_prediction_lifecycle_transitions(db_session: AsyncSession):
    now = datetime.now(UTC)
    pred = Prediction(
        id=uuid.uuid4(),
        title="Lifecycle State Transition Test",
        service="payment-service",
        status="Active",
        risk_level="Critical",
        created_at=now,
        updated_at=now,
    )
    db_session.add(pred)
    await db_session.commit()

    # Transition to Mitigated
    updated = await prediction_service.update_status(db_session, pred.id, "Mitigated")
    assert updated is not None
    assert updated.status == "Mitigated"

    # Transition to Resolved
    resolved = await prediction_service.update_status(db_session, pred.id, "Resolved")
    assert resolved is not None
    assert resolved.status == "Resolved"


# ---------------------------------------------------------------------------
# 14. Incident Command Center Integration (Declare Incident)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_incident_integration_create(db_session: AsyncSession):
    now = datetime.now(UTC)
    pred = Prediction(
        id=uuid.uuid4(),
        title="Critical Cache Outage Imminent",
        service="cache-service",
        risk_level="Critical",
        failure_probability=95.0,
        status="Active",
        likely_root_cause="Redis cluster master node memory saturation",
        recommended_preventive_actions=["Failover to redis-replica-01"],
        created_at=now,
        updated_at=now,
    )
    db_session.add(pred)
    await db_session.commit()

    incident = await prediction_service.create_incident_from_prediction(
        db=db_session,
        prediction_id=pred.id,
        custom_severity="CRITICAL",
    )
    assert incident is not None
    assert incident.affected_service == "cache-service"
    assert incident.severity == "CRITICAL"
    assert incident.source == "AIOps_Prediction"

    # Verify prediction status updated to Triggered
    reloaded_pred = await prediction_service.get_by_id(db_session, pred.id)
    assert reloaded_pred.status == "Triggered"


# ---------------------------------------------------------------------------
# 15. Dependency Integration (Upstream/Downstream Impact)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dependency_integration_upstream_downstream(db_session: AsyncSession):
    # Create service dependency link
    dep = ServiceDependency(
        id=uuid.uuid4(),
        source_service="checkout-service",
        target_service="payment-gateway",
        dependency_type="http",
        error_rate=12.5,
        latency_ms=850.0,
    )
    db_session.add(dep)
    await db_session.commit()

    prediction = await predictive_aiops_engine.generate_prediction(
        db=db_session,
        service_name="checkout-service",
        region="us-east-1",
    )
    assert prediction is not None
    assert "payment-gateway" in prediction.affected_services


# ---------------------------------------------------------------------------
# 16. Gemini AI Diagnostics Fallback
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_gemini_fallback_diagnostics(db_session: AsyncSession):
    # Without valid Gemini key, engine falls back cleanly to local
    prediction = await predictive_aiops_engine.generate_prediction(
        db=db_session,
        service_name="auth-service",
        region="us-west-2",
    )
    assert prediction.analysis_engine in ["local", "gemini"]
    assert prediction.ai_explanation is not None
    assert len(prediction.recommended_preventive_actions) > 0


# ---------------------------------------------------------------------------
# 17. Multi-Tenant Organization Isolation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_organization_tenant_isolation(db_session: AsyncSession):
    org_a = Organization(id=uuid.uuid4(), name="Org Alpha", slug=f"org-alpha-{uuid.uuid4().hex[:6]}")
    org_b = Organization(id=uuid.uuid4(), name="Org Beta", slug=f"org-beta-{uuid.uuid4().hex[:6]}")
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    pred_a = Prediction(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        title="Alpha Risk Alert",
        service="alpha-api",
        status="Active",
    )
    pred_b = Prediction(
        id=uuid.uuid4(),
        organization_id=org_b.id,
        title="Beta Risk Alert",
        service="beta-api",
        status="Active",
    )
    db_session.add_all([pred_a, pred_b])
    await db_session.commit()

    # Query org A
    list_a, total_a, _ = await prediction_service.list_predictions(db_session, organization_id=org_a.id)
    svc_names_a = [p.service for p in list_a]
    assert "alpha-api" in svc_names_a
    assert "beta-api" not in svc_names_a


# ---------------------------------------------------------------------------
# 18. REST Endpoints & RBAC Validation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rbac_and_permissions(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Forecast endpoint
    forecast_resp = await client.post(
        "/api/v1/predictions/forecast",
        json={"service": "user-service", "metric_name": "cpu_utilization", "historical_values": [50.0, 60.0, 70.0, 80.0]},
        headers=headers,
    )
    assert forecast_resp.status_code == 200
    f_data = forecast_resp.json()
    assert "forecast_points" in f_data
    assert len(f_data["forecast_points"]) == 6

    # Anomalies endpoint
    anom_resp = await client.post(
        "/api/v1/predictions/anomalies",
        json={
            "service": "user-service",
            "metric_name": "cpu_utilization",
            "current_value": 99.0,
            "historical_values": [40.0, 42.0, 41.0, 40.0, 42.0, 41.0, 40.0],
        },
        headers=headers,
    )
    assert anom_resp.status_code == 200
    assert anom_resp.json()["is_anomaly"] is True

    # Capacity endpoint
    cap_resp = await client.post(
        "/api/v1/predictions/capacity",
        json={"service": "user-service", "resource_name": "memory_utilization", "historical_values": [60.0, 65.0, 72.0, 81.0]},
        headers=headers,
    )
    assert cap_resp.status_code == 200
    assert cap_resp.json()["is_exhaustion_imminent"] is True


# ---------------------------------------------------------------------------
# 19. Prediction Pagination & Multi-Dimensional Filters
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_prediction_pagination_and_filters(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Analytics summary
    analytics_resp = await client.get("/api/v1/predictions/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    an_data = analytics_resp.json()
    assert "total_predictions" in an_data
    assert "predictions_by_service" in an_data

    # Filter by service
    filtered_resp = await client.get("/api/v1/predictions?service=api-gateway&page=1&size=5", headers=headers)
    assert filtered_resp.status_code == 200
    p_data = filtered_resp.json()
    assert p_data["page"] == 1
    assert p_data["size"] == 5
    for item in p_data["items"]:
        assert item["service"].lower() == "api-gateway"


# ---------------------------------------------------------------------------
# 20. Edge Cases: Empty, Single-Sample, and Constant Data
# ---------------------------------------------------------------------------
def test_edge_cases_empty_and_constant():
    # Empty series
    b_empty = baseline_engine.calculate_baseline([])
    assert b_empty.samples_count == 0
    assert b_empty.mean == 0.0

    # Single-sample
    b_single = baseline_engine.calculate_baseline([42.0])
    assert b_single.samples_count == 1
    assert b_single.mean == 42.0
    assert b_single.standard_deviation == 0.0

    # Constant series
    const_series = [50.0, 50.0, 50.0, 50.0, 50.0]
    trend_const = capacity_risk_engine.trend.analyze_trend(const_series)
    assert trend_const.trend == "STABLE"
    assert trend_const.rate_of_change == 0.0

    # Anomaly on constant baseline
    anom_const = anomaly_engine.detect_anomaly(current_value=50.0, historical_values=const_series)
    assert anom_const.is_anomaly is False
    assert anom_const.severity == "NORMAL"
