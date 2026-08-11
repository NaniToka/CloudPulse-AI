"""
Enterprise Service Orchestrator for Service Dependency & Root-Cause Intelligence.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_dependency import crud_service_dependency, crud_service_node
from app.models.incident import Incident
from app.models.service_dependency import ServiceDependency
from app.schemas.dependency import (
    BlastRadiusResponse,
    DependencyDiscoveryResponse,
    DependencyGraphResponse,
    RootCauseRankingResponse,
    ServiceDependencyResponse,
    ServiceHealthResponse,
    ServiceListResponse,
    ServiceNodeDetailResponse,
    ServiceNodeResponse,
)
from app.services.blast_radius_engine import blast_radius_engine
from app.services.dependency_discovery_service import dependency_discovery_service
from app.services.root_cause_intelligence_service import root_cause_intelligence_service
from app.services.service_health_service import service_health_service

log = structlog.get_logger(__name__)


class ServiceDependencyService:
    """Unified coordinator for dependency discovery, graph queries, health, and RCA."""

    async def seed_initial_topology_if_empty(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> None:
        """Seeds standard enterprise production topology if no dependencies exist."""
        edge_stmt = select(func.count(ServiceDependency.id)).where(
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None)
        )
        edge_res = await db.execute(edge_stmt)
        total_edges = edge_res.scalar() or 0
        if total_edges == 0:
            log.info("seeding_initial_dependency_topology")
            await dependency_discovery_service.discover_and_synchronize(
                db, organization_id=organization_id
            )

    async def get_graph(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        environment: str | None = None,
        region: str | None = None,
        service: str | None = None,
        depth: int = 5,
    ) -> DependencyGraphResponse:
        """Retrieves topology graph nodes and edges."""
        await self.seed_initial_topology_if_empty(db, organization_id)

        nodes, edges, critical_path, unhealthy_count = await crud_service_node.get_graph(
            db,
            organization_id=organization_id,
            environment=environment,
            region=region,
            root_service=service,
            depth=depth,
        )

        return DependencyGraphResponse(
            nodes=[ServiceNodeResponse.model_validate(n) for n in nodes],
            edges=[ServiceDependencyResponse.model_validate(e) for e in edges],
            total_nodes=len(nodes),
            total_edges=len(edges),
            critical_path=critical_path,
            unhealthy_services_count=unhealthy_count,
            generated_at=datetime.now(UTC),
        )

    async def list_services(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        environment: str | None = None,
        region: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort_by: str = "name",
        sort_dir: str = "asc",
        page: int = 1,
        size: int = 20,
    ) -> ServiceListResponse:
        """Lists paginated service nodes."""
        await self.seed_initial_topology_if_empty(db, organization_id)

        items, total, pages = await crud_service_node.get_filtered(
            db,
            organization_id=organization_id,
            environment=environment,
            region=region,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            size=size,
        )

        return ServiceListResponse(
            items=[ServiceNodeResponse.model_validate(n) for n in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    async def get_service_detail(
        self,
        db: AsyncSession,
        service_id: uuid.UUID | str,
        organization_id: uuid.UUID | None = None,
    ) -> ServiceNodeDetailResponse | None:
        """Retrieves detailed service node attributes, upstream dependencies, and downstream callers."""
        await self.seed_initial_topology_if_empty(db, organization_id)

        # Allow lookup by UUID or by service name string
        if isinstance(service_id, uuid.UUID):
            node = await crud_service_node.get(db, id=service_id)
        else:
            try:
                parsed_uuid = uuid.UUID(str(service_id))
                node = await crud_service_node.get(db, id=parsed_uuid)
            except ValueError:
                node = await crud_service_node.get_by_name(db, name=str(service_id), organization_id=organization_id)

        if not node:
            return None

        upstream = await crud_service_dependency.get_upstream_dependencies(
            db, service_name=node.name, organization_id=organization_id
        )
        downstream = await crud_service_dependency.get_downstream_dependents(
            db, service_name=node.name, organization_id=organization_id
        )

        # Fetch recent active incidents for this service
        inc_stmt = select(Incident).where(
            func.lower(Incident.affected_service) == node.name.lower(),
            (Incident.organization_id == organization_id)
            if organization_id
            else Incident.organization_id.is_(None),
        ).limit(5)
        inc_res = await db.execute(inc_stmt)
        incidents = inc_res.scalars().all()

        recent_incs = [
            {
                "id": str(i.id),
                "title": i.title,
                "severity": str(i.severity),
                "status": str(i.status),
                "started_at": i.started_at.isoformat() if i.started_at else None,
            }
            for i in incidents
        ]

        return ServiceNodeDetailResponse(
            id=node.id,
            organization_id=node.organization_id,
            name=node.name,
            type=node.type,
            environment=node.environment,
            region=node.region,
            status=node.status,
            health_score=node.health_score,
            error_rate=node.error_rate,
            latency_p99_ms=node.latency_p99_ms,
            request_rate=node.request_rate,
            active_incidents_count=node.active_incidents_count,
            metadata_json=node.metadata_json or {},
            created_at=node.created_at,
            updated_at=node.updated_at,
            upstream_dependencies=[ServiceDependencyResponse.model_validate(u) for u in upstream],
            downstream_dependents=[ServiceDependencyResponse.model_validate(d) for d in downstream],
            recent_incidents=recent_incs,
            recent_alerts=[],
        )

    async def get_service_health(
        self,
        db: AsyncSession,
        service_id: uuid.UUID | str,
        organization_id: uuid.UUID | None = None,
    ) -> ServiceHealthResponse | None:
        """Evaluates live calculated health for a service."""
        detail = await self.get_service_detail(db, service_id, organization_id)
        if not detail:
            return None

        return await service_health_service.evaluate_service_health(
            db, detail.name, organization_id=organization_id
        )

    async def discover(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID | None = None,
        time_window_minutes: int = 60,
        include_traces: bool = True,
        include_logs: bool = True,
        include_k8s: bool = True,
        include_cloud: bool = True,
    ) -> DependencyDiscoveryResponse:
        """Discovers and synchronizes dependencies across multi-modal telemetry."""
        return await dependency_discovery_service.discover_and_synchronize(
            db,
            organization_id=organization_id,
            time_window_minutes=time_window_minutes,
            include_traces=include_traces,
            include_logs=include_logs,
            include_k8s=include_k8s,
            include_cloud=include_cloud,
        )

    async def calculate_blast_radius(
        self,
        db: AsyncSession,
        service_name: str,
        depth: int = 5,
        organization_id: uuid.UUID | None = None,
    ) -> BlastRadiusResponse:
        """Calculates topological blast radius for a service failure."""
        await self.seed_initial_topology_if_empty(db, organization_id)
        return await blast_radius_engine.calculate_blast_radius(
            db, root_service=service_name, depth=depth, organization_id=organization_id
        )

    async def rank_root_causes(
        self,
        db: AsyncSession,
        service_name: str | None = None,
        incident_id: uuid.UUID | None = None,
        signals: list[dict[str, Any]] | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> RootCauseRankingResponse:
        """Ranks root cause candidates for an incident or service degradation."""
        await self.seed_initial_topology_if_empty(db, organization_id)
        return await root_cause_intelligence_service.rank_root_causes(
            db,
            service_name=service_name,
            incident_id=incident_id,
            signals=signals,
            organization_id=organization_id,
        )

    async def get_incident_analysis(
        self,
        db: AsyncSession,
        incident_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> RootCauseRankingResponse | None:
        """Retrieves comprehensive topological root cause analysis for an incident."""
        inc_stmt = select(Incident).where(Incident.id == incident_id)
        inc_res = await db.execute(inc_stmt)
        incident = inc_res.scalar_one_or_none()
        if not incident:
            return None

        return await self.rank_root_causes(
            db,
            service_name=incident.affected_service,
            incident_id=incident.id,
            signals=incident.evidence,
            organization_id=organization_id,
        )


service_dependency_service = ServiceDependencyService()
