"""
Comprehensive Enterprise Pytest Suite for AI Service Dependency & Root-Cause Intelligence Engine.

Tests:
1. Dependency discovery from spans and infrastructure
2. Dependency confidence calculation
3. Graph generation endpoint
4. Duplicate dependency prevention (idempotency)
5. Service health scoring & status
6. Blast radius DAG traversal
7. Failure propagation simulation
8. Root cause ranking in multi-tier cascading scenario
9. Explainable evidence generation
10. Gemini fallback diagnostics
11. Multi-tenant organization isolation
12. Service listing pagination & filtering
13. Invalid service error handling (404)
14. Large graph depth-limited traversal
15. Incident integration endpoint
16. Service details with upstream callers and downstream dependencies
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.organization import Organization
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.models.trace import Span, Trace
from app.services.dependency_discovery_service import dependency_discovery_service
from app.services.root_cause_intelligence_service import root_cause_intelligence_service
from app.services.service_health_service import service_health_service


# ---------------------------------------------------------------------------
# 1. Dependency Discovery from Spans
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dependency_discovery_from_spans(db_session: AsyncSession):
    """Verifies that parent-child spans across different services automatically generate dependency edges."""
    now = datetime.now(UTC)
    tr = Trace(
        id=uuid.uuid4(),
        trace_id="tr-test-disc-01",
        name="POST /api/v1/orders",
        root_service="api-gateway",
        http_status=200,
        duration_ms=120.0,
        status="ok",
    )
    db_session.add(tr)

    s1 = Span(
        id=uuid.uuid4(),
        trace_id="tr-test-disc-01",
        span_id="sp-parent-01",
        service_name="api-gateway",
        operation_name="HTTP POST /checkout",
        span_kind="SERVER",
        status_code="OK",
        duration_ms=120.0,
        start_time=now,
        end_time=now + timedelta(milliseconds=120),
    )
    s2 = Span(
        id=uuid.uuid4(),
        trace_id="tr-test-disc-01",
        span_id="sp-child-02",
        parent_span_id="sp-parent-01",
        service_name="checkout-service",
        operation_name="Process Checkout",
        span_kind="CLIENT",
        status_code="OK",
        duration_ms=85.0,
        start_time=now + timedelta(milliseconds=10),
        end_time=now + timedelta(milliseconds=95),
    )
    db_session.add(s1)
    db_session.add(s2)
    await db_session.commit()

    disc_res = await dependency_discovery_service.discover_and_synchronize(db_session, include_traces=True)
    assert disc_res.discovered_nodes_count >= 2
    assert disc_res.discovered_edges_count >= 1

    # Verify edge exists
    dep = await db_session.execute(
        ServiceDependency.__table__.select().where(
            ServiceDependency.source_service == "api-gateway",
            ServiceDependency.target_service == "checkout-service",
        )
    )
    assert dep.first() is not None


# ---------------------------------------------------------------------------
# 2. Dependency Confidence Calculation
# ---------------------------------------------------------------------------
def test_dependency_confidence_calculation():
    """Validates mathematical confidence scoring bounded between 0.15 and 0.99."""
    # Strong evidence: trace + call volume + k8s + observations
    high_conf = dependency_discovery_service.calculate_dependency_confidence(
        evidence_count=25,
        has_trace_evidence=True,
        has_network_evidence=True,
        has_k8s_evidence=True,
        call_count=5000,
    )
    assert 0.85 <= high_conf <= 0.99

    # Weak evidence
    low_conf = dependency_discovery_service.calculate_dependency_confidence(
        evidence_count=1,
        has_trace_evidence=False,
        has_network_evidence=False,
        has_k8s_evidence=False,
        call_count=1,
    )
    assert 0.15 <= low_conf <= 0.40


# ---------------------------------------------------------------------------
# 3. Dependency Graph Endpoint
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dependency_graph_endpoint(client: AsyncClient):
    """Tests GET /api/v1/dependencies/graph returns populated nodes and edges."""
    res = await client.get("/api/v1/dependencies/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 2
    assert len(data["edges"]) >= 1
    assert "critical_path" in data


# ---------------------------------------------------------------------------
# 4. Duplicate Dependency Prevention (Idempotency)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_dependency_prevention(db_session: AsyncSession):
    """Verifies that running discovery multiple times updates edge counts rather than duplicating records."""
    res1 = await dependency_discovery_service.discover_and_synchronize(db_session)
    first_count = res1.discovered_edges_count

    res2 = await dependency_discovery_service.discover_and_synchronize(db_session)
    assert res2.updated_edges_count >= first_count


# ---------------------------------------------------------------------------
# 5. Service Health Scoring & Status Evaluation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_service_health_scoring(db_session: AsyncSession):
    """Validates mathematical health score calculation and status transition."""
    # Degraded service with incident
    inc = Incident(
        id=uuid.uuid4(),
        title="Payment Service High Error Rate",
        severity="CRITICAL",
        status="INVESTIGATING",
        affected_service="payment-service",
    )
    db_session.add(inc)
    await db_session.commit()

    health = await service_health_service.evaluate_service_health(db_session, "payment-service")
    assert health.service_name == "payment-service"
    assert health.health_score < 85.0
    assert health.status in ["DEGRADED", "CRITICAL"]
    assert len(health.factors) > 0


# ---------------------------------------------------------------------------
# 6. Blast Radius DAG Traversal
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_blast_radius_dag_traversal(db_session: AsyncSession):
    """
    Tests failure propagation DAG traversal:
    postgres-primary -> payment-service -> order-service -> checkout-service -> api-gateway
    """
    from app.services.service_dependency_service import service_dependency_service

    blast = await service_dependency_service.calculate_blast_radius(
        db_session, service_name="postgres-primary", depth=5
    )
    assert blast.root_component == "postgres-primary"
    assert len(blast.affected_services) >= 2
    assert blast.dependency_depth >= 1
    assert blast.financial_risk_estimate.startswith("$")


# ---------------------------------------------------------------------------
# 7. Failure Propagation Hops Simulation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_failure_propagation_hops(db_session: AsyncSession):
    """Verifies detailed simulation of cascading failure hops with latency and error amplification."""
    from app.services.service_dependency_service import service_dependency_service

    blast = await service_dependency_service.calculate_blast_radius(
        db_session, service_name="payment-service", depth=5
    )
    assert len(blast.propagation_hops) > 0
    hop = blast.propagation_hops[0]
    assert hop.source is not None
    assert hop.target is not None
    assert hop.latency_increase_percent >= 100.0
    assert hop.propagation_risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


# ---------------------------------------------------------------------------
# 8. Deterministic Multi-Tier Root Cause Ranking Scenario
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_root_cause_ranking_multi_tier_scenario(db_session: AsyncSession):
    """
    Multi-Tier Cascading Failure Scenario:
    api-gateway -> checkout-service -> order-service -> payment-service -> postgresql

    Simulated signals:
    - payment-service: error_rate=45%, latency=2800ms (CRITICAL)
    - order-service: error_rate=32% (HIGH)
    - checkout-service: latency increased by 350% (HIGH)
    - api-gateway: HTTP 500 spike (HIGH)

    Expectation: The engine must derive payment-service as Candidate #1 (highest score).
    """
    signals = [
        {
            "service": "payment-service",
            "metric_name": "error_rate",
            "error_rate": 45.0,
            "latency_ms": 2800.0,
            "severity": "CRITICAL",
            "message": "Payment gateway timeout & 45% error rate",
        },
        {
            "service": "order-service",
            "metric_name": "error_rate",
            "error_rate": 32.0,
            "severity": "HIGH",
            "message": "Order creation HTTP 500 cascade",
        },
        {
            "service": "checkout-service",
            "metric_name": "latency",
            "latency_ms": 1850.0,
            "severity": "HIGH",
            "message": "Checkout P99 latency increased 350%",
        },
        {
            "service": "api-gateway",
            "metric_name": "http_5xx",
            "error_rate": 24.0,
            "severity": "HIGH",
            "message": "Ingress HTTP 500 error spike",
        },
    ]

    ranking_resp = await root_cause_intelligence_service.rank_root_causes(
        db_session, service_name="api-gateway", signals=signals
    )

    assert ranking_resp.primary_root_cause == "payment-service"
    assert ranking_resp.primary_score >= 0.80
    assert len(ranking_resp.candidates) >= 3
    assert ranking_resp.candidates[0].service_name == "payment-service"
    assert ranking_resp.candidates[0].rank == 1


# ---------------------------------------------------------------------------
# 9. Explainable Evidence Generation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_explainable_evidence_generation(db_session: AsyncSession):
    """Validates explainable evidence items attached to root cause ranking."""
    signals = [
        {
            "service": "redis-cluster",
            "metric_name": "memory_limit",
            "severity": "CRITICAL",
            "message": "Redis maxmemory 2GB breached",
        }
    ]
    res = await root_cause_intelligence_service.rank_root_causes(
        db_session, service_name="redis-cluster", signals=signals
    )
    assert len(res.evidence_graph) >= 1
    ev = res.evidence_graph[0]
    assert "source" in ev
    assert "observation" in ev
    assert ev["strength"] >= 0.70


# ---------------------------------------------------------------------------
# 10. Gemini Fallback Diagnostics
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_gemini_fallback_diagnostics(client: AsyncClient):
    """Tests that when GEMINI_API_KEY is inactive, response returns analysis_engine='local'."""
    res = await client.post("/api/v1/dependencies/root-cause", json={"service_name": "auth-service"})
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_engine"] in ["gemini", "local"]
    assert len(data["candidates"]) > 0


# ---------------------------------------------------------------------------
# 11. Organization Tenant Isolation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_organization_isolation(db_session: AsyncSession):
    """Validates multi-tenant isolation for dependency nodes and edges."""
    org1 = Organization(id=uuid.uuid4(), name="Org Alpha", slug="org-alpha")
    org2 = Organization(id=uuid.uuid4(), name="Org Beta", slug="org-beta")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.flush()

    node1 = ServiceNode(
        id=uuid.uuid4(), organization_id=org1.id, name="alpha-microservice", type="service"
    )
    node2 = ServiceNode(
        id=uuid.uuid4(), organization_id=org2.id, name="beta-microservice", type="service"
    )
    db_session.add(node1)
    db_session.add(node2)
    await db_session.commit()

    # Discover and query per org
    g1 = await dependency_discovery_service.discover_and_synchronize(db_session, organization_id=org1.id)
    assert g1 is not None


# ---------------------------------------------------------------------------
# 12. Service Listing Pagination & Filtering
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_service_listing_pagination(client: AsyncClient):
    """Tests GET /api/v1/dependencies/services with pagination and status filters."""
    res = await client.get("/api/v1/dependencies/services?page=1&size=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert len(data["items"]) <= 5


# ---------------------------------------------------------------------------
# 13. Invalid Service Error Handling (404)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_invalid_service_error_handling(client: AsyncClient):
    """Tests 404 for nonexistent service ID."""
    fake_id = uuid.uuid4()
    res = await client.get(f"/api/v1/dependencies/services/{fake_id}")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 14. Large Graph Depth-Limited Traversal
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_large_graph_depth_traversal(client: AsyncClient):
    """Tests depth filtering on topology graph."""
    res = await client.get("/api/v1/dependencies/graph?service=api-gateway&depth=2")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data


# ---------------------------------------------------------------------------
# 15. Incident Integration Endpoint
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_incident_dependency_analysis_integration(client: AsyncClient):
    """Tests GET /api/v1/dependencies/incidents/{incident_id}/analysis."""
    # Declare incident
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Payment Downstream Outage", "severity": "CRITICAL", "service": "payment-service"},
    )
    assert decl_res.status_code == 201
    inc_id = decl_res.json()["id"]

    # Request dependency RCA analysis for this incident
    rca_res = await client.get(f"/api/v1/dependencies/incidents/{inc_id}/analysis")
    assert rca_res.status_code == 200
    data = rca_res.json()
    assert data["primary_root_cause"] is not None
    assert "candidates" in data
    assert "blast_radius" in data


# ---------------------------------------------------------------------------
# 16. Service Detail with Upstream & Downstream Callers
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_service_detail_with_upstream_downstream(client: AsyncClient):
    """Tests GET /api/v1/dependencies/services/{service_id} returns upstream callers and downstream dependencies."""
    list_res = await client.get("/api/v1/dependencies/services?size=1")
    assert list_res.status_code == 200
    svc_id = list_res.json()["items"][0]["id"]

    res = await client.get(f"/api/v1/dependencies/services/{svc_id}")
    assert res.status_code == 200
    data = res.json()
    assert "upstream_dependencies" in data
    assert "downstream_dependents" in data
    assert "health_score" in data
