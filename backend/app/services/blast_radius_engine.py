"""
Deterministic Topological Blast Radius & Failure Propagation Engine.

Traverses the Service Dependency Graph to model failure blast radius and cascading
degradation paths across microservices, databases, queues, and cloud infrastructure.
"""

from __future__ import annotations

import uuid
from collections import deque

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service_dependency import ServiceDependency, ServiceNode
from app.schemas.dependency import BlastRadiusResponse, FailurePropagationHop

log = structlog.get_logger(__name__)


class BlastRadiusEngine:
    """Computes topological blast radius and failure propagation trees."""

    async def calculate_blast_radius(
        self,
        db: AsyncSession,
        root_service: str,
        depth: int = 5,
        organization_id: uuid.UUID | None = None,
    ) -> BlastRadiusResponse:
        """
        Calculates failure propagation and affected blast radius starting from root_service.

        Note on causal propagation:
        When a backend dependency (e.g. payment-service or postgres) degrades,
        all callers that rely on it (order-service -> checkout-service -> api-gateway)
        experience downstream cascading degradation.
        """
        cleaned_root = root_service.strip().lower()

        # 1. Fetch all dependencies for organization
        dep_stmt = select(ServiceDependency).where(
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None)
        )
        dep_res = await db.execute(dep_stmt)
        all_dependencies = list(dep_res.scalars().all())

        if not all_dependencies:
            from app.services.dependency_discovery_service import dependency_discovery_service
            await dependency_discovery_service.discover_and_synchronize(db, organization_id=organization_id)
            dep_res = await db.execute(dep_stmt)
            all_dependencies = list(dep_res.scalars().all())

        # 2. Build reverse caller adjacency map (target -> [sources that call target])
        # and forward callee adjacency map (source -> [targets called by source])
        caller_map: dict[str, list[ServiceDependency]] = {}
        callee_map: dict[str, list[ServiceDependency]] = {}

        for d in all_dependencies:
            src = d.source_service.strip().lower()
            tgt = d.target_service.strip().lower()
            caller_map.setdefault(tgt, []).append(d)
            callee_map.setdefault(src, []).append(d)

        # 3. BFS Traversal to discover all affected dependent services
        visited: set[str] = {cleaned_root}
        queue: deque[tuple[str, int, list[str]]] = deque([(cleaned_root, 0, [cleaned_root])])

        directly_affected: list[str] = []
        indirectly_affected: list[str] = []
        propagation_paths: list[list[str]] = []
        propagation_hops: list[FailurePropagationHop] = []
        max_depth_reached = 0

        while queue:
            current_svc, current_depth, current_path = queue.popleft()
            max_depth_reached = max(max_depth_reached, current_depth)

            # Look up callers that depend on current_svc
            incoming_deps = caller_map.get(current_svc, [])
            for dep in incoming_deps:
                caller_svc = dep.source_service.strip().lower()
                hop_path = current_path + [caller_svc]

                # Failure Hop Simulation
                hop = FailurePropagationHop(
                    source=current_svc,
                    target=caller_svc,
                    latency_increase_percent=round(120.0 + (current_depth * 65.0), 1),
                    error_rate=round(min(85.0, 15.0 + (current_depth * 18.5)), 1),
                    propagation_risk="CRITICAL"
                    if current_depth <= 1
                    else "HIGH"
                    if current_depth <= 3
                    else "MEDIUM",
                )
                propagation_hops.append(hop)

                if caller_svc not in visited:
                    visited.add(caller_svc)
                    if current_depth == 0:
                        directly_affected.append(caller_svc)
                    else:
                        indirectly_affected.append(caller_svc)

                    if current_depth + 1 < depth:
                        queue.append((caller_svc, current_depth + 1, hop_path))

                    propagation_paths.append(hop_path)

        # Also check downstream callees if root is an ingress/gateway
        if not directly_affected and not indirectly_affected:
            downstream_deps = callee_map.get(cleaned_root, [])
            for dep in downstream_deps:
                tgt = dep.target_service.strip().lower()
                if tgt not in visited:
                    visited.add(tgt)
                    directly_affected.append(tgt)
                    propagation_paths.append([cleaned_root, tgt])

        all_affected = list(visited)

        # 4. Fetch node attributes for affected services
        node_stmt = select(ServiceNode).where(
            func.lower(ServiceNode.name).in_(all_affected),
            (ServiceNode.organization_id == organization_id)
            if organization_id
            else ServiceNode.organization_id.is_(None),
        )
        node_res = await db.execute(node_stmt)
        nodes = node_res.scalars().all()
        node_lookup = {n.name.lower(): n for n in nodes}

        # 5. Financial & User Impact Calculation
        affected_count = len(all_affected)
        has_critical_backend = any(
            k in cleaned_root for k in ["payment", "billing", "db", "postgres", "auth"]
        )

        if affected_count >= 4 or has_critical_backend:
            user_impact = "CRITICAL"
            fin_risk = f"${(affected_count * 4500) + 12000:,} / hr"
        elif affected_count >= 2:
            user_impact = "HIGH"
            fin_risk = f"${(affected_count * 2500) + 5000:,} / hr"
        else:
            user_impact = "MEDIUM"
            fin_risk = "$3,500 / hr"

        # 6. Build Topology Graph JSON
        graph_nodes = []
        for svc_name in all_affected:
            node_obj = node_lookup.get(svc_name)
            is_root = svc_name == cleaned_root
            graph_nodes.append(
                {
                    "id": svc_name,
                    "label": svc_name,
                    "type": node_obj.type if node_obj else "service",
                    "status": "CRITICAL" if is_root else "DEGRADED",
                    "health_score": 15.0 if is_root else 55.0,
                    "is_root_cause": is_root,
                    "environment": node_obj.environment if node_obj else "production",
                }
            )

        graph_edges = []
        for dep in all_dependencies:
            src = dep.source_service.strip().lower()
            tgt = dep.target_service.strip().lower()
            if src in visited and tgt in visited:
                graph_edges.append(
                    {
                        "source": src,
                        "target": tgt,
                        "protocol": dep.protocol,
                        "type": dep.dependency_type,
                        "confidence": dep.confidence,
                        "latency_ms": dep.latency_ms,
                    }
                )

        affected_endpoints = [
            f"/api/v1/{s}" for s in all_affected if any(k in s for k in ["api", "service", "gateway"])
        ]
        affected_regions = list({n.region for n in nodes if n.region} or ["us-east-1"])

        return BlastRadiusResponse(
            root_component=cleaned_root,
            directly_affected_resources=directly_affected,
            indirectly_affected_resources=indirectly_affected,
            affected_services=all_affected,
            dependency_depth=max(1, max_depth_reached + 1),
            propagation_paths=propagation_paths,
            propagation_hops=propagation_hops[:20],
            estimated_user_impact=user_impact,
            financial_risk_estimate=fin_risk,
            affected_endpoints=affected_endpoints[:10],
            affected_regions=affected_regions,
            topology_graph={"nodes": graph_nodes, "edges": graph_edges},
        )


blast_radius_engine = BlastRadiusEngine()
