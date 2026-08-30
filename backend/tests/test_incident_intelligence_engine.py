"""
Comprehensive Production Test Suite for AI Incident Intelligence & Automated Root-Cause Analysis.
Covers:
- Incident Lifecycle Transitions (OPEN -> INVESTIGATING -> MITIGATING -> RESOLVED -> CLOSED -> REOPEN)
- Multi-Signal Deterministic Correlation & Scoring
- Multi-Modal RCA Causal Inference (DB, Redis, CPU, Deployment Regression)
- Structured Evidence Graph & Categorization
- Topological Blast Radius & Dependency Impact
- Chronological Timeline Event Logging
- Actionable Remediation Generation & Execution Safety
- Resolution Verification Engine (Before vs After Telemetry Comparison)
- Grounded Gemini AI Diagnostics & Local Fallback
- SLA & MTTR Tracking
- Multi-Tenant Isolation & RBAC
- Edge Cases & Empty Telemetry Handling
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentTimelineEvent
from app.models.organization import Organization
from app.models.trace import ServiceDependency
from app.schemas.incident import (
    IncidentAcknowledgeRequest,
    IncidentCreate,
    IncidentInvestigateRequest,
    IncidentMitigateRequest,
    IncidentResolve,
)
from app.schemas.signal import NormalizedSignal, SignalSeverity
from app.services.incident_correlation_engine import incident_correlation_engine
from app.services.incident_resolution_verification_service import (
    incident_resolution_verification_service,
)
from app.services.incident_service import incident_service
from app.services.root_cause_analysis_service import root_cause_analysis_service


@pytest.mark.asyncio
async def test_incident_declaration_and_lifecycle(db_session: AsyncSession):
    """Test full incident lifecycle state transitions."""
    # 1. Create / Declare Incident
    payload = IncidentCreate(
        title="Elevated HTTP 504 Gateway Timeouts on API Gateway",
        description="Ingress proxy reporting >8% 504 error responses.",
        severity="CRITICAL",
        priority="Critical",
        affected_service="api-gateway",
        affected_services=["api-gateway", "auth-service", "payment-service"],
        environment="production",
        created_by="SRE-OnCall",
    )
    incident = await incident_service.create(db_session, payload)
    assert incident.id is not None
    assert incident.status in ["INVESTIGATING", "OPEN", "DETECTED"]
    assert incident.sla_target_seconds == 900  # CRITICAL SLA is 15m

    # 2. Acknowledge
    ack_req = IncidentAcknowledgeRequest(assigned_to="DevOps Lead", notes="Acknowledged alert and inspecting ingress logs.")
    acked = await incident_service.acknowledge(db_session, incident.id, ack_req, user_name="DevOps Lead")
    assert acked is not None
    assert acked.status == "ACKNOWLEDGED"
    assert acked.assigned_to == "DevOps Lead"

    # 3. Investigate
    inv_req = IncidentInvestigateRequest(assigned_to="DevOps Lead", notes="Investigating database pool exhaustion.")
    investigating = await incident_service.investigate(db_session, incident.id, inv_req, user_name="DevOps Lead")
    assert investigating is not None
    assert investigating.status == "INVESTIGATING"

    # 4. Mitigate
    mit_req = IncidentMitigateRequest(action_id="act-db-pool-expand", notes="Scaling connection pool.")
    mitigating = await incident_service.mitigate(db_session, incident.id, mit_req, user_name="DevOps Lead")
    assert mitigating is not None
    assert mitigating.status == "MITIGATING"

    # 5. Resolve
    res_req = IncidentResolve(resolution_notes="Connection pool scaled from 200 to 500; latency normalized.", resolved_by="DevOps Lead")
    resolved = await incident_service.resolve(db_session, incident.id, res_req)
    assert resolved is not None
    assert resolved.status == "RESOLVED"
    assert resolved.resolved_at is not None
    assert resolved.mttr_seconds is not None

    # 6. Close
    closed = await incident_service.close(db_session, incident.id, user_name="DevOps Lead")
    assert closed is not None
    assert closed.status == "CLOSED"

    # 7. Reopen
    reopened = await incident_service.reopen(db_session, incident.id, reason="Recurring 504 burst detected.", reopened_by="SRE Bot")
    assert reopened is not None
    assert reopened.status == "INVESTIGATING"
    assert reopened.resolved_at is None


@pytest.mark.asyncio
async def test_multi_signal_correlation_scoring(db_session: AsyncSession):
    """Test deterministic correlation scoring across temporal, service, and signal dimensions."""
    now = datetime.now(UTC)

    sig1 = NormalizedSignal(
        signal_id="sig-1",
        service="payment-service",
        title="High error rate",
        severity=SignalSeverity.CRITICAL,
        source="telemetry",
        timestamp=now,
        metric="error_rate",
        value=6.4,
    )
    sig2 = NormalizedSignal(
        signal_id="sig-2",
        service="payment-service",
        title="P99 latency spike",
        severity=SignalSeverity.HIGH,
        source="trace",
        timestamp=now + timedelta(seconds=45),
        metric="latency_p99",
        value=2400.0,
    )
    sig3 = NormalizedSignal(
        signal_id="sig-3",
        service="payment-service",
        title="PostgreSQL connection timeout",
        severity=SignalSeverity.CRITICAL,
        source="log",
        timestamp=now + timedelta(seconds=90),
    )

    cluster = [sig1, sig2, sig3]
    services = ["payment-service"]
    resources = ["postgres-primary"]

    score = incident_correlation_engine.calculate_correlation_score(
        cluster=cluster,
        services=services,
        resources=resources,
        time_spread_seconds=90.0,
        has_trace_match=True,
    )

    assert 0.80 <= score <= 1.0
    fp = incident_correlation_engine.generate_signal_fingerprint(sig1)
    assert len(fp) == 16


@pytest.mark.asyncio
async def test_root_cause_analysis_causal_inference(db_session: AsyncSession):
    """Test multi-modal causal inference identifying specific failure patterns."""
    # Pattern 1: Database connection pool saturation
    db_incident = Incident(
        title="Database max_connections reached",
        affected_service="database-cluster",
        affected_services=["database-cluster", "payment-service"],
        evidence=[
            {
                "type": "log",
                "source": "postgresql",
                "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections (max_connections=200)",
                "severity": "CRITICAL",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ],
    )
    db_session.add(db_incident)
    await db_session.flush()

    res = await root_cause_analysis_service.analyze_incident(db_session, db_incident)
    assert "connection pool" in res["root_cause"].lower() or "postgresql" in res["root_cause"].lower()
    assert res["confidence"] >= 0.85
    assert len(res["contributing_factors"]) >= 2
    assert len(res["recommended_actions"]) >= 1

    # Pattern 2: Deployment-induced regression
    deploy_incident = Incident(
        title="Post-Release Latency Regression",
        affected_service="auth-service",
        affected_services=["auth-service", "api-gateway"],
        evidence=[
            {
                "type": "deployment",
                "source": "auth-service",
                "message": "Deployment rollout v2.4.1 completed 3 minutes before error burst.",
                "severity": "HIGH",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ],
    )
    db_session.add(deploy_incident)
    await db_session.flush()

    res_deploy = await root_cause_analysis_service.analyze_incident(db_session, deploy_incident)
    assert "deployment" in res_deploy["root_cause"].lower() or "regression" in res_deploy["root_cause"].lower()


@pytest.mark.asyncio
async def test_evidence_graph_generation(db_session: AsyncSession):
    """Test structured evidence graph categorization."""
    incident = Incident(
        title="Checkout Flow Outage",
        affected_service="checkout-service",
        evidence=[
            {"type": "metric", "source": "checkout-service", "message": "CPU at 98%", "metric_value": 98.0},
            {"type": "log", "source": "checkout-service", "message": "NullPointerException in payment handler"},
            {"type": "trace", "source": "api-gateway", "message": "Span timeout 5000ms"},
            {"type": "alert", "source": "AlertManager", "message": "CheckoutErrorRateAlert firing"},
            {"type": "k8s", "source": "checkout-pod-1", "message": "OOMKilled restarted 3 times"},
        ],
    )
    db_session.add(incident)
    await db_session.commit()

    ev_graph = await incident_service.get_evidence_graph(db_session, incident.id)
    assert ev_graph is not None
    assert ev_graph["evidence_count"] == 5
    assert len(ev_graph["categories"]["metrics"]) == 1
    assert len(ev_graph["categories"]["logs"]) == 1
    assert len(ev_graph["categories"]["traces"]) == 1
    assert len(ev_graph["categories"]["alerts"]) == 1
    assert len(ev_graph["categories"]["kubernetes"]) == 1


@pytest.mark.asyncio
async def test_blast_radius_dag_computation(db_session: AsyncSession):
    """Test topological blast radius computation."""
    # Insert service dependency
    dep = ServiceDependency(
        source_service="api-gateway",
        target_service="payment-service",
        dependency_type="synchronous",
        protocol="grpc",
        latency_ms=45.0,
    )
    db_session.add(dep)

    incident = Incident(
        title="Payment Service Latency",
        severity="CRITICAL",
        affected_service="payment-service",
        affected_services=["payment-service", "api-gateway", "checkout-svc"],
    )
    db_session.add(incident)
    await db_session.commit()

    blast = await root_cause_analysis_service.calculate_blast_radius(db_session, incident)
    assert blast["root_component"] == "payment-service"
    assert len(blast["affected_services"]) == 3
    assert blast["estimated_user_impact"] == "CRITICAL"
    assert "nodes" in blast["topology_graph"]
    assert "edges" in blast["topology_graph"]


@pytest.mark.asyncio
async def test_resolution_verification_telemetry_comparison(db_session: AsyncSession):
    """Test telemetry verification confirming successful incident resolution."""
    incident = Incident(
        title="Memory Leak and Error Spike",
        affected_service="auth-service",
        evidence=[
            {"type": "metric", "source": "error_rate", "metric_value": 8.5},
            {"type": "metric", "source": "latency_p99", "metric_value": 3200.0},
        ],
    )
    db_session.add(incident)
    await db_session.commit()

    # Pass recovered post-remediation metrics
    res = await incident_resolution_verification_service.verify_incident_resolution(
        db_session,
        incident,
        post_telemetry_override={
            "error_rate": 0.02,
            "latency_p99_ms": 95.0,
            "cpu_utilization": 38.0,
            "memory_utilization": 45.0,
        },
    )

    assert res.resolution_verified is True
    assert res.remaining_risk == "NONE"
    assert res.service_health_score >= 95.0
    assert len(res.verification_evidence) >= 4

    # Verify incident updated in DB
    assert incident.resolution_verified is True
    assert incident.remaining_risk == "NONE"


@pytest.mark.asyncio
async def test_resolution_verification_unresolved_failure(db_session: AsyncSession):
    """Test telemetry verification flagging remaining risk when metrics remain elevated."""
    incident = Incident(
        title="Unmitigated Database Contention",
        affected_service="database-cluster",
    )
    db_session.add(incident)
    await db_session.commit()

    # Pass elevated metrics (still failing)
    res = await incident_resolution_verification_service.verify_incident_resolution(
        db_session,
        incident,
        post_telemetry_override={
            "error_rate": 6.8,
            "latency_p99_ms": 2900.0,
            "cpu_utilization": 96.0,
            "memory_utilization": 92.0,
        },
    )

    assert res.resolution_verified is False
    assert res.remaining_risk == "HIGH"
    assert res.service_health_score < 60.0
    assert incident.resolution_verified is False


@pytest.mark.asyncio
async def test_incident_sla_and_mttr_calculation(db_session: AsyncSession):
    """Test MTTR calculation and SLA target compliance."""
    start_time = datetime.now(UTC) - timedelta(minutes=20)
    incident = Incident(
        title="Checkout Latency Spike",
        severity="CRITICAL",  # Target: 15 mins (900s)
        started_at=start_time,
        created_at=start_time,
        sla_target_seconds=900,
    )
    db_session.add(incident)
    await db_session.commit()

    # Resolve after 20 mins (breaching 15m SLA)
    res_req = IncidentResolve(resolution_notes="Scaled pods", resolved_by="Engineer")
    resolved = await incident_service.resolve(db_session, incident.id, res_req)

    assert resolved is not None
    assert resolved.mttr_seconds >= 1200.0
    assert resolved.sla_status == "BREACHED"


@pytest.mark.asyncio
async def test_chronological_timeline_logging(db_session: AsyncSession):
    """Test chronological timeline event recording."""
    incident = Incident(
        title="Timeline Test Incident",
        affected_service="payment-service",
    )
    db_session.add(incident)
    await db_session.commit()

    now = datetime.now(UTC)
    evt1 = IncidentTimelineEvent(
        id=uuid.uuid4(),
        incident_id=incident.id,
        timestamp=now - timedelta(minutes=5),
        event_type="metric_anomaly",
        title="Error rate spike",
        source="Prometheus",
    )
    evt2 = IncidentTimelineEvent(
        id=uuid.uuid4(),
        incident_id=incident.id,
        timestamp=now,
        event_type="status_changed",
        title="Status changed to INVESTIGATING",
        source="System",
    )
    db_session.add_all([evt1, evt2])
    await db_session.commit()

    timeline = await incident_service.get_timeline(db_session, incident.id)
    assert len(timeline) >= 2
    assert timeline[0].timestamp <= timeline[1].timestamp


@pytest.mark.asyncio
async def test_organization_tenant_isolation(db_session: AsyncSession):
    """Test strict multi-tenant isolation across incidents."""
    org1 = Organization(name="Tenant Alpha", slug=f"tenant-alpha-{uuid.uuid4().hex[:6]}")
    org2 = Organization(name="Tenant Beta", slug=f"tenant-beta-{uuid.uuid4().hex[:6]}")
    db_session.add_all([org1, org2])
    await db_session.flush()

    inc1 = Incident(title="Tenant Alpha Incident", organization_id=org1.id)
    inc2 = Incident(title="Tenant Beta Incident", organization_id=org2.id)
    db_session.add_all([inc1, inc2])
    await db_session.commit()

    items1, total1, _ = await incident_service.list_incidents(db_session, organization_id=org1.id, size=100)
    items2, total2, _ = await incident_service.list_incidents(db_session, organization_id=org2.id, size=100)

    org1_ids = [str(i.id) for i in items1]
    org2_ids = [str(i.id) for i in items2]

    assert str(inc1.id) in org1_ids
    assert str(inc2.id) not in org1_ids
    assert str(inc2.id) in org2_ids
    assert str(inc1.id) not in org2_ids


@pytest.mark.asyncio
async def test_edge_cases_empty_and_missing_telemetry(db_session: AsyncSession):
    """Test RCA and verification engines with missing telemetry/empty evidence."""
    incident = Incident(
        title="Empty Telemetry Incident",
        affected_service="unknown-service",
        evidence=[],
    )
    db_session.add(incident)
    await db_session.commit()

    rca_res = await root_cause_analysis_service.analyze_incident(db_session, incident)
    assert rca_res is not None
    assert rca_res["confidence"] > 0.0
    assert len(rca_res["evidence"]) >= 1  # Gracefully populated fallback evidence

    ver_res = await incident_resolution_verification_service.verify_incident_resolution(
        db_session, incident
    )
    assert ver_res is not None
    assert ver_res.service == "unknown-service"


@pytest.mark.asyncio
async def test_incident_pagination_and_filtering(db_session: AsyncSession):
    """Test incident filtering by status, severity, service, environment."""
    for i in range(5):
        inc = Incident(
            title=f"Bulk Incident {i}",
            service="api-gateway" if i % 2 == 0 else "payment-service",
            severity="CRITICAL" if i % 2 == 0 else "HIGH",
            status="OPEN" if i < 3 else "RESOLVED",
            environment="production",
        )
        db_session.add(inc)
    await db_session.commit()

    items, total, pages = await incident_service.list_incidents(
        db_session, status="OPEN", service="api-gateway", page=1, size=10
    )
    assert total >= 1
    assert all(str(i.status).upper() == "OPEN" for i in items)
    assert all("api-gateway" in (i.affected_service or "") for i in items)



@pytest.mark.asyncio
async def test_gemini_fallback_diagnostics(db_session: AsyncSession):
    """Test Grounded Gemini fallback when AI is unavailable or offline."""
    from app.services.incident_ai_service import analyze_incident_with_gemini

    res = await analyze_incident_with_gemini(
        title="Redis Memory Eviction",
        description="Redis cluster maxmemory threshold breached.",
        severity="HIGH",
        priority="High",
        affected_service="redis-cache",
        evidence=[{"type": "metric", "source": "redis", "message": "maxmemory 2GB reached"}],
        contributing_factors=["Cache exhaustion"],
    )
    assert res is not None
    assert res.get("analysis_engine") in ["gemini", "local"]
    assert "summary" in res or "ai_summary" in res
    assert "root_cause" in res or "ai_root_cause" in res


@pytest.mark.asyncio
async def test_incident_remediation_execution_safety(db_session: AsyncSession):
    """Test remediation execution requiring explicit engineer authorization."""
    from app.schemas.incident import IncidentRemediateRequest

    incident = Incident(
        title="Database Connection Surge",
        affected_service="database-cluster",
        recommended_actions=[
            {
                "id": "act-db-pool-expand",
                "title": "Scale DB Pool",
                "workflow_id": "wf-db-scale",
                "risk_level": "LOW",
            }
        ],
    )
    db_session.add(incident)
    await db_session.commit()

    req = IncidentRemediateRequest(
        action_id="act-db-pool-expand",
        authorized_by="Lead SRE Alex",
    )
    rem_res = await incident_service.execute_remediation(db_session, incident.id, req)
    assert rem_res.status == "EXECUTED"
    assert "act-db-pool-expand" == rem_res.action_id
    assert rem_res.workflow_execution_id is not None
