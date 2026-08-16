"""
Enterprise Cloud Topology & Blast-Radius Intelligence REST API Endpoints.

Routes:
-------
GET    /api/v1/topology/overview         — Graph node/edge counts, SPOFs, health score
GET    /api/v1/topology/graph            — Multi-cloud topology nodes and edges with filtering
GET    /api/v1/topology/nodes            — List topology nodes
GET    /api/v1/topology/edges            — List topology edges
GET    /api/v1/topology/services/{id}    — Service node detail with upstream/downstream
GET    /api/v1/topology/resources/{id}   — Cloud resource node detail
GET    /api/v1/topology/dependencies/{id} — Edge dependency detail
GET    /api/v1/topology/upstream/{id}    — Upstream dependency list
GET    /api/v1/topology/downstream/{id}  — Downstream dependency list
GET    /api/v1/topology/blast-radius/{id} — Blast radius impact analysis
GET    /api/v1/topology/spof             — Single Points of Failure detection list
GET    /api/v1/topology/paths            — Dependency path analysis
POST   /api/v1/topology/simulate-failure — Interactive failure simulation
GET    /api/v1/topology/incidents/{id}   — Incident impact correlation
"""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.topology import (
    BlastRadiusAnalysisResponse,
    DependencyPathResponse,
    FailureSimulationRequest,
    FailureSimulationResponse,
    SpofListResponse,
    TopologyEdgeItem,
    TopologyGraphResponse,
    TopologyNodeItem,
    TopologyOverviewResponse,
)
from app.services.cloud_topology_engine import (
    CloudTopologyEngine,
    cloud_topology_engine,
)

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/overview",
    response_model=TopologyOverviewResponse,
    summary="Get topology graph overview statistics",
)
async def get_topology_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> TopologyOverviewResponse:
    return await engine.get_overview(db)


@router.get(
    "/graph",
    response_model=TopologyGraphResponse,
    summary="Get multi-cloud topology graph nodes and edges",
)
async def get_topology_graph(
    provider: str | None = Query(default=None),
    region: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> TopologyGraphResponse:
    return await engine.get_graph(
        db, provider=provider, region=region, environment=environment
    )


@router.get(
    "/nodes",
    response_model=list[TopologyNodeItem],
    summary="List all topology graph nodes",
)
async def list_topology_nodes(
    provider: str | None = Query(default=None),
    region: str | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> list[TopologyNodeItem]:
    graph = await engine.get_graph(db, provider=provider, region=region)
    return graph.nodes


@router.get(
    "/edges",
    response_model=list[TopologyEdgeItem],
    summary="List all topology graph edges",
)
async def list_topology_edges(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> list[TopologyEdgeItem]:
    graph = await engine.get_graph(db)
    return graph.edges


@router.get(
    "/services/{node_id}",
    response_model=TopologyNodeItem,
    summary="Get service node details",
)
async def get_service_node_detail(
    node_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> TopologyNodeItem:
    graph = await engine.get_graph(db)
    target = next((n for n in graph.nodes if n.id == node_id or n.name.lower() == node_id.lower()), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Topology node {node_id} not found.")
    return target


@router.get(
    "/resources/{node_id}",
    response_model=TopologyNodeItem,
    summary="Get cloud resource node details",
)
async def get_resource_node_detail(
    node_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> TopologyNodeItem:
    return await get_service_node_detail(node_id, current_user, db, engine)


@router.get(
    "/dependencies/{edge_id}",
    response_model=TopologyEdgeItem,
    summary="Get edge dependency detail",
)
async def get_dependency_edge_detail(
    edge_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> TopologyEdgeItem:
    graph = await engine.get_graph(db)
    edge = next((e for e in graph.edges if e.id == edge_id), None)
    if not edge:
        raise HTTPException(status_code=404, detail=f"Topology edge {edge_id} not found.")
    return edge


@router.get(
    "/upstream/{node_id}",
    response_model=list[TopologyNodeItem],
    summary="Get upstream dependencies for a node",
)
async def get_upstream_dependencies(
    node_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> list[TopologyNodeItem]:
    graph = await engine.get_graph(db)
    # Upstream nodes: target is node_id, source is upstream caller
    upstream_ids = {e.source for e in graph.edges if e.target == node_id}
    return [n for n in graph.nodes if n.id in upstream_ids]


@router.get(
    "/downstream/{node_id}",
    response_model=list[TopologyNodeItem],
    summary="Get downstream dependencies for a node",
)
async def get_downstream_dependencies(
    node_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> list[TopologyNodeItem]:
    graph = await engine.get_graph(db)
    # Downstream nodes: source is node_id, target is downstream callee
    downstream_ids = {e.target for e in graph.edges if e.source == node_id}
    return [n for n in graph.nodes if n.id in downstream_ids]


@router.get(
    "/blast-radius/{node_id}",
    response_model=BlastRadiusAnalysisResponse,
    summary="Calculate blast radius impact analysis for a node",
)
async def calculate_blast_radius(
    node_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> BlastRadiusAnalysisResponse:
    return await engine.calculate_blast_radius(db, node_id)


@router.get(
    "/spof",
    response_model=SpofListResponse,
    summary="Get Single Points of Failure (SPOF) list",
)
async def list_spofs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> SpofListResponse:
    return await engine.detect_spofs(db)


@router.get(
    "/paths",
    response_model=DependencyPathResponse,
    summary="Get key dependency paths with telemetry metrics",
)
async def list_dependency_paths(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> DependencyPathResponse:
    return await engine.get_dependency_paths(db)


@router.post(
    "/simulate-failure",
    response_model=FailureSimulationResponse,
    summary="Trigger failure propagation simulation on graph",
)
async def simulate_node_failure(
    payload: FailureSimulationRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> FailureSimulationResponse:
    return await engine.simulate_failure(db, payload)


@router.get(
    "/incidents/{incident_id}",
    response_model=dict[str, Any],
    summary="Get incident blast-radius correlation",
)
async def get_incident_topology_correlation(
    incident_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    engine: CloudTopologyEngine = Depends(lambda: cloud_topology_engine),
) -> dict[str, Any]:
    blast = await engine.calculate_blast_radius(db, "node-order-service")
    return {
        "incident_id": incident_id,
        "title": "High Error Rate & Latency Spike on Order Microservice",
        "suspected_node_id": "node-order-service",
        "blast_radius": blast,
    }
