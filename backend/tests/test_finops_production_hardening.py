"""
Comprehensive unit and integration test suite for FinOps Production Hardening & Data Quality.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient

from app.services.cost_engine import (
    calculate_cost_forecast,
    calculate_efficiency_score,
    calculate_savings_summary,
    detect_cost_anomalies,
    evaluate_budget,
)

def unique_payload() -> dict:
    return {
        "email": f"finopsuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "FinOps",
        "last_name": "Tester",
    }

async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ── 1. Unit Tests for Financial Calculation Safety ──────────────────────────

@pytest.mark.asyncio
async def test_calculate_efficiency_score_edge_cases():
    assert calculate_efficiency_score(0.0, 500.0) == 100
    assert calculate_efficiency_score(-100.0, 50.0) == 100
    assert calculate_efficiency_score(1000.0, 0.0) == 100
    assert calculate_efficiency_score(1000.0, 500.0) == 50

@pytest.mark.asyncio
async def test_calculate_savings_summary_annual_derivation():
    recs = [
        {"estimated_savings": 500.0, "status": "active"},
        {"estimated_savings": 250.50, "status": "active"},
        {"estimated_savings": 100.0, "status": "dismissed"},
    ]
    res = calculate_savings_summary(recs)
    assert res["total_monthly_savings"] == 750.50
    assert res["total_annual_savings"] == round(750.50 * 12.0, 2)
    assert res["opportunity_count"] == 2

@pytest.mark.asyncio
async def test_evaluate_budget_edge_cases():
    zero_b = evaluate_budget(0.0, 500.0, 525.0)
    assert zero_b["budget"] == 0.0
    assert zero_b["threshold_status"] == "EXCEEDED_100"
    assert zero_b["remaining"] == 0.0

    norm_b = evaluate_budget(10000.0, 4000.0, 4200.0)
    assert norm_b["utilization_pct"] == 40.0
    assert norm_b["remaining"] == 6000.0
    assert norm_b["threshold_status"] == "NORMAL"

@pytest.mark.asyncio
async def test_detect_cost_anomalies_unit():
    costs = [
        {"cost": 1000.0, "status": "active", "resource_name": "r1", "service": "s1", "provider": "aws"},
        {"cost": 1200.0, "status": "active", "resource_name": "r2", "service": "s1", "provider": "aws"},
        {"cost": 4500.0, "status": "idle", "resource_name": "r3-idle", "service": "s2", "provider": "gcp"},
    ]
    anomalies = detect_cost_anomalies(costs)
    assert len(anomalies) > 0
    top = anomalies[0]
    assert top["resource"] == "r3-idle"
    assert top["severity"] in ("CRITICAL", "HIGH", "MEDIUM")

@pytest.mark.asyncio
async def test_calculate_cost_forecast_unit():
    trend = [{"cost": 100.0 + i * 2.0} for i in range(10)]
    fc = calculate_cost_forecast(trend, 3000.0)
    assert fc["forecast_7_day"] > 0
    assert fc["forecast_30_day"] > 0
    assert "historical_basis" in fc

# ── 2. Integration Tests for API Provider & Date Filtering ──────────────────

@pytest.mark.asyncio
async def test_finops_overview_provider_filtering(client: AsyncClient):
    headers = await get_auth_headers(client)

    res_aws = await client.get("/api/v1/cost/overview?provider=aws", headers=headers)
    assert res_aws.status_code == 200
    data_aws = res_aws.json()
    assert "monthly_cost" in data_aws

    res_gcp = await client.get("/api/v1/cost/overview?provider=gcp", headers=headers)
    assert res_gcp.status_code == 200

@pytest.mark.asyncio
async def test_finops_trends_date_range_filtering(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/trends?date_range=7_days", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["daily_trend"]) == 7

@pytest.mark.asyncio
async def test_finops_budget_crud_hardening(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {
        "name": "Hardened Security Test Budget",
        "amount": 25000.0,
        "provider": "aws",
        "service": "all",
        "period": "monthly",
        "threshold_percentages": [50, 75, 90, 100],
    }
    create_res = await client.post("/api/v1/cost/budgets", json=payload, headers=headers)
    assert create_res.status_code == 201
    created = create_res.json()
    b_id = created["id"]
    assert created["amount"] == 25000.0

    update_payload = {
        "name": "Hardened Security Test Budget Updated",
        "amount": 30000.0,
        "provider": "aws",
    }
    update_res = await client.put(f"/api/v1/cost/budgets/{b_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["amount"] == 30000.0

@pytest.mark.asyncio
async def test_finops_anomalies_and_savings_api(client: AsyncClient):
    headers = await get_auth_headers(client)

    anom_res = await client.get("/api/v1/cost/anomalies", headers=headers)
    assert anom_res.status_code == 200

    sav_res = await client.get("/api/v1/cost/savings", headers=headers)
    assert sav_res.status_code == 200
    sav_data = sav_res.json()
    assert sav_data["total_annual_savings"] == round(sav_data["total_monthly_savings"] * 12.0, 2)
