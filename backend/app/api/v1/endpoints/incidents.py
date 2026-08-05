"""
Incident Management Center API endpoints & WebSockets.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResolve,
    IncidentResponse,
    IncidentListResponse,
    IncidentAnalyticsResponse,
    SeverityCount,
    MonthlyTrendPoint,
    IncidentAIAnalysisResponse,
)
from app.services.incident_ai_service import analyze_incident_with_gemini
from app.services.websocket_manager import incident_ws_manager

log = structlog.get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Seed initial sample data if DB is empty
# ---------------------------------------------------------------------------
async def _seed_initial_incidents_if_empty(db: AsyncSession) -> None:
    count_stmt = select(func.count(Incident.id))
    result = await db.execute(count_stmt)
    total = result.scalar() or 0

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
                assigned_engineer="Sarah Chen (SRE Lead)",
                created_by="AlertManager Bot",
                created_at=datetime(2026, 8, 5, 21, 30, tzinfo=timezone.utc),
                ai_summary="Payment Gateway latency breached SLO. Redis cache eviction rates increased by 320%.",
                ai_root_cause="Redis memory limit reached maxmemory threshold (2GB), evicting session tokens.",
                ai_business_impact="Checkout conversion rate dropped by 8.4% during peak window.",
                ai_suggested_resolution="1. Scale Redis instance to 8GB.\n2. Evict orphan telemetry keys.\n3. Increase timeout limit.",
                ai_preventive_actions=["Enable Memory Autoscaling", "Implement Key TTL audit policy"],
                ai_similar_incidents=[{"id": "INC-402", "title": "Cache memory exhaustion", "similarity": "91%"}],
                ai_estimated_resolution_time="15-25 mins",
            ),
            Incident(
                title="High CPU Saturation on Auth Worker Node",
                description="Kubernetes worker pool node-us-east-1a CPU utilization at 98% for > 15 minutes.",
                severity="P1",
                priority="High",
                status="Monitoring",
                affected_service="auth-service",
                assigned_engineer="Alex Rivera (DevOps)",
                created_by="Datadog Webhook",
                created_at=datetime(2026, 8, 5, 20, 15, tzinfo=timezone.utc),
                ai_summary="Auth Service worker node CPU throttled due to JWT verification thread pool lock contention.",
                ai_root_cause="Unbounded bcrypt hashing thread pool blocking Node event loop under load burst.",
                ai_business_impact="Login duration increased from 120ms to 850ms.",
                ai_suggested_resolution="Scale auth-service replicas from 4 to 10 instances.",
                ai_preventive_actions=["Migrate password hashing to worker pool", "Add HPA target at 70% CPU"],
                ai_similar_incidents=[{"id": "INC-388", "title": "Bcrypt worker bottleneck", "similarity": "86%"}],
                ai_estimated_resolution_time="20 mins",
            ),
            Incident(
                title="Database Connection Pool Exhaustion",
                description="PostgreSQL primary instance rejected connections: max_connections (200) reached.",
                severity="P0",
                priority="Critical",
                status="Open",
                affected_service="database-cluster",
                assigned_engineer="Marcus Vance (DBA)",
                created_by="CloudPulse Monitor",
                created_at=datetime(2026, 8, 5, 22, 45, tzinfo=timezone.utc),
                ai_summary="DB Connection Pool exhausted by leaked idle connections from microservice worker pods.",
                ai_root_cause="Unclosed DB session instances in background retry loop during network micro-outage.",
                ai_business_impact="Write requests failing across 3 downstream services.",
                ai_suggested_resolution="Execute PgBouncer connection reset and restart leaking worker deployments.",
                ai_preventive_actions=["Configure PgBouncer transaction pooling mode", "Set max_db_idle_time=30s"],
                ai_similar_incidents=[{"id": "INC-290", "title": "PgBouncer pool exhaustion", "similarity": "95%"}],
                ai_estimated_resolution_time="10-15 mins",
            ),
            Incident(
                title="S3 Bucket Rate Limit Throttling",
                description="Object storage GET requests returning HTTP 503 Slow Down rate limit responses.",
                severity="P2",
                priority="Medium",
                status="Resolved",
                affected_service="storage-service",
                assigned_engineer="Elena Rostova (Cloud Eng)",
                created_by="System User",
                created_at=datetime(2026, 8, 4, 14, 0, tzinfo=timezone.utc),
                resolved_at=datetime(2026, 8, 4, 14, 35, tzinfo=timezone.utc),
                resolution_notes="Partitioned S3 key prefixes with hash prefixing to distribute request partitions.",
                resolved_by="Elena Rostova",
                ai_summary="S3 prefix partition limit hit (3,500 GET req/s limit per prefix).",
                ai_root_cause="Static path prefix structure `/logs/2026-08/` caused request hotspot.",
                ai_business_impact="Log export pipeline delayed by 35 minutes.",
                ai_suggested_resolution="Distribute prefix with hex hashes `/logs/{hash}/2026-08/`.",
                ai_preventive_actions=["Automate key prefix distribution rule"],
                ai_similar_incidents=[],
                ai_estimated_resolution_time="30 mins",
            ),
            Incident(
                title="Kafka Consumer Group Rebalance Loop",
                description="Telemetry consumer group continually rebalancing due to heartbeat timeout.",
                severity="P3",
                priority="Low",
                status="Closed",
                affected_service="kafka-ingestion",
                assigned_engineer="David Kim (Platform Eng)",
                created_by="Kafka Exporter",
                created_at=datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc),
                resolved_at=datetime(2026, 8, 3, 10, 40, tzinfo=timezone.utc),
                resolution_notes="Increased max.poll.interval.ms from 300000ms to 600000ms.",
                resolved_by="David Kim",
                ai_summary="High message processing time per batch caused consumer heartbeat timeout.",
                ai_root_cause="Batch size max.poll.records=500 was too large for heavy payload parsing.",
                ai_business_impact="Minor telemetry metrics latency offset.",
                ai_suggested_resolution="Reduce batch size or increase poll timeout.",
                ai_preventive_actions=["Tune max.poll.records to 150"],
                ai_similar_incidents=[],
                ai_estimated_resolution_time="40 mins",
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
            # Keep-alive heartbeat / receiver loop
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

@router.get("", response_model=IncidentListResponse, summary="List incidents")
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (Open, Investigating, Monitoring, Resolved, Closed)"),
    severity: Optional[str] = Query(None, description="Filter by severity (P0, P1, P2, P3)"),
    priority: Optional[str] = Query(None, description="Filter by priority (Critical, High, Medium, Low)"),
    service: Optional[str] = Query(None, description="Filter by affected service"),
    search: Optional[str] = Query(None, description="Search term in title or description"),
    sort_by: str = Query("created_at", description="Sort field (created_at, severity, priority, status)"),
    sort_dir: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated list of incidents with filters, search, and sorting."""
    await _seed_initial_incidents_if_empty(db)

    query = select(Incident)

    # Filters
    filters = []
    if status:
        filters.append(func.lower(Incident.status) == status.lower())
    if severity:
        filters.append(func.upper(Incident.severity) == severity.upper())
    if priority:
        filters.append(func.lower(Incident.priority) == priority.lower())
    if service:
        filters.append(func.lower(Incident.affected_service) == service.lower())
    if search:
        search_pattern = f"%{search.lower()}%"
        filters.append(
            or_(
                func.lower(Incident.title).like(search_pattern),
                func.lower(Incident.description).like(search_pattern),
                func.lower(Incident.affected_service).like(search_pattern),
                func.lower(Incident.assigned_engineer).like(search_pattern),
            )
        )

    if filters:
        query = query.where(and_(*filters))

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    # Sorting
    sort_column = getattr(Incident, sort_by, Incident.created_at)
    if sort_dir.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    incidents = result.scalars().all()
    pages = math.ceil(total / size) if total > 0 else 1

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(inc) for inc in incidents],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/analytics", response_model=IncidentAnalyticsResponse, summary="Incident analytics & charts")
async def get_incident_analytics(db: AsyncSession = Depends(get_db)):
    """Get metrics for incident analytics: Incidents by Severity, MTTR, Monthly Trend, Resolution Rate, Active vs Resolved."""
    await _seed_initial_incidents_if_empty(db)

    # Severity counts
    sev_stmt = select(Incident.severity, func.count(Incident.id)).group_by(Incident.severity)
    sev_res = await db.execute(sev_stmt)
    sev_dict = {s: c for s, c in sev_res.all()}
    all_severities = ["P0", "P1", "P2", "P3"]
    incidents_by_severity = [
        SeverityCount(severity=s, count=sev_dict.get(s, 0)) for s in all_severities
    ]

    # Total, Active, Resolved
    total_res = await db.execute(select(func.count(Incident.id)))
    total_incidents = total_res.scalar() or 0

    resolved_res = await db.execute(
        select(func.count(Incident.id)).where(func.lower(Incident.status).in_(["resolved", "closed"]))
    )
    resolved_incidents = resolved_res.scalar() or 0
    active_incidents = total_incidents - resolved_incidents

    # Resolution Rate
    resolution_rate_percent = (
        round((resolved_incidents / total_incidents) * 100, 1) if total_incidents > 0 else 0.0
    )

    # Mean Time To Resolve (MTTR)
    resolved_query = select(Incident).where(Incident.resolved_at.isnot(None))
    res_items = (await db.execute(resolved_query)).scalars().all()
    
    total_diff_minutes = 0.0
    valid_mttr_count = 0
    for inc in res_items:
        if inc.resolved_at and inc.created_at:
            diff = (inc.resolved_at - inc.created_at).total_seconds() / 60.0
            if diff >= 0:
                total_diff_minutes += diff
                valid_mttr_count += 1
    
    mttr_minutes = round(total_diff_minutes / valid_mttr_count, 1) if valid_mttr_count > 0 else 28.5

    # Monthly Trend (Mock / Calculated)
    monthly_trend = [
        MonthlyTrendPoint(month="Mar", count=14, resolved_count=12),
        MonthlyTrendPoint(month="Apr", count=18, resolved_count=16),
        MonthlyTrendPoint(month="May", count=11, resolved_count=10),
        MonthlyTrendPoint(month="Jun", count=19, resolved_count=18),
        MonthlyTrendPoint(month="Jul", count=15, resolved_count=14),
        MonthlyTrendPoint(month="Aug", count=total_incidents, resolved_count=resolved_incidents),
    ]

    return IncidentAnalyticsResponse(
        incidents_by_severity=incidents_by_severity,
        mean_time_to_resolve_minutes=mttr_minutes,
        monthly_trend=monthly_trend,
        resolution_rate_percent=resolution_rate_percent,
        active_incidents=active_incidents,
        resolved_incidents=resolved_incidents,
        total_incidents=total_incidents,
    )


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, summary="Create incident")
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new incident, automatically invoke Gemini AI analysis, and broadcast WebSocket notification."""
    now = datetime.now(timezone.utc)
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity.value,
        priority=payload.priority.value,
        status=payload.status.value,
        affected_service=payload.affected_service or "api-gateway",
        affected_services=payload.affected_services or [payload.affected_service or "api-gateway"],
        assigned_engineer=payload.assigned_engineer,
        created_by=payload.created_by or "System User",
        created_at=now,
        updated_at=now,
    )

    if payload.auto_analyze:
        ai_data = await analyze_incident_with_gemini(
            title=payload.title,
            description=payload.description or "",
            severity=payload.severity.value,
            priority=payload.priority.value,
            affected_service=payload.affected_service or "api-gateway",
        )
        incident.ai_summary = ai_data.get("ai_summary")
        incident.ai_root_cause = ai_data.get("ai_root_cause")
        incident.ai_business_impact = ai_data.get("ai_business_impact")
        incident.ai_suggested_resolution = ai_data.get("ai_suggested_resolution")
        incident.ai_preventive_actions = ai_data.get("ai_preventive_actions")
        incident.ai_similar_incidents = ai_data.get("ai_similar_incidents")
        incident.ai_estimated_resolution_time = ai_data.get("ai_estimated_resolution_time")

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    response_data = IncidentResponse.model_validate(incident)

    # Broadcast WebSocket Event
    await incident_ws_manager.broadcast({
        "event": "incident_created",
        "data": response_data.model_dump(mode="json"),
        "timestamp": now.isoformat(),
    })

    return response_data


@router.get("/{incident_id}", response_model=IncidentResponse, summary="Get incident details")
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single incident by ID."""
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    return IncidentResponse.model_validate(incident)


@router.put("/{incident_id}", response_model=IncidentResponse, summary="Update incident")
async def update_incident(incident_id: uuid.UUID, payload: IncidentUpdate, db: AsyncSession = Depends(get_db)):
    """Update incident attributes, broadcasting WebSockets when status/severity/assignment change."""
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    old_severity = incident.severity
    old_assigned = incident.assigned_engineer
    old_status = incident.status

    if payload.title is not None:
        incident.title = payload.title
    if payload.description is not None:
        incident.description = payload.description
    if payload.severity is not None:
        incident.severity = payload.severity.value
    if payload.priority is not None:
        incident.priority = payload.priority.value
    if payload.status is not None:
        incident.status = payload.status.value
        if payload.status.value in ["Resolved", "Closed"] and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)
    if payload.affected_service is not None:
        incident.affected_service = payload.affected_service
    if payload.affected_services is not None:
        incident.affected_services = payload.affected_services
    if payload.assigned_engineer is not None:
        incident.assigned_engineer = payload.assigned_engineer
    if payload.resolution_notes is not None:
        incident.resolution_notes = payload.resolution_notes

    incident.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(incident)

    resp = IncidentResponse.model_validate(incident)

    # WebSockets events trigger
    if old_severity != incident.severity:
        await incident_ws_manager.broadcast({
            "event": "severity_changed",
            "incident_id": str(incident.id),
            "old_severity": old_severity,
            "new_severity": incident.severity,
            "data": resp.model_dump(mode="json"),
        })

    if old_assigned != incident.assigned_engineer:
        await incident_ws_manager.broadcast({
            "event": "assignment_changed",
            "incident_id": str(incident.id),
            "old_engineer": old_assigned,
            "new_engineer": incident.assigned_engineer,
            "data": resp.model_dump(mode="json"),
        })

    if old_status != incident.status:
        await incident_ws_manager.broadcast({
            "event": "status_changed",
            "incident_id": str(incident.id),
            "old_status": old_status,
            "new_status": incident.status,
            "data": resp.model_dump(mode="json"),
        })

    return resp


@router.post("/{incident_id}/resolve", response_model=IncidentResponse, summary="Resolve incident")
async def resolve_incident(incident_id: uuid.UUID, payload: IncidentResolve, db: AsyncSession = Depends(get_db)):
    """Mark incident as resolved with resolution notes and broadcast real-time update."""
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    incident.status = "Resolved"
    incident.resolution_notes = payload.resolution_notes
    incident.resolved_by = payload.resolved_by or "Engineer"
    incident.resolved_at = datetime.now(timezone.utc)
    incident.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(incident)

    resp = IncidentResponse.model_validate(incident)

    # Broadcast WebSocket event
    await incident_ws_manager.broadcast({
        "event": "incident_resolved",
        "incident_id": str(incident.id),
        "resolution_notes": payload.resolution_notes,
        "data": resp.model_dump(mode="json"),
    })

    return resp


@router.post("/{incident_id}/analyze", response_model=IncidentAIAnalysisResponse, summary="Re-run Gemini AI analysis")
async def reanalyze_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Trigger or refresh Google Gemini AI analysis for a specific incident."""
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    ai_data = await analyze_incident_with_gemini(
        title=incident.title,
        description=incident.description or "",
        severity=incident.severity,
        priority=incident.priority,
        affected_service=incident.affected_service or "api-gateway",
    )

    incident.ai_summary = ai_data["ai_summary"]
    incident.ai_root_cause = ai_data["ai_root_cause"]
    incident.ai_business_impact = ai_data["ai_business_impact"]
    incident.ai_suggested_resolution = ai_data["ai_suggested_resolution"]
    incident.ai_preventive_actions = ai_data["ai_preventive_actions"]
    incident.ai_similar_incidents = ai_data["ai_similar_incidents"]
    incident.ai_estimated_resolution_time = ai_data["ai_estimated_resolution_time"]
    incident.updated_at = datetime.now(timezone.utc)

    await db.commit()

    return IncidentAIAnalysisResponse(
        ai_summary=incident.ai_summary,
        ai_root_cause=incident.ai_root_cause,
        ai_business_impact=incident.ai_business_impact,
        ai_suggested_resolution=incident.ai_suggested_resolution,
        ai_preventive_actions=incident.ai_preventive_actions or [],
        ai_similar_incidents=incident.ai_similar_incidents or [],
        ai_estimated_resolution_time=incident.ai_estimated_resolution_time or "30 minutes",
    )


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete incident")
async def delete_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete an incident by ID."""
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    await db.delete(incident)
    await db.commit()
    return None
