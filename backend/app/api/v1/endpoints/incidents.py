"""
Enterprise Incident Management Center & RCA Platform API endpoints & WebSockets.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.incident import Incident, IncidentTimelineEvent
from app.models.organization import Organization
from app.schemas.incident import (
    BlastRadiusResponse,
    IncidentAcknowledgeRequest,
    IncidentAIAnalysisResponse,
    IncidentAnalyticsResponse,
    IncidentAssignRequest,
    IncidentCorrelationRequest,
    IncidentCorrelationResponse,
    IncidentCreate,
    IncidentDeclareRequest,
    IncidentEvidenceGraphResponse,
    IncidentInvestigateRequest,
    IncidentListResponse,
    IncidentMitigateRequest,
    IncidentRemediateRequest,
    IncidentRemediateResponse,
    IncidentReopenRequest,
    IncidentResolutionVerificationRequest,
    IncidentResolutionVerificationResponse,
    IncidentResolve,
    IncidentResponse,
    IncidentStatsResponse,
    IncidentTimelineEventCreate,
    IncidentTimelineEventResponse,
    IncidentUpdate,
    RootCauseAnalysisResponse,
)
from app.services.incident_service import IncidentService, incident_service
from app.services.websocket_manager import incident_ws_manager

log = structlog.get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency Injection for Incident Service
# ---------------------------------------------------------------------------
def get_incident_service() -> IncidentService:
    return incident_service


# ---------------------------------------------------------------------------
# Seed initial sample data if DB is empty
# ---------------------------------------------------------------------------
async def _seed_initial_incidents_if_empty(db: AsyncSession, service: IncidentService) -> None:
    incidents, total, _ = await service.list_incidents(db, size=1)
    if total == 0:
        log.info("seeding_initial_incidents")
        now = datetime.now(UTC)

        org_stmt = select(Organization).limit(1)
        org_res = await db.execute(org_stmt)
        default_org = org_res.scalar_one_or_none()
        org_id = default_org.id if default_org else None

        sample_incidents = [
            Incident(
                organization_id=org_id,
                title="P99 Latency degradation on Payment API",
                description="Payment API response time exceeded 2.5s threshold due to Redis cache eviction spike.",
                severity="CRITICAL",
                priority="Critical",
                status="INVESTIGATING",
                source="correlation_engine",
                affected_service="payment-service",
                affected_services=["payment-service", "checkout-svc", "auth-service"],
                affected_resources=["redis-cluster-cache", "payment-api-pod-1"],
                resource_id="redis-cluster-cache",
                environment="production",
                affected_region="us-east-1",
                assigned_engineer="Sarah Chen (SRE Lead)",
                assigned_to="Sarah Chen (SRE Lead)",
                created_by="AlertManager Bot",
                started_at=now,
                detected_at=now,
                created_at=now,
                confidence_score=0.96,
                impact_score=92.0,
                correlation_score=0.96,
                sla_target_seconds=900,
                sla_status="PENDING",
                analysis_engine="local",
                root_cause="Redis memory limit reached maxmemory threshold (2GB), evicting session tokens.",
                contributing_factors=[
                    "Redis memory limit reached maxmemory threshold (2GB)",
                    "Checkout conversion rate drop",
                    "Session token lookup cache misses",
                ],
                evidence=[
                    {
                        "type": "metric",
                        "source": "redis-cluster-cache",
                        "message": "Redis memory usage at 99.4% (maxmemory=2GB breached)",
                        "severity": "CRITICAL",
                        "metric_value": 99.4,
                        "threshold": 85.0,
                    },
                    {
                        "type": "trace",
                        "source": "payment-service",
                        "message": "P99 latency increased 4.2x from 120ms to 2540ms",
                        "severity": "HIGH",
                        "metric_value": 2540.0,
                        "threshold": 300.0,
                    },
                ],
                recommended_actions=[
                    {
                        "id": "act-redis-scale",
                        "title": "Scale Redis Cluster Memory to 8GB",
                        "description": "Resize Redis cluster cache nodes and enable volatile-lru eviction.",
                        "action_type": "scale",
                        "workflow_id": "wf-redis-scale",
                        "automated": True,
                        "risk_level": "LOW",
                        "risk": "LOW",
                        "requires_approval": True,
                        "dry_run": True,
                    },
                    {
                        "id": "act-flush-telemetry-keys",
                        "title": "Evict Orphaned Telemetry Keys",
                        "description": "Run non-blocking SCAN and UNLINK on expired telemetry namespaces.",
                        "action_type": "config",
                        "workflow_id": "wf-redis-key-cleanup",
                        "automated": True,
                        "risk_level": "LOW",
                        "risk": "LOW",
                        "requires_approval": True,
                        "dry_run": True,
                    },
                ],
                blast_radius={
                    "root_component": "redis-cluster-cache",
                    "directly_affected_resources": ["redis-cluster-cache"],
                    "indirectly_affected_resources": ["payment-service", "checkout-svc", "auth-service"],
                    "affected_services": ["payment-service", "checkout-svc", "auth-service"],
                    "dependency_depth": 3,
                    "estimated_user_impact": "CRITICAL",
                    "financial_risk_estimate": "$12,500 / hr",
                },
                ai_summary="Payment Gateway latency breached SLO. Redis cache eviction rates increased by 320%.",
                ai_root_cause="Redis memory limit reached maxmemory threshold (2GB), evicting session tokens.",
                ai_business_impact="Checkout conversion rate dropped by 8.4% during peak window.",
                ai_immediate_mitigation="1. Scale Redis instance to 8GB.\n2. Evict orphan telemetry keys.\n3. Increase timeout limit.",
                ai_suggested_resolution="1. Scale Redis instance to 8GB.\n2. Evict orphan telemetry keys.",
                ai_long_term_prevention=[
                    "Enable Memory Autoscaling",
                    "Implement Key TTL audit policy",
                ],
                ai_preventive_actions=[
                    "Enable Memory Autoscaling",
                    "Implement Key TTL audit policy",
                ],
                ai_similar_incidents=[
                    {"id": "INC-402", "title": "Cache memory exhaustion", "similarity": "91%"}
                ],
                ai_estimated_resolution_time="15-25 mins",
                ai_confidence_score=0.96,
            ),
            Incident(
                organization_id=org_id,
                title="Database Connection Pool Exhaustion on PostgreSQL Primary",
                description="PostgreSQL primary rejected connections: max_connections (200) reached due to connection leaks.",
                severity="CRITICAL",
                priority="Critical",
                status="IDENTIFIED",
                source="correlation_engine",
                affected_service="database-cluster",
                affected_services=["database-cluster", "payment-service", "order-worker", "api-gateway"],
                affected_resources=["postgres-primary-db", "pgbouncer-pool-01"],
                resource_id="postgres-primary-db",
                environment="production",
                affected_region="us-east-1",
                assigned_engineer="Marcus Vance (DBA)",
                assigned_to="Marcus Vance (DBA)",
                created_by="CloudPulse Correlation Engine",
                started_at=now,
                detected_at=now,
                created_at=now,
                confidence_score=0.94,
                impact_score=95.0,
                correlation_score=0.95,
                sla_target_seconds=900,
                sla_status="PENDING",
                analysis_engine="local",
                root_cause="PostgreSQL connection pool saturation due to unclosed idle sessions during background retry loop.",
                contributing_factors=[
                    "Database active connections reached 200/200 limit",
                    "42 idle in transaction connections held by worker pods",
                    "Microservice retry storm multiplying connection attempts",
                ],
                evidence=[
                    {
                        "type": "metric",
                        "source": "postgres-primary",
                        "message": "Database active connections at 98.4% (max_connections=200)",
                        "severity": "CRITICAL",
                        "metric_value": 98.4,
                        "threshold": 80.0,
                    },
                    {
                        "type": "log",
                        "source": "postgres-primary",
                        "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
                        "severity": "CRITICAL",
                    },
                    {
                        "type": "trace",
                        "source": "api-gateway",
                        "message": "Downstream HTTP 500 errors originating from database timeout spans",
                        "severity": "HIGH",
                    },
                ],
                recommended_actions=[
                    {
                        "id": "act-db-pool-expand",
                        "title": "Increase DB Connection Pool Limit & Provision Read Replica",
                        "description": "Scale PostgreSQL max_connections from 200 to 500 and route read traffic to replica.",
                        "action_type": "scale",
                        "workflow_id": "wf-db-autoscale",
                        "automated": True,
                        "risk_level": "LOW",
                        "risk": "LOW",
                        "requires_approval": True,
                        "dry_run": True,
                    },
                    {
                        "id": "act-pgbouncer-flush",
                        "title": "Reset PgBouncer Pool & Flush Orphaned Sessions",
                        "description": "Execute PAUSE and RESUME on PgBouncer to clear stale backend connections.",
                        "action_type": "restart",
                        "workflow_id": "wf-pgbouncer-flush",
                        "automated": True,
                        "risk_level": "LOW",
                        "risk": "LOW",
                        "requires_approval": True,
                        "dry_run": True,
                    },
                ],
                blast_radius={
                    "root_component": "database-cluster",
                    "directly_affected_resources": ["postgres-primary-db"],
                    "indirectly_affected_resources": ["payment-service", "order-worker", "api-gateway"],
                    "affected_services": ["database-cluster", "payment-service", "order-worker", "api-gateway"],
                    "dependency_depth": 4,
                    "estimated_user_impact": "CRITICAL",
                    "financial_risk_estimate": "$18,000 / hr",
                },
                ai_summary="DB Connection Pool exhausted by leaked idle connections from microservice worker pods.",
                ai_root_cause="Unclosed DB session instances in background retry loop during network micro-outage.",
                ai_business_impact="Write requests failing across 3 downstream services.",
                ai_immediate_mitigation="Execute PgBouncer connection reset and restart leaking worker deployments.",
                ai_suggested_resolution="Execute PgBouncer connection reset and restart leaking worker deployments.",
                ai_long_term_prevention=[
                    "Configure PgBouncer transaction pooling mode",
                    "Set max_db_idle_time=30s",
                ],
                ai_preventive_actions=[
                    "Configure PgBouncer transaction pooling mode",
                    "Set max_db_idle_time=30s",
                ],
                ai_similar_incidents=[
                    {"id": "INC-290", "title": "PgBouncer pool exhaustion", "similarity": "95%"}
                ],
                ai_estimated_resolution_time="10-15 mins",
                ai_confidence_score=0.95,
            ),
        ]

        for inc in sample_incidents:
            db.add(inc)
            await db.flush()

            evt1 = IncidentTimelineEvent(
                id=uuid.uuid4(),
                incident_id=inc.id,
                timestamp=now,
                event_type="metric_anomaly",
                title=f"Telemetry Anomaly Detected: {inc.affected_service}",
                description=f"Automated monitoring detected threshold anomaly on {inc.affected_service}.",
                source=inc.affected_service or "system",
                created_by="MonitoringEngine",
            )
            evt2 = IncidentTimelineEvent(
                id=uuid.uuid4(),
                incident_id=inc.id,
                timestamp=now,
                event_type="incident_created",
                title=f"Incident Correlated: {inc.title}",
                description=f"Incident created with {inc.severity} severity (Confidence: {int(inc.confidence_score * 100)}%).",
                source="IncidentCorrelationEngine",
                created_by="IncidentCorrelationEngine",
            )
            evt3 = IncidentTimelineEvent(
                id=uuid.uuid4(),
                incident_id=inc.id,
                timestamp=now,
                event_type="rca_identified",
                title=f"RCA Complete: {inc.root_cause}",
                description=f"Confidence: {int(inc.confidence_score * 100)}%. Multi-signal evidence verified.",
                source="RootCauseAnalysisService",
                created_by="CloudPulse AI",
            )
            db.add(evt1)
            db.add(evt2)
            db.add(evt3)

        await db.commit()


# ---------------------------------------------------------------------------
# WebSocket Endpoint
# ---------------------------------------------------------------------------


@router.websocket("/ws")
async def incident_websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for incident broadcasts."""
    await incident_ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        incident_ws_manager.disconnect(websocket)
    except Exception as exc:
        log.warning("websocket_error", error=str(exc))
        incident_ws_manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------


@router.get("/active", response_model=list[IncidentResponse], summary="Get active incidents")
async def get_active_incidents(
    db: AsyncSession = Depends(get_db),
    service: IncidentService = Depends(get_incident_service),
):
    """Retrieve list of currently active incidents."""
    await _seed_initial_incidents_if_empty(db, service)
    active_incidents = await service.get_active(db)
    return [IncidentResponse.model_validate(inc) for inc in active_incidents]


@router.get("/stats", response_model=IncidentStatsResponse, summary="Get incident stats")
async def get_incident_stats(
    db: AsyncSession = Depends(get_db),
    service: IncidentService = Depends(get_incident_service),
):
    """Retrieve top KPI cards stats: Open Incidents, Critical Incidents, Avg Resolution Time, SLA Compliance."""
    await _seed_initial_incidents_if_empty(db, service)
    return await service.get_stats(db)


@router.get(
    "/analytics", response_model=IncidentAnalyticsResponse, summary="Incident analytics & charts"
)
async def get_incident_analytics(
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Get metrics for incident analytics charts, SLA compliance, and MTTR."""
    await _seed_initial_incidents_if_empty(db, service_layer)
    return await service_layer.get_analytics(db)


@router.get("", response_model=IncidentListResponse, summary="List incidents")
async def list_incidents(
    status: str | None = Query(
        None, description="Filter by status (OPEN, ACKNOWLEDGED, INVESTIGATING, MITIGATING, RESOLVED, CLOSED)"
    ),
    severity: str | None = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    priority: str | None = Query(None, description="Filter by priority (Critical, High, Medium, Low)"),
    service: str | None = Query(None, description="Filter by affected service"),
    environment: str | None = Query(None, description="Filter by environment (production, staging, dev)"),
    region: str | None = Query(None, description="Filter by cloud region"),
    start_date: datetime | None = Query(None, description="Filter incidents created after this datetime"),
    end_date: datetime | None = Query(None, description="Filter incidents created before this datetime"),
    search: str | None = Query(None, description="Search term in title, description, or root cause"),
    sort_by: str = Query("created_at", description="Sort field (created_at, severity, priority, status)"),
    sort_dir: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    page_size: int | None = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Retrieve paginated list of incidents with filters, search, and sorting."""
    await _seed_initial_incidents_if_empty(db, service_layer)
    effective_size = page_size or size

    incidents, total, pages = await service_layer.list_incidents(
        db,
        status=status,
        severity=severity,
        priority=priority,
        service=service,
        environment=environment,
        region=region,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        size=effective_size,
    )

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(inc) for inc in incidents],
        total=total,
        page=page,
        size=effective_size,
        pages=pages,
    )


@router.post(
    "/correlate",
    response_model=IncidentCorrelationResponse,
    summary="Correlate raw signals and alerts into incidents",
)
async def correlate_signals(
    payload: IncidentCorrelationRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """
    Ingests multi-source signals, deduplicates, and correlates them into high-confidence Incident entities.
    Protects against duplicate creation through deterministic fingerprinting.
    """
    signals_input = payload.alerts or payload.signals
    if not signals_input:
        # If no alerts in body, provide sample multi-service cascade
        signals_input = [
            {
                "service": "database-cluster",
                "event_type": "metric_anomaly",
                "title": "PostgreSQL active connections at 98.4%",
                "severity": "CRITICAL",
            },
            {
                "service": "payment-service",
                "event_type": "trace_failure",
                "title": "HTTP 504 Gateway Timeouts on /checkout",
                "severity": "HIGH",
            },
            {
                "service": "auth-service",
                "event_type": "log_error",
                "title": "Database connection pool timeout in session worker",
                "severity": "HIGH",
            },
        ]

    created = await service_layer.correlate_raw_alerts(
        db, signals_input, organization_id=payload.organization_id
    )
    return IncidentCorrelationResponse(
        correlated_incidents_count=len(created),
        raw_alerts_processed=len(signals_input),
        incidents=[IncidentResponse.model_validate(inc) for inc in created],
    )


@router.post(
    "/declare",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually declare an incident",
)
async def declare_incident_endpoint(
    payload: IncidentDeclareRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Manually declare an incident from the UI or API."""
    incident = await service_layer.declare_incident(db, payload)
    return IncidentResponse.model_validate(incident)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create incident",
)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Create a new incident, automatically invoke Gemini AI analysis, and broadcast WebSocket notification."""
    incident = await service_layer.create(db, payload)
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}", response_model=IncidentResponse, summary="Get incident details")
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Retrieve details for a single incident by ID."""
    incident = await service_layer.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(incident)


@router.put("/{incident_id}", response_model=IncidentResponse, summary="Update incident")
async def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Update incident attributes, broadcasting WebSockets when status/severity change."""
    updated = await service_layer.update(db, incident_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(updated)


@router.post(
    "/{incident_id}/acknowledge",
    response_model=IncidentResponse,
    summary="Acknowledge incident",
)
async def acknowledge_incident(
    incident_id: uuid.UUID,
    payload: IncidentAcknowledgeRequest = IncidentAcknowledgeRequest(),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Acknowledge incident, updating status to ACKNOWLEDGED and recording timeline event."""
    user_name = payload.assigned_to or "Engineer"
    ack_obj = await service_layer.acknowledge(db, incident_id, payload, user_name=user_name)
    if not ack_obj:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(ack_obj)


@router.post(
    "/{incident_id}/investigate",
    response_model=IncidentResponse,
    summary="Start incident investigation",
)
async def investigate_incident(
    incident_id: uuid.UUID,
    payload: IncidentInvestigateRequest = IncidentInvestigateRequest(),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Transition incident to INVESTIGATING and trigger active RCA and AI diagnostics."""
    user_name = payload.assigned_to or "Engineer"
    inv_obj = await service_layer.investigate(db, incident_id, payload, user_name=user_name)
    if not inv_obj:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(inv_obj)


@router.post(
    "/{incident_id}/mitigate",
    response_model=IncidentResponse,
    summary="Start incident mitigation",
)
async def mitigate_incident(
    incident_id: uuid.UUID,
    payload: IncidentMitigateRequest = IncidentMitigateRequest(),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Transition incident to MITIGATING status."""
    user_name = payload.authorized_by or "Engineer"
    mit_obj = await service_layer.mitigate(db, incident_id, payload, user_name=user_name)
    if not mit_obj:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(mit_obj)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse, summary="Resolve incident")
async def resolve_incident(
    incident_id: uuid.UUID,
    payload: IncidentResolve,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Mark incident as resolved, calculate MTTR and evaluate SLA compliance status."""
    resolved = await service_layer.resolve(db, incident_id, payload)
    if not resolved:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(resolved)


@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentAIAnalysisResponse,
    summary="Re-run Gemini AI analysis & RCA",
)
async def reanalyze_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Trigger or refresh Google Gemini AI analysis and multi-modal RCA for a specific incident."""
    ai_data = await service_layer.analyze(db, incident_id)
    if not ai_data:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentAIAnalysisResponse(
        summary=ai_data.get("summary") or ai_data.get("ai_summary", ""),
        root_cause=ai_data.get("root_cause") or ai_data.get("ai_root_cause", ""),
        confidence=float(ai_data.get("confidence") or ai_data.get("ai_confidence_score", 0.94)),
        evidence=ai_data.get("evidence", []),
        impact=ai_data.get("impact") or ai_data.get("ai_business_impact", ""),
        recommended_actions=ai_data.get("recommended_actions", []),
        preventive_actions=ai_data.get("preventive_actions") or ai_data.get("ai_long_term_prevention", []),
        analysis_engine=ai_data.get("analysis_engine", "local"),
        ai_summary=ai_data.get("ai_summary", ""),
        ai_root_cause=ai_data.get("ai_root_cause", ""),
        ai_business_impact=ai_data.get("ai_business_impact", ""),
        ai_suggested_resolution=ai_data.get("ai_suggested_resolution", ""),
        ai_immediate_mitigation=ai_data.get("ai_immediate_mitigation", ""),
        ai_long_term_prevention=ai_data.get("ai_long_term_prevention", []),
        ai_preventive_actions=ai_data.get("ai_preventive_actions", []),
        ai_similar_incidents=ai_data.get("ai_similar_incidents", []),
        ai_estimated_resolution_time=ai_data.get("ai_estimated_resolution_time", "30 minutes"),
        ai_confidence_score=float(ai_data.get("ai_confidence_score", 0.94)),
    )


@router.get(
    "/{incident_id}/timeline",
    response_model=list[IncidentTimelineEventResponse],
    summary="Get incident timeline",
)
async def get_incident_timeline(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Retrieve chronological event timeline for an incident."""
    events = await service_layer.get_timeline(db, incident_id)
    return [IncidentTimelineEventResponse.model_validate(e) for e in events]


@router.post(
    "/{incident_id}/timeline",
    response_model=IncidentTimelineEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add timeline event or engineer note",
)
async def add_incident_timeline_event(
    incident_id: uuid.UUID,
    payload: IncidentTimelineEventCreate,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Add a manual note or telemetry event to the incident timeline."""
    evt = await service_layer.add_timeline_event(db, incident_id, payload)
    return IncidentTimelineEventResponse.model_validate(evt)


@router.get(
    "/{incident_id}/impact",
    response_model=BlastRadiusResponse,
    summary="Get incident blast radius & topology impact",
)
async def get_incident_impact(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Calculate blast radius and topology impact graph for an incident."""
    impact = await service_layer.get_impact(db, incident_id)
    if not impact:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return BlastRadiusResponse(**impact)


@router.get(
    "/{incident_id}/root-cause",
    response_model=RootCauseAnalysisResponse,
    summary="Get RCA diagnosis & evidence",
)
async def get_incident_root_cause(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Get detailed root cause analysis, confidence score, evidence matrix, and recommendations."""
    rca = await service_layer.get_root_cause(db, incident_id)
    if not rca:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return RootCauseAnalysisResponse(**rca)


@router.post(
    "/{incident_id}/remediate",
    response_model=IncidentRemediateResponse,
    summary="Execute authorized remediation workflow",
)
async def execute_incident_remediation(
    incident_id: uuid.UUID,
    payload: IncidentRemediateRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """
    Executes an authorized remediation action via the Workflow Automation Engine.
    Safety gated: Requires explicit engineer authorization.
    """
    try:
        return await service_layer.execute_remediation(db, incident_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        log.error("remediation_execution_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Remediation failed: {str(exc)}")


@router.patch("/{incident_id}", response_model=IncidentResponse, summary="Patch incident")
async def patch_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Partially update incident attributes."""
    updated = await service_layer.update(db, incident_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(updated)


@router.post(
    "/{incident_id}/verify-resolution",
    response_model=IncidentResolutionVerificationResponse,
    summary="Verify incident resolution against telemetry",
)
async def verify_incident_resolution(
    incident_id: uuid.UUID,
    payload: IncidentResolutionVerificationRequest = IncidentResolutionVerificationRequest(),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """
    Compares telemetry before and during the incident against post-mitigation metrics
    to verify that error rates, latency, and resource saturation have normalized.
    """
    res = await service_layer.verify_resolution(db, incident_id, post_telemetry=payload.post_telemetry)
    if not res:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResolutionVerificationResponse(
        incident_id=res.incident_id,
        resolution_verified=res.resolution_verified,
        service=res.service,
        remaining_risk=res.remaining_risk,
        verification_evidence=res.verification_evidence,
        pre_remediation_summary=res.pre_remediation_summary,
        post_remediation_summary=res.post_remediation_summary,
        service_health_score=res.service_health_score,
        verified_at=res.verified_at,
    )


@router.post(
    "/{incident_id}/close",
    response_model=IncidentResponse,
    summary="Close incident",
)
async def close_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Mark an incident as CLOSED after verified resolution."""
    closed = await service_layer.close(db, incident_id)
    if not closed:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(closed)


@router.post(
    "/{incident_id}/reopen",
    response_model=IncidentResponse,
    summary="Reopen incident",
)
async def reopen_incident(
    incident_id: uuid.UUID,
    payload: IncidentReopenRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Reopens an incident if regression or recurring errors are detected."""
    reopened = await service_layer.reopen(db, incident_id, reason=payload.reason, reopened_by=payload.reopened_by)
    if not reopened:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(reopened)


@router.post(
    "/{incident_id}/assign",
    response_model=IncidentResponse,
    summary="Assign incident",
)
async def assign_incident(
    incident_id: uuid.UUID,
    payload: IncidentAssignRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Assign incident to an SRE engineer or on-call team."""
    assigned = await service_layer.assign(db, incident_id, payload.assigned_to)
    if not assigned:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentResponse.model_validate(assigned)


@router.get(
    "/{incident_id}/evidence",
    response_model=IncidentEvidenceGraphResponse,
    summary="Get structured incident evidence graph",
)
async def get_incident_evidence(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Retrieve structured evidence graph categorized by metrics, logs, traces, alerts, deployments, and k8s."""
    ev_graph = await service_layer.get_evidence_graph(db, incident_id)
    if not ev_graph:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return IncidentEvidenceGraphResponse(**ev_graph)


@router.get(
    "/{incident_id}/blast-radius",
    response_model=BlastRadiusResponse,
    summary="Get incident blast radius (alias for /impact)",
)
async def get_incident_blast_radius_alias(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Alias route for blast radius calculation."""
    impact = await service_layer.get_impact(db, incident_id)
    if not impact:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return BlastRadiusResponse(**impact)


@router.get(
    "/{incident_id}/recommendations",
    response_model=list[dict[str, Any]],
    summary="Get incident recommendations",
)
async def get_incident_recommendations(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Get list of actionable remediation steps for an incident."""
    incident = await service_layer.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return incident.recommended_actions or []


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete incident")
async def delete_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Delete an incident by ID."""
    success = await service_layer.delete(db, incident_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return None
