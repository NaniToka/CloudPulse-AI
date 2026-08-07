"""
Incident Management Center API endpoints & WebSockets.
Refactored with Service Layer and Repository Pattern.
"""

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentAIAnalysisResponse,
    IncidentAnalyticsResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentResolve,
    IncidentResponse,
    IncidentStatsResponse,
    IncidentUpdate,
    MonthlyTrendPoint,
    SeverityCount,
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
        sample_incidents = [
            Incident(
                title="P99 Latency degradation on Payment API",
                description="Payment API response time exceeded 2.5s threshold due to Redis cache eviction spike.",
                severity="P0",
                priority="Critical",
                status="Investigating",
                affected_service="payment-service",
                affected_region="us-east-1",
                assigned_engineer="Sarah Chen (SRE Lead)",
                assigned_to="Sarah Chen (SRE Lead)",
                created_by="AlertManager Bot",
                started_at=datetime(2026, 8, 5, 21, 30, tzinfo=UTC),
                created_at=datetime(2026, 8, 5, 21, 30, tzinfo=UTC),
                ai_summary="Payment Gateway latency breached SLO. Redis cache eviction rates increased by 320%.",
                root_cause="Redis memory limit reached maxmemory threshold (2GB), evicting session tokens.",
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
                title="High CPU Saturation on Auth Worker Node",
                description="Kubernetes worker pool node-us-east-1a CPU utilization at 98% for > 15 minutes.",
                severity="P1",
                priority="High",
                status="Monitoring",
                affected_service="auth-service",
                affected_region="us-west-2",
                assigned_engineer="Alex Rivera (DevOps)",
                assigned_to="Alex Rivera (DevOps)",
                created_by="Datadog Webhook",
                started_at=datetime(2026, 8, 5, 20, 15, tzinfo=UTC),
                created_at=datetime(2026, 8, 5, 20, 15, tzinfo=UTC),
                ai_summary="Auth Service worker node CPU throttled due to JWT verification thread pool lock contention.",
                root_cause="Unbounded bcrypt hashing thread pool blocking Node event loop under load burst.",
                ai_root_cause="Unbounded bcrypt hashing thread pool blocking Node event loop under load burst.",
                ai_business_impact="Login duration increased from 120ms to 850ms.",
                ai_immediate_mitigation="Scale auth-service replicas from 4 to 10 instances.",
                ai_suggested_resolution="Scale auth-service replicas from 4 to 10 instances.",
                ai_long_term_prevention=[
                    "Migrate password hashing to worker pool",
                    "Add HPA target at 70% CPU",
                ],
                ai_preventive_actions=[
                    "Migrate password hashing to worker pool",
                    "Add HPA target at 70% CPU",
                ],
                ai_similar_incidents=[
                    {"id": "INC-388", "title": "Bcrypt worker bottleneck", "similarity": "86%"}
                ],
                ai_estimated_resolution_time="20 mins",
                ai_confidence_score=0.92,
            ),
            Incident(
                title="Database Connection Pool Exhaustion",
                description="PostgreSQL primary instance rejected connections: max_connections (200) reached.",
                severity="P0",
                priority="Critical",
                status="Open",
                affected_service="database-cluster",
                affected_region="us-east-1",
                assigned_engineer="Marcus Vance (DBA)",
                assigned_to="Marcus Vance (DBA)",
                created_by="CloudPulse Monitor",
                started_at=datetime(2026, 8, 5, 22, 45, tzinfo=UTC),
                created_at=datetime(2026, 8, 5, 22, 45, tzinfo=UTC),
                ai_summary="DB Connection Pool exhausted by leaked idle connections from microservice worker pods.",
                root_cause="Unclosed DB session instances in background retry loop during network micro-outage.",
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
            Incident(
                title="S3 Bucket Rate Limit Throttling",
                description="Object storage GET requests returning HTTP 503 Slow Down rate limit responses.",
                severity="P2",
                priority="Medium",
                status="Resolved",
                affected_service="storage-service",
                affected_region="eu-west-1",
                assigned_engineer="Elena Rostova (Cloud Eng)",
                assigned_to="Elena Rostova (Cloud Eng)",
                created_by="System User",
                started_at=datetime(2026, 8, 4, 14, 0, tzinfo=UTC),
                created_at=datetime(2026, 8, 4, 14, 0, tzinfo=UTC),
                resolved_at=datetime(2026, 8, 4, 14, 35, tzinfo=UTC),
                resolution_notes="Partitioned S3 key prefixes with hash prefixing to distribute request partitions.",
                resolved_by="Elena Rostova",
                ai_summary="S3 prefix partition limit hit (3,500 GET req/s limit per prefix).",
                root_cause="Static path prefix structure `/logs/2026-08/` caused request hotspot.",
                ai_root_cause="Static path prefix structure `/logs/2026-08/` caused request hotspot.",
                ai_business_impact="Log export pipeline delayed by 35 minutes.",
                ai_immediate_mitigation="Distribute prefix with hex hashes `/logs/{hash}/2026-08/`.",
                ai_suggested_resolution="Distribute prefix with hex hashes `/logs/{hash}/2026-08/`.",
                ai_long_term_prevention=["Automate key prefix distribution rule"],
                ai_preventive_actions=["Automate key prefix distribution rule"],
                ai_similar_incidents=[],
                ai_estimated_resolution_time="30 mins",
                ai_confidence_score=0.91,
            ),
        ]
        for inc in sample_incidents:
            db.add(inc)
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
    """Retrieve list of currently active (non-resolved, non-closed) incidents."""
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


@router.get("", response_model=IncidentListResponse, summary="List incidents")
async def list_incidents(
    status: str | None = Query(
        None, description="Filter by status (Open, Investigating, Monitoring, Resolved, Closed)"
    ),
    severity: str | None = Query(None, description="Filter by severity (P0, P1, P2, P3)"),
    priority: str | None = Query(
        None, description="Filter by priority (Critical, High, Medium, Low)"
    ),
    service: str | None = Query(None, description="Filter by affected service"),
    search: str | None = Query(None, description="Search term in title or description"),
    sort_by: str = Query(
        "created_at", description="Sort field (created_at, severity, priority, status)"
    ),
    sort_dir: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Retrieve paginated list of incidents with filters, search, and sorting."""
    await _seed_initial_incidents_if_empty(db, service_layer)

    incidents, total, pages = await service_layer.list_incidents(
        db,
        status=status,
        severity=severity,
        priority=priority,
        service=service,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        size=size,
    )

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(inc) for inc in incidents],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/analytics", response_model=IncidentAnalyticsResponse, summary="Incident analytics & charts"
)
async def get_incident_analytics(
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Get metrics for incident analytics charts."""
    await _seed_initial_incidents_if_empty(db, service_layer)

    incidents, total_incidents, _ = await service_layer.list_incidents(db, size=100)
    stats = await service_layer.get_stats(db)

    # Severity counts
    sev_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    resolved_count = 0
    for inc in incidents:
        if inc.severity in sev_counts:
            sev_counts[inc.severity] += 1
        if inc.status in ["Resolved", "Closed"]:
            resolved_count += 1

    incidents_by_severity = [SeverityCount(severity=s, count=c) for s, c in sev_counts.items()]

    active_incidents = total_incidents - resolved_count
    resolution_rate = (
        round((resolved_count / total_incidents) * 100, 1) if total_incidents > 0 else 0.0
    )

    monthly_trend = [
        MonthlyTrendPoint(month="Mar", count=14, resolved_count=12),
        MonthlyTrendPoint(month="Apr", count=18, resolved_count=16),
        MonthlyTrendPoint(month="May", count=11, resolved_count=10),
        MonthlyTrendPoint(month="Jun", count=19, resolved_count=18),
        MonthlyTrendPoint(month="Jul", count=15, resolved_count=14),
        MonthlyTrendPoint(month="Aug", count=total_incidents, resolved_count=resolved_count),
    ]

    return IncidentAnalyticsResponse(
        incidents_by_severity=incidents_by_severity,
        mean_time_to_resolve_minutes=stats.avg_resolution_time_minutes,
        monthly_trend=monthly_trend,
        resolution_rate_percent=resolution_rate,
        active_incidents=active_incidents,
        resolved_incidents=resolved_count,
        total_incidents=total_incidents,
        sla_compliance_percent=stats.sla_compliance_percent,
    )


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
    """Update incident attributes, broadcasting WebSockets when status/severity/assignment change."""
    updated = await service_layer.update(db, incident_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(updated)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse, summary="Resolve incident")
async def resolve_incident(
    incident_id: uuid.UUID,
    payload: IncidentResolve,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Mark incident as resolved with resolution notes and broadcast real-time update."""
    resolved = await service_layer.resolve(db, incident_id, payload)
    if not resolved:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(resolved)


@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentAIAnalysisResponse,
    summary="Re-run Gemini AI analysis",
)
async def reanalyze_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: IncidentService = Depends(get_incident_service),
):
    """Trigger or refresh Google Gemini AI analysis for a specific incident."""
    ai_data = await service_layer.analyze(db, incident_id)
    if not ai_data:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentAIAnalysisResponse(
        ai_summary=ai_data["ai_summary"],
        root_cause=ai_data["root_cause"],
        ai_root_cause=ai_data["ai_root_cause"],
        ai_business_impact=ai_data["ai_business_impact"],
        ai_suggested_resolution=ai_data["ai_suggested_resolution"],
        ai_immediate_mitigation=ai_data["ai_immediate_mitigation"],
        ai_long_term_prevention=ai_data.get("ai_long_term_prevention", []),
        ai_preventive_actions=ai_data.get("ai_preventive_actions", []),
        ai_similar_incidents=ai_data.get("ai_similar_incidents", []),
        ai_estimated_resolution_time=ai_data.get("ai_estimated_resolution_time", "30 minutes"),
        ai_confidence_score=ai_data.get("ai_confidence_score", 0.94),
    )


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
