"""
REST API Endpoints for Unified Telemetry Intelligence Platform.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.telemetry.schemas.telemetry import (
    AIOperationalSummary,
    LogIngestPayload,
    MetricIngestPayload,
    MetricRecordResponse,
    TelemetryEventResponse,
    TelemetryHealthResponse,
    TraceIngestPayload,
    TraceRecordResponse,
)
from app.telemetry.services.telemetry_service import telemetry_service

router = APIRouter()


@router.post("/logs", response_model=TelemetryEventResponse, status_code=status.HTTP_201_CREATED, summary="Ingest Application & System Logs")
async def ingest_logs(
    payload: LogIngestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Ingests log records into the telemetry pipeline, normalizes severity, and classifies anomalies."""
    event = await telemetry_service.ingest_log(db, payload=payload, organization_id=current_user.organization_id)
    return TelemetryEventResponse.model_validate(event)


@router.post("/metrics", response_model=MetricRecordResponse, status_code=status.HTTP_201_CREATED, summary="Ingest Resource Metrics")
async def ingest_metrics(
    payload: MetricIngestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Ingests numerical time-series metrics and computes AI statistical deviations."""
    result = await telemetry_service.ingest_metric(db, payload=payload, organization_id=current_user.organization_id)
    return MetricRecordResponse.model_validate(result["record"])


@router.post("/traces", response_model=list[TraceRecordResponse], status_code=status.HTTP_201_CREATED, summary="Ingest Distributed Traces")
async def ingest_traces(
    payload: TraceIngestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Ingests distributed tracing spans and detects execution latency bottlenecks."""
    records = await telemetry_service.ingest_trace(db, payload=payload, organization_id=current_user.organization_id)
    return [TraceRecordResponse.model_validate(r) for r in records]


@router.get("/events", response_model=list[TelemetryEventResponse], summary="List Telemetry Events")
async def list_telemetry_events(
    limit: int = Query(50, ge=1, le=200, description="Max events to return"),
    severity: str | None = Query(None, description="Filter by severity (CRITICAL, ERROR, WARN, INFO)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Retrieves real-time telemetry event records across all connected infrastructure sources."""
    events = await telemetry_service.get_recent_events(db, limit=limit, severity=severity)
    return [TelemetryEventResponse.model_validate(e) for e in events]


@router.get("/health", response_model=TelemetryHealthResponse, summary="Get Pipeline Health")
async def get_telemetry_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Returns telemetry pipeline throughput, collector status, and active anomaly counters."""
    return await telemetry_service.get_health(db)


@router.get("/ai-summary", response_model=AIOperationalSummary, summary="Get AI Operational Summary")
async def get_ai_operational_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Generates an intelligent operational summary correlating cross-pipeline signals."""
    return await telemetry_service.generate_operational_summary(db, organization_id=current_user.organization_id)
