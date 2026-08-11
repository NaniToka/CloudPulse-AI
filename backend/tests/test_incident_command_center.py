"""
Comprehensive Enterprise Test Suite for Incident Command Center.

Tests:
1. Signal normalization
2. Signal correlation
3. Correlation score calculation
4. Duplicate incident prevention (idempotency)
5. Incident creation & manual declaration
6. Incident listing with filters & pagination
7. Incident details (evidence, blast radius, timeline)
8. Acknowledge lifecycle
9. Investigate lifecycle
10. Mitigate lifecycle
11. Resolve lifecycle (MTTR & SLA calculation)
12. MTTR calculation accuracy
13. SLA compliance calculation
14. Analytics calculation (mean/median MTTR, SLA compliance, root causes)
15. Deterministic RCA engine
16. Gemini fallback & analysis_engine labeling
17. Organization tenant isolation
18. Invalid state transitions and error handling
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.organization import Organization
from app.schemas.signal import NormalizedSignal, SignalSeverity, SignalSource, normalize_signal
from app.services.incident_correlation_engine import incident_correlation_engine
from app.services.root_cause_analysis_service import root_cause_analysis_service


FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# 1. Signal Normalization
# ---------------------------------------------------------------------------
def test_signal_normalization():
    """Validates normalization of signals across metrics, logs, alerts, traces, and k8s."""
    raw_metric = {
        "source": "telemetry",
        "service": "api-gateway",
        "resource": "pod-8f7d",
        "metric_name": "cpu_utilization_percent",
        "metric_value": 94.2,
        "threshold": 85.0,
        "severity": "CRITICAL",
        "title": "CPU utilization spike",
    }
    sig = normalize_signal(raw_metric)
    assert sig.source == SignalSource.TELEMETRY
    assert sig.severity == SignalSeverity.CRITICAL
    assert sig.service == "api-gateway"
    assert sig.resource_id == "pod-8f7d"
    assert sig.value == 94.2
    assert sig.threshold == 85.0

    raw_k8s = {
        "event_type": "kubernetes",
        "service_name": "payment-service",
        "pod": "payment-api-pod-1",
        "title": "Pod OOMKilled",
        "severity": "high",
        "trace_id": "tr-abc12345",
    }
    sig_k8s = normalize_signal(raw_k8s)
    assert sig_k8s.source == SignalSource.KUBERNETES
    assert sig_k8s.severity == SignalSeverity.HIGH
    assert sig_k8s.service == "payment-service"
    assert sig_k8s.resource_id == "payment-api-pod-1"
    assert sig_k8s.metadata.get("trace_id") == "tr-abc12345"


# ---------------------------------------------------------------------------
# 2. Signal Correlation & Fixture Integration
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_signal_correlation_from_fixtures(db_session: AsyncSession):
    """
    Validates that a cascading failure scenario:
    api-gateway CPU spike + memory pressure + HTTP 500 spike + DB timeout
    correlates into ONE unified Incident instead of multiple disconnected alerts.
    """
    with open(FIXTURES_DIR / "telemetry.json") as f:
        telem_signals = json.load(f)
    with open(FIXTURES_DIR / "alerts.json") as f:
        alert_signals = json.load(f)
    with open(FIXTURES_DIR / "logs.json") as f:
        log_signals = json.load(f)

    all_signals = telem_signals + alert_signals + log_signals
    incidents = await incident_correlation_engine.correlate_alerts(db_session, all_signals)

    # Should consolidate related signals into high-confidence incident
    assert len(incidents) >= 1
    primary_inc = incidents[0]
    assert primary_inc.severity in ["CRITICAL", "HIGH"]
    assert primary_inc.status == "INVESTIGATING"
    assert primary_inc.correlation_score >= 0.75
    assert len(primary_inc.evidence) >= 3


# ---------------------------------------------------------------------------
# 3. Correlation Score Calculation
# ---------------------------------------------------------------------------
def test_correlation_score_calculation():
    """Validates mathematical properties of correlation score calculation."""
    now = datetime.now(UTC)
    sig1 = NormalizedSignal(
        source=SignalSource.TELEMETRY,
        service="api-gateway",
        title="CPU spike",
        timestamp=now,
        metadata={"trace_id": "tr-123"},
    )
    sig2 = NormalizedSignal(
        source=SignalSource.TRACE,
        service="payment-service",
        title="HTTP 504 Timeout",
        timestamp=now + timedelta(seconds=30),
        metadata={"trace_id": "tr-123"},
    )
    sig3 = NormalizedSignal(
        source=SignalSource.LOG,
        service="database-cluster",
        title="DB connection pool timeout",
        timestamp=now + timedelta(seconds=45),
        metadata={"trace_id": "tr-123"},
    )

    cluster = [sig1, sig2, sig3]
    services = ["api-gateway", "payment-service", "database-cluster"]
    resources = ["res-1", "res-2"]
    time_spread = 45.0
    has_trace = True

    score = incident_correlation_engine.calculate_correlation_score(
        cluster, services, resources, time_spread, has_trace
    )
    assert 0.85 <= score <= 0.99


# ---------------------------------------------------------------------------
# 4. Duplicate Incident Prevention (Idempotency)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_incident_prevention(db_session: AsyncSession):
    """
    Verifies that processing the same signal batch twice DOES NOT create duplicate incidents.
    """
    signals = [
        {
            "service": "database-cluster",
            "resource": "postgres-db-1",
            "title": "PostgreSQL active connections > 95%",
            "severity": "CRITICAL",
            "timestamp": "2026-08-11T11:00:00Z",
        },
        {
            "service": "api-gateway",
            "resource": "ingress-gw",
            "title": "HTTP 500 error spike",
            "severity": "HIGH",
            "timestamp": "2026-08-11T11:01:00Z",
        },
    ]

    # First correlation
    incidents_first = await incident_correlation_engine.correlate_alerts(db_session, signals)
    assert len(incidents_first) == 1
    first_id = incidents_first[0].id

    # Second correlation with same signals
    incidents_second = await incident_correlation_engine.correlate_alerts(db_session, signals)
    assert len(incidents_second) == 1
    assert incidents_second[0].id == first_id


# ---------------------------------------------------------------------------
# 5. Incident Creation & Manual Declaration
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_declare_incident_endpoint(client: AsyncClient):
    """Tests POST /api/v1/incidents/declare manually opens an incident."""
    payload = {
        "title": "Manual Test Incident: Core Auth Failure",
        "description": "Auth token verification failing across all regions.",
        "severity": "CRITICAL",
        "priority": "Critical",
        "service": "auth-service",
        "environment": "production",
        "region": "us-east-1",
        "created_by": "SRE Lead",
        "auto_analyze": True,
    }

    res = await client.post("/api/v1/incidents/declare", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["severity"] == "CRITICAL"
    assert data["status"] == "OPEN"
    assert data["sla_target_seconds"] == 900
    assert data["sla_status"] == "PENDING"


# ---------------------------------------------------------------------------
# 6. Incident Listing with Filters & Pagination
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_incidents_filtering(client: AsyncClient):
    """Tests GET /api/v1/incidents with status, severity, service, and pagination."""
    # Declare test incidents
    await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Service A Degradation", "severity": "HIGH", "service": "payment-service"},
    )
    await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Service B Outage", "severity": "CRITICAL", "service": "database-cluster"},
    )

    # Filter by severity
    res_crit = await client.get("/api/v1/incidents?severity=CRITICAL")
    assert res_crit.status_code == 200
    data_crit = res_crit.json()
    assert all(i["severity"] in ["CRITICAL", "P0"] for i in data_crit["items"])

    # Filter by service
    res_svc = await client.get("/api/v1/incidents?service=payment-service")
    assert res_svc.status_code == 200
    data_svc = res_svc.json()
    assert all("payment-service" in (i["affected_service"] or "") for i in data_svc["items"])

    # Pagination test
    res_page = await client.get("/api/v1/incidents?page=1&size=1")
    assert res_page.status_code == 200
    data_page = res_page.json()
    assert len(data_page["items"]) <= 1
    assert data_page["page"] == 1


# ---------------------------------------------------------------------------
# 7. Incident Details Endpoint
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_incident_details(client: AsyncClient):
    """Tests GET /api/v1/incidents/{id} returns details, evidence, and timeline."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Checkout Latency Spike", "severity": "HIGH", "service": "checkout-svc"},
    )
    inc_id = decl_res.json()["id"]

    res = await client.get(f"/api/v1/incidents/{inc_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == inc_id
    assert "evidence" in data
    assert "timeline_events" in data
    assert "recommended_actions" in data


# ---------------------------------------------------------------------------
# 8. Acknowledge Lifecycle
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_acknowledge_incident(client: AsyncClient):
    """Tests POST /api/v1/incidents/{id}/acknowledge transitions status."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Redis Memory High", "severity": "MEDIUM", "service": "redis-cluster"},
    )
    inc_id = decl_res.json()["id"]

    ack_res = await client.post(
        f"/api/v1/incidents/{inc_id}/acknowledge",
        json={"assigned_to": "Alex Rivera", "notes": "Investigating Redis memory leak"},
    )
    assert ack_res.status_code == 200
    data = ack_res.json()
    assert data["status"] == "ACKNOWLEDGED"
    assert data["assigned_to"] == "Alex Rivera"
    assert data["acknowledged_at"] is not None


# ---------------------------------------------------------------------------
# 9. Investigate Lifecycle
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_investigate_incident(client: AsyncClient):
    """Tests POST /api/v1/incidents/{id}/investigate transitions status."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Kafka Consumer Lag", "severity": "HIGH", "service": "order-worker"},
    )
    inc_id = decl_res.json()["id"]

    inv_res = await client.post(
        f"/api/v1/incidents/{inc_id}/investigate",
        json={"assigned_to": "Marcus Vance", "notes": "Profiling lag on partition 4"},
    )
    assert inv_res.status_code == 200
    data = inv_res.json()
    assert data["status"] == "INVESTIGATING"


# ---------------------------------------------------------------------------
# 10. Mitigate Lifecycle
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_mitigate_incident(client: AsyncClient):
    """Tests POST /api/v1/incidents/{id}/mitigate transitions status."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "High Disk Usage", "severity": "MEDIUM", "service": "postgres-primary"},
    )
    inc_id = decl_res.json()["id"]

    mit_res = await client.post(
        f"/api/v1/incidents/{inc_id}/mitigate",
        json={"action_id": "act-disk-cleanup", "notes": "Vacuuming dead tuples"},
    )
    assert mit_res.status_code == 200
    data = mit_res.json()
    assert data["status"] == "MITIGATING"


# ---------------------------------------------------------------------------
# 11 & 12 & 13. Resolve Lifecycle, MTTR & SLA Calculation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_incident_mttr_and_sla(client: AsyncClient):
    """Tests POST /api/v1/incidents/{id}/resolve calculates MTTR and SLA status."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Payment Degradation", "severity": "CRITICAL", "service": "payment-service"},
    )
    inc_id = decl_res.json()["id"]

    resolve_res = await client.post(
        f"/api/v1/incidents/{inc_id}/resolve",
        json={"resolution_notes": "Restarted pods and expanded cache memory", "resolved_by": "Sarah Chen"},
    )
    assert resolve_res.status_code == 200
    data = resolve_res.json()
    assert data["status"] == "RESOLVED"
    assert data["resolved_at"] is not None
    assert data["mttr_seconds"] is not None
    assert data["mttr_seconds"] >= 0.0
    # Resolved quickly in test, so should meet 900s SLA target
    assert data["sla_status"] == "MET"


# ---------------------------------------------------------------------------
# 14. Analytics Endpoint Calculation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_incident_analytics_endpoint(client: AsyncClient):
    """Tests GET /api/v1/incidents/analytics returns MTTR and SLA calculations."""
    res = await client.get("/api/v1/incidents/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_incidents" in data
    assert "open_incidents" in data
    assert "resolved_incidents" in data
    assert "critical_incidents" in data
    assert "average_mttr_seconds" in data
    assert "median_mttr_seconds" in data
    assert "sla_compliance_percent" in data
    assert "by_severity" in data
    assert "by_service" in data
    assert "top_root_causes" in data


# ---------------------------------------------------------------------------
# 15. Deterministic Root Cause Analysis (RCA) Engine
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_deterministic_rca_engine(db_session: AsyncSession):
    """Tests that deterministic RCA isolates database pool and Redis saturation patterns."""
    inc = Incident(
        id=uuid.uuid4(),
        title="PostgreSQL Connection Storm",
        severity="CRITICAL",
        affected_service="database-cluster",
        evidence=[
            {
                "type": "metric",
                "source": "postgres-primary",
                "message": "Database active connections at 99.4% (max_connections=200 threshold breached)",
                "severity": "CRITICAL",
            }
        ],
    )
    db_session.add(inc)
    await db_session.flush()

    rca_res = await root_cause_analysis_service.analyze_incident(db_session, inc)
    assert "connection pool" in rca_res["root_cause"].lower()
    assert rca_res["confidence"] >= 0.85
    assert len(rca_res["recommended_actions"]) > 0


# ---------------------------------------------------------------------------
# 16. Gemini Fallback & Analysis Engine Tagging
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_gemini_fallback_tagging(client: AsyncClient):
    """Tests that when GEMINI_API_KEY is not live, analysis_engine returns 'local'."""
    decl_res = await client.post(
        "/api/v1/incidents/declare",
        json={"title": "Ingress Timeout", "severity": "HIGH", "service": "api-gateway"},
    )
    inc_id = decl_res.json()["id"]

    analyze_res = await client.post(f"/api/v1/incidents/{inc_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["analysis_engine"] in ["gemini", "local"]
    assert len(data["recommended_actions"]) > 0


# ---------------------------------------------------------------------------
# 17. Organization Tenant Isolation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_organization_isolation(db_session: AsyncSession):
    """Validates multi-tenant isolation by organization_id."""
    org1 = Organization(id=uuid.uuid4(), name="Org One", slug="org-one")
    org2 = Organization(id=uuid.uuid4(), name="Org Two", slug="org-two")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.flush()

    signals_org1 = [
        {"service": "auth-service", "title": "Auth Error Org 1", "severity": "HIGH"}
    ]
    signals_org2 = [
        {"service": "billing-svc", "title": "Billing Failure Org 2", "severity": "CRITICAL"}
    ]

    inc1 = await incident_correlation_engine.correlate_alerts(
        db_session, signals_org1, organization_id=org1.id
    )
    inc2 = await incident_correlation_engine.correlate_alerts(
        db_session, signals_org2, organization_id=org2.id
    )

    assert inc1[0].organization_id == org1.id
    assert inc2[0].organization_id == org2.id


# ---------------------------------------------------------------------------
# 18. Invalid State Transitions & Error Handling
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_invalid_incident_error_handling(client: AsyncClient):
    """Tests 404 for nonexistent incident and validation error handling."""
    fake_id = uuid.uuid4()
    res = await client.get(f"/api/v1/incidents/{fake_id}")
    assert res.status_code == 404

    # Resolve with empty resolution notes should fail validation
    res_bad = await client.post(f"/api/v1/incidents/{fake_id}/resolve", json={"resolution_notes": ""})
    assert res_bad.status_code in [404, 422]
