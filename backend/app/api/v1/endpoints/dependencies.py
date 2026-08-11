"""
AI Service Dependency & Root-Cause Intelligence REST API Endpoints.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.dependency import (
    BlastRadiusRequest,
    BlastRadiusResponse,
    DependencyDiscoveryRequest,
    DependencyDiscoveryResponse,
    DependencyGraphResponse,
    RootCauseRankingRequest,
    RootCauseRankingResponse,
    ServiceHealthResponse,
    ServiceListResponse,
    ServiceNodeDetailResponse,
)
from app.services.service_dependency_service import (
    ServiceDependencyService,
    service_dependency_service,
)

log = structlog.get_logger(__name__)

router = APIRouter()


def get_dependency_service() -> ServiceDependencyService:
    return service_dependency_service


@router.post(
    "/discover",
    response_model=DependencyDiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger automatic dependency discovery",
)
async def discover_dependencies(
    payload: DependencyDiscoveryRequest = DependencyDiscoveryRequest(),
    db: AsyncSession = Depends(get_db),
    service: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Discovers, scores, and synchronizes service dependencies from traces, logs, metrics, K8s, and Cloud resources.
    """
    return await service.discover(
        db,
        time_window_minutes=payload.time_window_minutes,
        include_traces=payload.include_traces,
        include_logs=payload.include_logs,
        include_k8s=payload.include_k8s,
        include_cloud=payload.include_cloud,
    )


@router.get(
    "/graph",
    response_model=DependencyGraphResponse,
    summary="Get Service Dependency Graph",
)
async def get_dependency_graph(
    environment: str | None = Query(None, description="Filter by environment (production, staging, dev)"),
    region: str | None = Query(None, description="Filter by cloud region"),
    service: str | None = Query(None, description="Root service name for depth-limited traversal"),
    depth: int = Query(5, ge=1, le=20, description="Traversal depth limit"),
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Retrieves full or filtered Service Dependency Graph nodes and edges.
    """
    return await service_layer.get_graph(
        db,
        environment=environment,
        region=region,
        service=service,
        depth=depth,
    )


@router.get(
    "/services",
    response_model=ServiceListResponse,
    summary="List Service Nodes with health metrics",
)
async def list_services(
    environment: str | None = Query(None, description="Filter by environment"),
    region: str | None = Query(None, description="Filter by region"),
    status: str | None = Query(None, description="Filter by status (HEALTHY, DEGRADED, CRITICAL, UNKNOWN)"),
    search: str | None = Query(None, description="Search service name or type"),
    sort_by: str = Query("name", description="Sort column (name, health_score, error_rate, latency_p99_ms)"),
    sort_dir: str = Query("asc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Retrieves paginated list of service nodes with their live health scores and error rates.
    """
    return await service_layer.list_services(
        db,
        environment=environment,
        region=region,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        size=size,
    )


@router.get(
    "/services/{service_id}",
    response_model=ServiceNodeDetailResponse,
    summary="Get Service Node details and upstream/downstream dependencies",
)
async def get_service_detail(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Retrieves service details, upstream caller dependencies, downstream called dependencies, and active incidents.
    """
    detail = await service_layer.get_service_detail(db, service_id=service_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Service node '{service_id}' not found.")
    return detail


@router.get(
    "/services/{service_id}/health",
    response_model=ServiceHealthResponse,
    summary="Get live Service Health Score & factors",
)
async def get_service_health(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Calculates live mathematical health score (0-100), status, and degradation factors for a service.
    """
    health = await service_layer.get_service_health(db, service_id=service_id)
    if not health:
        raise HTTPException(status_code=404, detail=f"Service node '{service_id}' not found.")
    return health


@router.post(
    "/blast-radius",
    response_model=BlastRadiusResponse,
    summary="Calculate failure blast radius and propagation path",
)
async def calculate_blast_radius_endpoint(
    payload: BlastRadiusRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Simulates failure on root service and traces downstream blast radius, cascading propagation hops, and user impact.
    """
    return await service_layer.calculate_blast_radius(
        db,
        service_name=payload.service_name,
        depth=payload.depth,
    )


@router.post(
    "/root-cause",
    response_model=RootCauseRankingResponse,
    summary="Rank root cause candidates with explainable scoring & AI",
)
async def rank_root_cause_endpoint(
    payload: RootCauseRankingRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Executes transparent 4-factor scoring and Grounded Gemini AI diagnostics to rank root cause candidates.
    """
    return await service_layer.rank_root_causes(
        db,
        service_name=payload.service_name,
        incident_id=payload.incident_id,
        signals=payload.signals,
    )


@router.get(
    "/incidents/{incident_id}/analysis",
    response_model=RootCauseRankingResponse,
    summary="Get comprehensive topological root cause analysis for an incident",
)
async def get_incident_rca_analysis(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: ServiceDependencyService = Depends(get_dependency_service),
):
    """
    Loads incident context, correlates with service dependency graph, and returns ranked root causes with blast radius.
    """
    analysis = await service_layer.get_incident_analysis(db, incident_id=incident_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return analysis
