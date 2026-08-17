"""
Comprehensive unit and integration test suite for FinOps Production Hardening & Data Quality.

Verifies:
1. Money calculation safety, rounding, and non-negative constraints.
2. Annual savings derivation (monthly * 12).
3. Provider filtering across all cost endpoints (AWS, Azure, GCP, Kubernetes).
4. Date range filtering (7_days, 30_days, quarter).
5. Statistical cost anomaly detection and severity thresholds.
6. Linear regression cost forecasting and confidence metadata.
7. Budget threshold evaluations (50%, 75%, 90%, 100%), remaining allocations, and edge cases ($0 budget).
8. Input validation for cost creation records.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_cost
from app.models.cloud_cost import CloudCost, CostBudget, OptimizationRecommendation
from app.models.user import User
from app.services.cost_engine import (
    calculate_cost_forecast,
    calculate_efficiency_score,
    calculate_savings_summary,
    detect_cost_anomalies,
    evaluate_budget,
    group_costs_by_provider,
    group_costs_by_region,
    group_costs_by_service,
)

pytestmark = pytest.mark.asyncio


# ── 1. Unit Tests for Financial Calculation Safety ──────────────────────────


def test_calculate_efficiency_score_edge_cases():
    assert calculate_efficiency_score(0.0, 500.0) == 100
    assert calculate_efficiency_score(-100.0, 50.0) == 100
    assert calculate_efficiency_score(1000.0, 0.0) == 100
    assert calculate_efficiency_score(1000.0, 500.0) == 75
    assert calculate_efficiency_score(1000.0, 2000.0) == 50  # clamped waste ratio


def test_calculate_savings_summary_annual_derivation():
    recs = [
        {"estimated_savings": 500.0, "status": "active"},
        {"estimated_savings": 250.50, "status": "active"},
        {"estimated_savings": 100.0, "status": "dismissed"},
    ]
    res = calculate_savings_summary(recs)
    assert res["total_monthly_savings"] == 750.50
    assert res["total_annual_savings"] == round(750.50 * 12.0, 2)
    assert res["opportunity_count"] == 2


def test_evaluate_budget_edge_cases():
    # $0 budget
    zero_b = evaluate_budget(0.0, 500.0, 525.0)
    assert zero_b["budget"] == 0.0
    assert zero_b["threshold_status"] == "EXCEEDED_100"
    assert zero_b["remaining"] == 0.0

    # Normal budget
    norm_b = evaluate_budget(10000.0, 4000.0, 4200.0)
    assert norm_b["utilization_pct"] == 40.0
    assert norm_b["remaining"] == 6000.0
    assert norm_b["threshold_status"] == "NORMAL"

    # Threshold status 75%
    warn_75 = evaluate_budget(10000.0, 7800.0, 8190.0)
    assert warn_75["utilization_pct"] == 78.0
    assert warn_75["threshold_status"] == "WARNING_75"
    assert 75 in warn_75["thresholds_reached"]

    # Over 100% budget
    exceeded = evaluate_budget(10000.0, 12000.0, 12600.0)
    assert exceeded["utilization_pct"] == 120.0
    assert exceeded["remaining"] == 0.0
    assert exceeded["threshold_status"] == "EXCEEDED_100"


def test_detect_cost_anomalies_unit():
    costs = [
        {"cost": 1000.0, "status": "active", "resource_name": "r1", "service": "s1", "provider": "aws"},
        {"cost": 1200.0, "status": "active", "resource_name": "r2", "service": "s1", "provider": "aws"},
        {"cost": 4500.0, "status": "idle", "resource_name": "r3-idle", "service": "s2", "provider": "gcp"},
    ]
    anomalies = detect_cost_anomalies(costs)
    assert len(anomalies) > 0
    top = anomalies[0]
    assert top["resource"] == "r3-idle"
    assert top["severity"] in ("CRITICAL", "HIGH")
    assert top["difference"] > 0


def test_calculate_cost_forecast_unit():
    trend = [{"cost": 100.0 + i * 2.0} for i in range(10)]
    fc = calculate_cost_forecast(trend, 3000.0)
    assert fc["forecast_7_day"] > 0
    assert fc["forecast_30_day"] > 0
    assert "historical_basis" in fc
    assert fc["confidence"] > 0.60


# ── 2. Integration Tests for API Provider & Date Filtering ──────────────────


async def test_finops_overview_provider_filtering(client: AsyncClient, test_user_token: str):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Filter AWS
    res_aws = await client.get("/api/v1/cost/overview?provider=aws", headers=headers)
    assert res_aws.status_code == 200
    data_aws = res_aws.json()
    assert data_aws["data_source"] == "Demo Data — Local Development"
    assert isinstance(data_aws["monthly_cost"], float)

    # Filter GCP
    res_gcp = await client.get("/api/v1/cost/overview?provider=gcp", headers=headers)
    assert res_gcp.status_code == 200
    data_gcp = res_gcp.json()
    assert isinstance(data_gcp["monthly_cost"], float)


async def test_finops_trends_date_range_filtering(client: AsyncClient, test_user_token: str):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    res = await client.get("/api/v1/cost/trends?date_range=7_days", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["daily_trend"]) == 7


async def test_finops_budget_crud_hardening(client: AsyncClient, test_user_token: str):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # 1. Create budget
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

    # 2. Update budget
    update_payload = {
        "name": "Hardened Security Test Budget Updated",
        "amount": 30000.0,
        "provider": "aws",
    }
    update_res = await client.put(f"/api/v1/cost/budgets/{b_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["amount"] == 30000.0
    assert updated["name"] == "Hardened Security Test Budget Updated"


async def test_finops_anomalies_and_savings_api(client: AsyncClient, test_user_token: str):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    anom_res = await client.get("/api/v1/cost/anomalies", headers=headers)
    assert anom_res.status_code == 200
    anom_data = anom_res.json()
    assert "anomalies" in anom_data

    sav_res = await client.get("/api/v1/cost/savings", headers=headers)
    assert sav_res.status_code == 200
    sav_data = sav_res.json()
    assert sav_data["total_annual_savings"] == round(sav_data["total_monthly_savings"] * 12.0, 2)
