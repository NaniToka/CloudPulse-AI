"""
CRUD Repository for ServiceNode and ServiceDependency Graph entities.
"""

from __future__ import annotations

import math
import uuid
from collections import deque

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.schemas.dependency import (
    ServiceDependencyCreate,
    ServiceDependencyUpdate,
    ServiceNodeCreate,
    ServiceNodeUpdate,
)


class CRUDServiceDependency(CRUDBase[ServiceDependency, ServiceDependencyCreate, ServiceDependencyUpdate]):
    """Repository for ServiceDependency relations."""

    async def get_by_source_target(
        self,
        db: AsyncSession,
        source: str,
        target: str,
        organization_id: uuid.UUID | None = None,
    ) -> ServiceDependency | None:
        stmt = select(ServiceDependency).where(
            func.lower(ServiceDependency.source_service) == source.strip().lower(),
            func.lower(ServiceDependency.target_service) == target.strip().lower(),
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None),
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_upstream_dependencies(
        self, db: AsyncSession, service_name: str, organization_id: uuid.UUID | None = None
    ) -> list[ServiceDependency]:
        """Dependencies called by this service (outbound)."""
        stmt = select(ServiceDependency).where(
            func.lower(ServiceDependency.source_service) == service_name.strip().lower(),
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None),
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_downstream_dependents(
        self, db: AsyncSession, service_name: str, organization_id: uuid.UUID | None = None
    ) -> list[ServiceDependency]:
        """Services that call this service (inbound callers)."""
        stmt = select(ServiceDependency).where(
            func.lower(ServiceDependency.target_service) == service_name.strip().lower(),
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None),
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


class CRUDServiceNode(CRUDBase[ServiceNode, ServiceNodeCreate, ServiceNodeUpdate]):
    """Repository for ServiceNode entities and Graph queries."""

    async def get_by_name(
        self, db: AsyncSession, name: str, organization_id: uuid.UUID | None = None
    ) -> ServiceNode | None:
        stmt = select(ServiceNode).where(
            func.lower(ServiceNode.name) == name.strip().lower(),
            (ServiceNode.organization_id == organization_id)
            if organization_id
            else ServiceNode.organization_id.is_(None),
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_filtered(
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
    ) -> tuple[list[ServiceNode], int, int]:
        filters = []
        if organization_id:
            filters.append(
                or_(ServiceNode.organization_id == organization_id, ServiceNode.organization_id.is_(None))
            )
        if environment:
            filters.append(func.lower(ServiceNode.environment) == environment.strip().lower())
        if region:
            filters.append(func.lower(ServiceNode.region) == region.strip().lower())
        if status:
            filters.append(func.lower(ServiceNode.status) == status.strip().lower())
        if search:
            s_pat = f"%{search.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(ServiceNode.name).like(s_pat),
                    func.lower(ServiceNode.type).like(s_pat),
                )
            )

        count_stmt = select(func.count(ServiceNode.id)).where(and_(*filters) if filters else True)
        count_res = await db.execute(count_stmt)
        total = count_res.scalar() or 0

        sort_col = getattr(ServiceNode, sort_by, ServiceNode.name)
        order_clause = sort_col.desc() if sort_dir.lower() == "desc" else sort_col.asc()

        offset = (page - 1) * size
        stmt = (
            select(ServiceNode)
            .where(and_(*filters) if filters else True)
            .order_by(order_clause)
            .offset(offset)
            .limit(size)
        )
        res = await db.execute(stmt)
        items = list(res.scalars().all())
        pages = math.ceil(total / size) if size > 0 else 1

        return items, total, pages

    async def get_graph(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        environment: str | None = None,
        region: str | None = None,
        root_service: str | None = None,
        depth: int = 5,
    ) -> tuple[list[ServiceNode], list[ServiceDependency], list[str], int]:
        """
        Retrieves topology graph nodes and edges with optional depth-limited BFS traversal.
        """
        # Fetch all edges for tenant
        dep_filters = []
        if organization_id:
            dep_filters.append(
                or_(ServiceDependency.organization_id == organization_id, ServiceDependency.organization_id.is_(None))
            )
        edge_stmt = select(ServiceDependency).where(and_(*dep_filters) if dep_filters else True)
        edge_res = await db.execute(edge_stmt)
        all_edges = list(edge_res.scalars().all())

        # If root_service specified, execute depth-limited BFS
        if root_service:
            cleaned_root = root_service.strip().lower()
            adj_map: dict[str, list[str]] = {}
            for e in all_edges:
                src = e.source_service.strip().lower()
                tgt = e.target_service.strip().lower()
                adj_map.setdefault(src, []).append(tgt)
                adj_map.setdefault(tgt, []).append(src)

            visited: set[str] = {cleaned_root}
            queue: deque[tuple[str, int]] = deque([(cleaned_root, 0)])

            while queue:
                curr, curr_depth = queue.popleft()
                if curr_depth < depth:
                    for neighbor in adj_map.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, curr_depth + 1))

            filtered_edges = [
                e
                for e in all_edges
                if e.source_service.strip().lower() in visited and e.target_service.strip().lower() in visited
            ]
            node_names = list(visited)
        else:
            filtered_edges = all_edges
            node_names = list(
                {e.source_service.strip().lower() for e in all_edges}
                | {e.target_service.strip().lower() for e in all_edges}
            )

        # Fetch nodes
        node_filters = [func.lower(ServiceNode.name).in_(node_names)] if node_names else []
        if organization_id:
            node_filters.append(
                or_(ServiceNode.organization_id == organization_id, ServiceNode.organization_id.is_(None))
            )
        if environment:
            node_filters.append(func.lower(ServiceNode.environment) == environment.strip().lower())
        if region:
            node_filters.append(func.lower(ServiceNode.region) == region.strip().lower())

        node_stmt = select(ServiceNode).where(and_(*node_filters) if node_filters else True)
        node_res = await db.execute(node_stmt)
        nodes = list(node_res.scalars().all())

        # Critical path calculation (nodes with lowest health or highest latency)
        unhealthy_count = sum(1 for n in nodes if n.status in ["DEGRADED", "CRITICAL"])
        critical_path = [n.name for n in sorted(nodes, key=lambda n: n.health_score)[:4]]

        return nodes, filtered_edges, critical_path, unhealthy_count


crud_service_node = CRUDServiceNode(ServiceNode)
crud_service_dependency = CRUDServiceDependency(ServiceDependency)
