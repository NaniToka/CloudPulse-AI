"""
Unit and integration test suite for FinOps Executive Intelligence & Cost Reporting.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient

from app.services.cost_engine import (
    analyze_cost_drivers,
    calculate_budget_crossing_projection,
    calculate_finops_health_score,
    calculate_period_comparison,
    calculate_savings_center_breakdown,
    generate_executive_cost_summary,
)

def unique_payload() -> dict:
    return {
        "email": f"execuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Executive",
        "last_name": "Tester",
    }

async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ── 1. Unit Tests for Executive Intelligence Engines ──────────────────────────

@pytest.mark.asyncio
async def test_calculate_finops_health_score_unit():
    res = calculate_finops_health_score(
        monthly_cost=10000.0,
        potential_savings=1000.0,
        anomalies_count=2,
        critical_anomalies_count=1,
        budget_utilization_pct=85.0,
        projected_variance_pct=4.2,
    )
    assert res["score"] > 0
    assert res["status"] in ("Healthy", "Watch", "At Risk", "Critical")
    assert len(res["factors"]) == 4

@pytest.mark.asyncio
async def test_generate_executive_cost_summary_unit():
    svc_breakdown = [{"service": "EC2 Compute", "cost": 5000.0, "percentage": 50.0}]
    recs = [{"estimated_savings": 500.0, "status": "active"}]
    anomalies = [{"severity": "CRITICAL"}]
    summary = generate_executive_cost_summary(10000.0, 9000.0, 11.1, svc_breakdown, recs, anomalies)
    assert summary["monthly_cost"] == 10000.0
    assert len(summary["summary_statements"]) >= 4

@pytest.mark.asyncio
async def test_analyze_cost_drivers_unit():
    costs = [
        {"cost": 3000.0, "provider": "aws", "service": "EC2", "region": "us-east-1", "resource_name": "prod-db"},
        {"cost": 1500.0, "provider": "gcp", "service": "GKE", "region": "us-central1", "resource_name": "k8s-node"},
    ]
    anomalies = [{"resource": "prod-db", "difference": 500.0, "explanation": "Spike"}]
    recs = [{"title": "Rightsize EC2", "estimated_savings": 400.0, "description": "Reduce size", "status": "active"}]

    drivers = analyze_cost_drivers(costs, anomalies, recs)
    assert drivers["top_provider"]["name"] == "AWS"
    assert drivers["top_service"]["name"] == "EC2"

@pytest.mark.asyncio
async def test_calculate_period_comparison_unit():
    current_costs = [{"cost": 4000.0, "provider": "aws", "service": "EC2"}]
    res = calculate_period_comparison(current_costs, 3500.0)
    assert res["current_spend"] == 4000.0
    assert res["previous_spend"] == 3500.0

@pytest.mark.asyncio
async def test_calculate_budget_crossing_projection_unit():
    daily_trend = [{"cost": 100.0} for _ in range(10)]
    proj = calculate_budget_crossing_projection(5000.0, 3000.0, daily_trend)
    assert proj["budget_crossed"] is False
    assert proj["burn_rate_daily"] == 100.0

@pytest.mark.asyncio
async def test_calculate_savings_center_breakdown_unit():
    recs = [
        {"estimated_savings": 400.0, "provider": "AWS", "recommendation_type": "rightsizing", "service": "EC2", "status": "active"},
        {"estimated_savings": 200.0, "provider": "GCP", "recommendation_type": "idle_resource", "service": "Cloud Storage", "status": "active"},
    ]
    sc = calculate_savings_center_breakdown(recs)
    assert sc["total_monthly_savings"] == 600.0
    assert sc["total_annual_savings"] == round(600.0 * 12.0, 2)
    assert sc["opportunity_count"] == 2

# ── 2. Integration Tests for Executive FinOps Endpoints ─────────────────────

@pytest.mark.asyncio
async def test_executive_health_score_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/health-score", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "score" in data

@pytest.mark.asyncio
async def test_executive_summary_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/executive-summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "summary_statements" in data

@pytest.mark.asyncio
async def test_cost_drivers_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/drivers", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_provider" in data

@pytest.mark.asyncio
async def test_period_comparison_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/period-comparison", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "current_spend" in data

@pytest.mark.asyncio
async def test_cost_explorer_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/explorer", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data

@pytest.mark.asyncio
async def test_savings_center_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    res = await client.get("/api/v1/cost/savings-center", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_annual_savings"] == round(data["total_monthly_savings"] * 12.0, 2)

@pytest.mark.asyncio
async def test_finops_report_generate_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    rep_res = await client.post("/api/v1/cost/reports/generate", json={"date_range": "30_days"}, headers=headers)
    assert rep_res.status_code == 200, rep_res.text

@pytest.mark.asyncio
async def test_finops_report_pdf_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    pdf_res = await client.get("/api/v1/cost/reports/pdf?date_range=30_days", headers=headers)
    assert pdf_res.status_code == 200, pdf_res.text
    assert pdf_res.headers["content-type"] == "application/pdf"

@pytest.mark.asyncio
async def test_finops_export_csv_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    csv_res = await client.get("/api/v1/cost/export?format=csv", headers=headers)
    assert csv_res.status_code == 200, csv_res.text
    assert "text/csv" in csv_res.headers["content-type"]
