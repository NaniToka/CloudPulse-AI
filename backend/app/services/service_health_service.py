"""
Service Health Scoring & Status Evaluation Engine.

Computes mathematical health scores (0 - 100) and lifecycle states
(HEALTHY, DEGRADED, CRITICAL, UNKNOWN) from real telemetry metrics,
active incidents, error rates, and dependency topology health.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.incident import Incident
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.schemas.dependency import ServiceHealthResponse

log = structlog.get_logger(__name__)


class ServiceHealthService:
    """Evaluates and updates service health based on multi-dimensional telemetry."""

    async def evaluate_service_health(
        self,
        db: AsyncSession,
        service_name: str,
        organization_id: uuid.UUID | None = None,
    ) -> ServiceHealthResponse:
        """
        Calculates real-time health score (0 - 100) and status for a service.
        """
        cleaned_name = service_name.strip().lower()
        now = datetime.now(UTC)
        factors: list[str] = []

        # 1. Fetch Node if exists
        node_stmt = select(ServiceNode).where(
            func.lower(ServiceNode.name) == cleaned_name,
            (ServiceNode.organization_id == organization_id)
            if organization_id
            else ServiceNode.organization_id.is_(None),
        )
        node_res = await db.execute(node_stmt)
        node = node_res.scalar_one_or_none()

        # 2. Fetch Active Incidents affecting this service
        inc_stmt = select(Incident).where(
            func.lower(Incident.status).notin_(["resolved", "closed"]),
            func.lower(Incident.affected_service) == cleaned_name,
            (Incident.organization_id == organization_id)
            if organization_id
            else Incident.organization_id.is_(None),
        )
        inc_res = await db.execute(inc_stmt)
        active_incidents = inc_res.scalars().all()

        incident_penalty = 0.0
        for inc in active_incidents:
            sev_u = (inc.severity or "HIGH").upper()
            if sev_u in ["CRITICAL", "P0"]:
                incident_penalty += 35.0
                factors.append(f"Active CRITICAL incident: {inc.title}")
            elif sev_u in ["HIGH", "P1"]:
                incident_penalty += 20.0
                factors.append(f"Active HIGH incident: {inc.title}")
            elif sev_u in ["MEDIUM", "P2"]:
                incident_penalty += 10.0
                factors.append(f"Active MEDIUM incident: {inc.title}")
            else:
                incident_penalty += 5.0

        incident_penalty = min(60.0, incident_penalty)

        # 3. Fetch Outbound Dependencies to check downstream health penalties
        dep_stmt = select(ServiceDependency).where(
            func.lower(ServiceDependency.source_service) == cleaned_name,
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None),
        )
        dep_res = await db.execute(dep_stmt)
        dependencies = dep_res.scalars().all()

        error_rate = node.error_rate if node else 0.0
        latency_p99 = node.latency_p99_ms if node else 45.0
        dep_penalty = 0.0

        if dependencies:
            dep_errors = [d.error_rate for d in dependencies if d.error_rate > 0]
            if dep_errors:
                max_dep_error = max(dep_errors)
                error_rate = max(error_rate, max_dep_error)
                dep_penalty = min(25.0, max_dep_error * 0.4)
                factors.append(f"Downstream dependency error rate: {max_dep_error}%")

            dep_latencies = [d.latency_ms for d in dependencies if d.latency_ms > 0]
            if dep_latencies:
                latency_p99 = max(latency_p99, max(dep_latencies))

        # Latency Penalty
        latency_penalty = 0.0
        if latency_p99 > 1500.0:
            latency_penalty = 25.0
            factors.append(f"Severe P99 latency degradation: {latency_p99:.1f}ms")
        elif latency_p99 > 500.0:
            latency_penalty = 15.0
            factors.append(f"Elevated P99 response time: {latency_p99:.1f}ms")

        # Error Rate Penalty
        error_penalty = min(40.0, error_rate * 1.2)
        if error_rate > 5.0:
            factors.append(f"Service error rate elevated at {error_rate:.1f}%")

        # Calculate final Health Score (0 - 100)
        total_penalties = incident_penalty + error_penalty + latency_penalty + dep_penalty
        health_score = max(0.0, min(100.0, 100.0 - total_penalties))

        # Derive Status
        if health_score >= 85.0:
            status = "HEALTHY"
        elif health_score >= 50.0:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        if not factors:
            factors.append("All core metrics operating within nominal baseline parameters.")

        # Update Node in DB if present
        if node:
            node.health_score = round(health_score, 1)
            node.status = status
            node.error_rate = round(error_rate, 1)
            node.latency_p99_ms = round(latency_p99, 1)
            node.active_incidents_count = len(active_incidents)
            node.updated_at = now
            await db.commit()

        return ServiceHealthResponse(
            service_id=node.id if node else None,
            service_name=cleaned_name,
            health_score=round(health_score, 1),
            status=status,
            error_rate=round(error_rate, 1),
            latency_p99_ms=round(latency_p99, 1),
            active_incidents_count=len(active_incidents),
            dependency_health_penalty=round(dep_penalty, 1),
            factors=factors,
            evaluated_at=now,
        )

    async def update_all_service_health(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> list[ServiceHealthResponse]:
        """Evaluates and updates health for all known service nodes in the organization."""
        node_stmt = select(ServiceNode).where(
            (ServiceNode.organization_id == organization_id)
            if organization_id
            else ServiceNode.organization_id.is_(None)
        )
        res = await db.execute(node_stmt)
        nodes = res.scalars().all()

        results: list[ServiceHealthResponse] = []
        for n in nodes:
            h = await self.evaluate_service_health(db, n.name, organization_id=organization_id)
            results.append(h)

        return results


service_health_service = ServiceHealthService()
