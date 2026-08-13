"""
Pytest suite for Enterprise Executive Intelligence & Operations Command Center:
- Deterministic Executive Health Score & Transparent Contributors
- Operational Risk Score & Top Affected Services
- Business Impact Translation & Unquantifiable Fallbacks
- Cross-Domain Signal Correlation (Incidents + SLO + FinOps + Security + Capacity)
- Top 5 Risks Ranking Engine
- Top Opportunities Aggregation
- AI & Local Executive Brief Generation (Dual Mode)
- Unified Change Timeline Stream
- Executive Operational Trend Indicators
- REST API Endpoints (/command-center/*) with Auth & Filters
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import command_center_engine


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"exec-cmd-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Exec",
        "last_name": "Commander",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_command_center_engine_health_score(db_session: AsyncSession):
    """Test deterministic health score calculation and transparent contributors."""
    health = await command_center_engine.calculate_executive_health_score(db_session)
    print("HEALTH PAYLOAD:", health)
    assert "overall_health_score" in health
    assert 0.0 <= health["overall_health_score"] <= 100.0
    assert health["status"] in ["HEALTHY", "DEGRADED", "AT_RISK", "CRITICAL"]
    assert len(health["contributing_factors"]) >= 1


@pytest.mark.asyncio
async def test_command_center_engine_operational_risk(db_session: AsyncSession):
    """Test operational risk score calculation and risk level."""
    risk = await command_center_engine.calculate_operational_risk_score(db_session)
    assert "operational_risk_score" in risk
    assert 0.0 <= risk["operational_risk_score"] <= 100.0
    assert risk["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(risk["affected_services"], list)


@pytest.mark.asyncio
async def test_command_center_business_impact():
    """Test technical to business impact translation and fallback."""
    impact_pay = command_center_engine.translate_business_impact("availability", service="payment-service")
    assert "checkout disruption" in impact_pay

    impact_cost = command_center_engine.translate_business_impact("cost", service="analytics-service")
    assert "budget overrun" in impact_cost

    impact_unknown = command_center_engine.translate_business_impact("unknown_cat", service="unknown_svc")
    assert impact_unknown == "Business impact cannot be quantified from available telemetry."


@pytest.mark.asyncio
async def test_command_center_cross_domain_correlation(db_session: AsyncSession):
    """Test cross-domain signal correlation across SLO, FinOps, Security, Capacity."""
    insights = await command_center_engine.correlate_cross_domain_insights(db_session)
    assert len(insights) >= 3
    categories = [i["category"] for i in insights]
    assert "slo_breach" in categories
    assert "cost_anomaly" in categories
    assert "security_finding" in categories


@pytest.mark.asyncio
async def test_command_center_top_risks_ranking(db_session: AsyncSession):
    """Test top 5 risk ranking engine."""
    insights = await command_center_engine.correlate_cross_domain_insights(db_session)
    top_risks = command_center_engine.rank_top_risks(insights)
    assert len(top_risks) <= 5
    assert top_risks[0]["rank"] == 1
    assert "severity" in top_risks[0]
    assert "score" in top_risks[0]


@pytest.mark.asyncio
async def test_command_center_opportunities_aggregation(db_session: AsyncSession):
    """Test top opportunities aggregation."""
    insights = await command_center_engine.correlate_cross_domain_insights(db_session)
    opps = command_center_engine.aggregate_top_opportunities(insights)
    assert len(opps) >= 3
    sources = [o["source"] for o in opps]
    assert "FinOps Engine" in sources
    assert "SLO Engine" in sources


@pytest.mark.asyncio
async def test_command_center_executive_brief(db_session: AsyncSession):
    """Test AI & Local Executive Brief generation."""
    brief = await command_center_engine.generate_executive_brief(db_session)
    assert "summary" in brief
    assert "top_concern" in brief
    assert "business_impact" in brief
    assert "recommended_action" in brief
    assert "badge" in brief


@pytest.mark.asyncio
async def test_command_center_timeline_stream(db_session: AsyncSession):
    """Test unified change timeline generation."""
    insights = await command_center_engine.correlate_cross_domain_insights(db_session)
    timeline = command_center_engine.build_unified_timeline(insights)
    assert len(timeline) >= 4
    assert "timestamp" in timeline[0]
    assert "event" in timeline[0]


@pytest.mark.asyncio
async def test_command_center_executive_trends():
    """Test executive operational trend indicators."""
    trends = command_center_engine.calculate_executive_trends()
    assert len(trends) >= 5
    assert trends[0]["trend_direction"] in ["IMPROVING", "STABLE", "DEGRADING"]


@pytest.mark.asyncio
async def test_api_command_center_overview_and_endpoints(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /command-center/overview and child endpoints."""
    ov_resp = await client.get("/api/v1/command-center/overview", headers=auth_headers)
    assert ov_resp.status_code == 200, ov_resp.text
    data = ov_resp.json()
    assert "health" in data
    assert "risk" in data
    assert "brief" in data
    assert "top_risks" in data
    assert "opportunities" in data
    assert "timeline" in data
    assert "trends" in data

    h_resp = await client.get("/api/v1/command-center/health", headers=auth_headers)
    assert h_resp.status_code == 200, h_resp.text

    r_resp = await client.get("/api/v1/command-center/risk", headers=auth_headers)
    assert r_resp.status_code == 200, r_resp.text

    i_resp = await client.get("/api/v1/command-center/insights", headers=auth_headers)
    assert i_resp.status_code == 200, i_resp.text

    rk_resp = await client.get("/api/v1/command-center/risks", headers=auth_headers)
    assert rk_resp.status_code == 200, rk_resp.text

    op_resp = await client.get("/api/v1/command-center/opportunities", headers=auth_headers)
    assert op_resp.status_code == 200, op_resp.text

    tl_resp = await client.get("/api/v1/command-center/timeline", headers=auth_headers)
    assert tl_resp.status_code == 200, tl_resp.text

    tr_resp = await client.get("/api/v1/command-center/trends", headers=auth_headers)
    assert tr_resp.status_code == 200, tr_resp.text

    anz_resp = await client.post("/api/v1/command-center/analyze", headers=auth_headers)
    assert anz_resp.status_code == 200, anz_resp.text
    assert "Enterprise Executive Intelligence Analysis Complete" in anz_resp.json()["analysis_summary"]
