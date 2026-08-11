"""
Distributed Tracing Platform REST API Endpoints.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.trace import (
    ServiceMapResponse,
    ServiceMetricsResponse,
    TraceAIAnalysisResponse,
    TraceListResponse,
    TraceResponse,
)
from app.services.trace_service import TraceService, generate_sample_trace_tree, trace_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_trace_service() -> TraceService:
    return trace_service


async def _seed_initial_traces_if_empty(db: AsyncSession, service: TraceService) -> None:
    traces, total, _ = await service.list_traces(db, size=1)
    if total == 0:
        log.info("seeding_initial_distributed_traces")
        sample_traces = [
            generate_sample_trace_tree(
                "tr-94821a0b", "POST /api/v1/checkout", "api-gateway", "error", 654.5
            ),
            generate_sample_trace_tree(
                "tr-10293b8c", "POST /api/v1/auth/login", "auth-service", "ok", 84.2
            ),
            generate_sample_trace_tree(
                "tr-55410c9d", "GET /api/v1/users/me", "user-service", "ok", 42.8
            ),
            generate_sample_trace_tree(
                "tr-88912d3e", "POST /api/v1/billing/charge", "billing-service", "error", 980.4
            ),
            generate_sample_trace_tree(
                "tr-33214e5f", "GET /api/v1/notifications/list", "notification-service", "ok", 112.5
            ),
        ]
        for tr in sample_traces:
            db.add(tr)
        await db.commit()


@router.get("/traces", response_model=TraceListResponse, summary="List distributed traces")
async def list_traces(
    service: str | None = Query(None, description="Filter by service name"),
    status: str | None = Query(None, description="Filter by status (ok, error)"),
    min_duration_ms: float | None = Query(None, description="Minimum duration in ms"),
    max_duration_ms: float | None = Query(None, description="Maximum duration in ms"),
    search: str | None = Query(None, description="Search trace name or trace_id"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Retrieve paginated list of distributed traces with filters."""
    await _seed_initial_traces_if_empty(db, service_layer)
    items, total, pages = await service_layer.list_traces(
        db,
        service=service,
        status=status,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        search=search,
        page=page,
        size=size,
    )
    return TraceListResponse(
        items=[TraceResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/traces/{trace_id}", response_model=TraceResponse, summary="Get trace detail & span tree"
)
async def get_trace(
    trace_id: str,
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Retrieve single trace with complete OpenTelemetry span tree."""
    await _seed_initial_traces_if_empty(db, service_layer)
    trace = await service_layer.get_by_trace_id(db, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found.")
    return TraceResponse.model_validate(trace)


@router.post(
    "/traces/{trace_id}/analyze",
    response_model=TraceAIAnalysisResponse,
    summary="Analyze trace with Gemini AI",
)
async def analyze_trace(
    trace_id: str,
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Trigger Google Gemini AI to analyze span tree bottlenecks and root cause."""
    await _seed_initial_traces_if_empty(db, service_layer)
    return await service_layer.analyze_trace(db, trace_id)


@router.get("/services/map", response_model=ServiceMapResponse, summary="Get Service Topology Map")
async def get_service_map(
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Retrieve interactive microservices topology graph nodes and edges."""
    await _seed_initial_traces_if_empty(db, service_layer)
    return await service_layer.get_service_map(db)


@router.get("/services/dependencies", summary="Get service dependencies list")
async def get_service_dependencies(
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Retrieve service dependency list."""
    await _seed_initial_traces_if_empty(db, service_layer)
    service_map = await service_layer.get_service_map(db)
    return {"dependencies": service_map.edges}


@router.get(
    "/services/{service_name}/metrics",
    response_model=ServiceMetricsResponse,
    summary="Get service performance metrics",
)
async def get_service_metrics(
    service_name: str,
    db: AsyncSession = Depends(get_db),
    service_layer: TraceService = Depends(get_trace_service),
):
    """Retrieve performance metrics (latency, RPS, error rate) for a specific service."""
    await _seed_initial_traces_if_empty(db, service_layer)
    return await service_layer.get_service_metrics(db, service_name)
