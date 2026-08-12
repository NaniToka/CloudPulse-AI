"""
Pytest Suite for Enterprise FinOps & Cost Intelligence Center:
- Cost Provider, Service, Region Aggregations
- Cost Anomaly Engine
- Cost Forecast Engine
- Budget Intelligence & Threshold Evaluation
- Savings Engine (Annual = Monthly * 12)
- API Endpoints (/overview, /trends, /providers, /services, /regions, /anomalies, /forecast, /budgets, /savings, /analyze)
"""

import uuid

import pytest
from httpx import AsyncClient

from app.services.cost_engine import (
    calculate_cost_forecast,
    calculate_savings_summary,
    detect_cost_anomalies,
    evaluate_budget,
    group_costs_by_provider,
    group_costs_by_region,
    group_costs_by_service,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"finopsuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "FinOps",
        "last_name": "Tester",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_cost_aggregation_engines():
    """Verify group_costs_by_provider, group_costs_by_service, and group_costs_by_region."""
    sample_costs = [
        {"cost": 4850.0, "provider": "aws", "service": "AWS EC2", "region": "us-east-1"},
        {"cost": 3100.0, "provider": "azure", "service": "Azure Virtual Machines", "region": "eastus"},
        {"cost": 28450.0, "provider": "gcp", "service": "Google Kubernetes Engine", "region": "us-central1"},
        {"cost": 5400.0, "provider": "kubernetes", "service": "Kubernetes Compute", "region": "us-central1"},
    ]

    providers = group_costs_by_provider(sample_costs)
    assert len(providers) == 4
    provider_names = {p["provider"] for p in providers}
    assert "AWS" in provider_names
    assert "Azure" in provider_names
    assert "GCP" in provider_names
    assert "Kubernetes" in provider_names

    services = group_costs_by_service(sample_costs)
    assert len(services) == 4

    regions = group_costs_by_region(sample_costs)
    assert len(regions) >= 2


@pytest.mark.asyncio
async def test_cost_anomaly_detection_engine():
    """Verify deterministic cost anomaly detection."""
    sample_costs = [
        {"cost": 100.0, "status": "active", "resource_name": "normal-vm", "service": "EC2", "provider": "aws"},
        {"cost": 150.0, "status": "active", "resource_name": "normal-db", "service": "RDS", "provider": "aws"},
        {"cost": 4200.0, "status": "idle", "resource_name": "idle-heavy-node", "service": "GKE", "provider": "gcp"},
        {"cost": 8500.0, "status": "active", "resource_name": "spiking-bigquery-job", "service": "BigQuery", "provider": "gcp"},
    ]
    anomalies = detect_cost_anomalies(sample_costs)
    assert len(anomalies) >= 1
    top_anomaly = anomalies[0]
    assert "anomaly_score" in top_anomaly
    assert top_anomaly["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    assert top_anomaly["actual_cost"] > top_anomaly["expected_cost"]


@pytest.mark.asyncio
async def test_cost_forecast_engine():
    """Verify 7-day, 30-day, and month-end forecast calculation."""
    daily_trend = [
        {"date": f"2026-08-{i:02d}", "cost": 2500.0 + (i * 20.0)} for i in range(1, 15)
    ]
    forecast = calculate_cost_forecast(daily_trend, monthly_cost=75000.0)

    assert "forecast_7_day" in forecast
    assert "forecast_30_day" in forecast
    assert "projected_month_end" in forecast
    assert forecast["confidence"] > 0.5
    assert forecast["trend_direction"] in ("increasing", "decreasing", "stable")


@pytest.mark.asyncio
async def test_budget_evaluation_engine():
    """Verify threshold evaluation (50%, 75%, 90%, 100%) and remaining budget calculation."""
    res = evaluate_budget(budget_amount=10000.0, current_spend=7800.0, projected_spend=9200.0)
    assert res["utilization_pct"] == 78.0
    assert res["remaining"] == 2200.0
    assert res["threshold_status"] == "WARNING_75"
    assert 50 in res["thresholds_reached"]
    assert 75 in res["thresholds_reached"]


@pytest.mark.asyncio
async def test_savings_summary_engine():
    """Verify annual savings equals monthly savings * 12."""
    recs = [
        {"estimated_savings": 500.0, "status": "active"},
        {"estimated_savings": 1200.0, "status": "active"},
        {"estimated_savings": 300.0, "status": "dismissed"},
    ]
    res = calculate_savings_summary(recs)
    assert res["total_monthly_savings"] == 1700.0
    assert res["total_annual_savings"] == 20400.0  # 1700 * 12
    assert res["opportunity_count"] == 2


@pytest.mark.asyncio
async def test_api_get_cost_overview(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/overview endpoint."""
    resp = await client.get("/api/v1/cost/overview", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "monthly_cost" in data
    assert "provider_breakdown" in data
    assert "data_source" in data
    assert "Demo Data" in data["data_source"]


@pytest.mark.asyncio
async def test_api_get_cost_trends(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/trends endpoint."""
    resp = await client.get("/api/v1/cost/trends", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "daily_trend" in data
    assert "projected_cost" in data


@pytest.mark.asyncio
async def test_api_get_cost_providers(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/providers endpoint."""
    resp = await client.get("/api/v1/cost/providers", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "providers" in data
    assert "total_cost" in data


@pytest.mark.asyncio
async def test_api_get_cost_anomalies(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/anomalies endpoint."""
    resp = await client.get("/api/v1/cost/anomalies", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "anomalies" in data
    assert "total_anomalies" in data


@pytest.mark.asyncio
async def test_api_get_cost_forecast(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/forecast endpoint."""
    resp = await client.get("/api/v1/cost/forecast", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "forecast_7_day" in data
    assert "confidence" in data


@pytest.mark.asyncio
async def test_api_budget_crud(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET, POST, and PUT /api/v1/cost/budgets endpoints."""
    # List budgets
    list_resp = await client.get("/api/v1/cost/budgets", headers=auth_headers)
    assert list_resp.status_code == 200, list_resp.text
    budgets = list_resp.json()["budgets"]
    assert len(budgets) >= 1

    # Create budget
    create_payload = {
        "name": "Test FinOps Team Budget",
        "amount": 25000.0,
        "provider": "aws",
        "service": "all",
        "environment": "production",
        "period": "monthly",
    }
    create_resp = await client.post("/api/v1/cost/budgets", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["name"] == "Test FinOps Team Budget"
    assert created["amount"] == 25000.0

    # Update budget
    budget_id = created["id"]
    update_resp = await client.put(
        f"/api/v1/cost/budgets/{budget_id}",
        json={"name": "Updated FinOps Budget", "amount": 30000.0},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["amount"] == 30000.0


@pytest.mark.asyncio
async def test_api_get_cost_savings(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/cost/savings endpoint."""
    resp = await client.get("/api/v1/cost/savings", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "total_monthly_savings" in data
    assert "total_annual_savings" in data
    assert data["total_annual_savings"] == round(data["total_monthly_savings"] * 12.0, 2)
