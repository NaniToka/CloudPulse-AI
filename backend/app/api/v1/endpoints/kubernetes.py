"""
Kubernetes & Container Intelligence REST API Endpoints.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.kubernetes_schemas import (
    K8sAnalysisResponse,
    K8sClusterResponse,
    K8sDeploymentResponse,
    K8sEventResponse,
    K8sNodeResponse,
    K8sPodResponse,
)
from app.services.kubernetes_service import KubernetesService, kubernetes_service

router = APIRouter()


@router.get(
    "/clusters", response_model=list[K8sClusterResponse], summary="List Kubernetes Clusters"
)
async def list_clusters(
    provider: str | None = Query(
        None, description="Filter by provider (GKE, EKS, AKS, Self-Hosted)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve monitored Kubernetes clusters."""
    clusters = await service.get_clusters(db, user_id=current_user.id, provider=provider)
    return [K8sClusterResponse.model_validate(c) for c in clusters]


@router.get("/nodes", response_model=list[K8sNodeResponse], summary="List Cluster Nodes")
async def list_nodes(
    cluster_id: uuid.UUID | None = Query(None, description="Filter by cluster ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve nodes with CPU and memory utilization metrics."""
    nodes = await service.get_nodes(db, cluster_id=cluster_id)
    return [K8sNodeResponse.model_validate(n) for n in nodes]


@router.get("/pods", response_model=list[K8sPodResponse], summary="List Pod Telemetry")
async def list_pods(
    cluster_id: uuid.UUID | None = Query(None, description="Filter by cluster ID"),
    namespace: str | None = Query(None, description="Filter by namespace"),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status (Running, CrashLoopBackOff, OOMKilled, Pending)",
    ),
    search: str | None = Query(None, description="Search pod name or deployment"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve Kubernetes Pods with status, restart counts, and resource usage."""
    pods = await service.get_pods(
        db, cluster_id=cluster_id, namespace=namespace, status=status_filter, search=search
    )
    return [K8sPodResponse.model_validate(p) for p in pods]


@router.get("/deployments", response_model=list[K8sDeploymentResponse], summary="List Deployments")
async def list_deployments(
    cluster_id: uuid.UUID | None = Query(None, description="Filter by cluster ID"),
    namespace: str | None = Query(None, description="Filter by namespace"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve Kubernetes Deployments and replica rollout status."""
    deployments = await service.get_deployments(db, cluster_id=cluster_id, namespace=namespace)
    return [K8sDeploymentResponse.model_validate(d) for d in deployments]


@router.get("/events", response_model=list[K8sEventResponse], summary="List Cluster Events")
async def list_events(
    event_type: str | None = Query(None, description="Filter event type (Normal, Warning)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve Kubernetes warning and normal cluster events."""
    events = await service.get_events(db, event_type=event_type)
    return [K8sEventResponse.model_validate(e) for e in events]


@router.get("/logs/{pod_name}", summary="Stream Container Logs")
async def get_pod_logs(
    pod_name: str,
    tail: int = Query(100, description="Number of lines to tail"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Retrieve stdout/stderr container logs for a pod."""
    logs = await service.get_pod_logs(db, pod_name, tail=tail)
    return {"pod_name": pod_name, "logs": logs}


@router.post(
    "/analyze", response_model=K8sAnalysisResponse, summary="Trigger Gemini AI Cluster Analysis"
)
async def analyze_cluster(
    cluster_id: uuid.UUID | None = Query(None, description="Optional cluster ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: KubernetesService = Depends(lambda: kubernetes_service),
):
    """Diagnose pod failures, OOMKilled events, and cluster capacity using Gemini AI."""
    return await service.analyze_cluster(db, cluster_id=cluster_id)
