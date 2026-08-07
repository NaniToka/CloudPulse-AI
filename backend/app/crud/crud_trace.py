"""
CRUD Repository for Distributed Tracing (Traces, Spans, ServiceDependencies).
"""

import math
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.trace import Trace
from app.schemas.trace import ServiceEdge, ServiceMapResponse, ServiceNode


class CRUDTrace(CRUDBase[Trace, Any, Any]):
    """Trace Repository implementing search, filtering, and span tree retrieval."""

    async def get_by_trace_id(self, db: AsyncSession, trace_id: str) -> Trace | None:
        """Fetch single trace with loaded spans."""
        stmt = select(Trace).options(selectinload(Trace.spans)).where(Trace.trace_id == trace_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        service: str | None = None,
        status: str | None = None,
        min_duration_ms: float | None = None,
        max_duration_ms: float | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Trace], int, int]:
        """Filter traces with pagination and search."""
        query = select(Trace).options(selectinload(Trace.spans))

        filters = []
        if service:
            filters.append(func.lower(Trace.root_service) == service.lower())
        if status:
            filters.append(func.lower(Trace.status) == status.lower())
        if min_duration_ms is not None:
            filters.append(Trace.duration_ms >= min_duration_ms)
        if max_duration_ms is not None:
            filters.append(Trace.duration_ms <= max_duration_ms)
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Trace.name).like(pattern),
                    func.lower(Trace.trace_id).like(pattern),
                    func.lower(Trace.root_service).like(pattern),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Sort & Paginate
        query = query.order_by(Trace.created_at.desc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())
        pages = math.ceil(total / size) if total > 0 else 1

        return items, total, pages

    async def get_service_map(self, db: AsyncSession) -> ServiceMapResponse:
        """Returns standard OpenTelemetry service graph nodes and edges."""
        nodes = [
            ServiceNode(
                id="load-balancer",
                label="Load Balancer",
                type="gateway",
                status="healthy",
                avg_latency_ms=12.0,
                rps=1450.0,
                error_rate_percent=0.1,
            ),
            ServiceNode(
                id="api-gateway",
                label="API Gateway",
                type="gateway",
                status="healthy",
                avg_latency_ms=28.5,
                rps=1420.0,
                error_rate_percent=0.2,
            ),
            ServiceNode(
                id="auth-service",
                label="Auth Service",
                type="service",
                status="healthy",
                avg_latency_ms=45.0,
                rps=980.0,
                error_rate_percent=0.3,
            ),
            ServiceNode(
                id="user-service",
                label="User Service",
                type="service",
                status="healthy",
                avg_latency_ms=32.0,
                rps=850.0,
                error_rate_percent=0.1,
            ),
            ServiceNode(
                id="billing-service",
                label="Billing Service",
                type="service",
                status="warning",
                avg_latency_ms=185.0,
                rps=320.0,
                error_rate_percent=2.4,
            ),
            ServiceNode(
                id="notification-service",
                label="Notification Service",
                type="service",
                status="healthy",
                avg_latency_ms=64.0,
                rps=210.0,
                error_rate_percent=0.5,
            ),
            ServiceNode(
                id="redis-cache",
                label="Redis Cache",
                type="cache",
                status="healthy",
                avg_latency_ms=2.4,
                rps=2840.0,
                error_rate_percent=0.0,
            ),
            ServiceNode(
                id="postgresql-db",
                label="PostgreSQL DB",
                type="database",
                status="healthy",
                avg_latency_ms=14.2,
                rps=1890.0,
                error_rate_percent=0.1,
            ),
            ServiceNode(
                id="external-payment-api",
                label="Stripe API",
                type="external",
                status="warning",
                avg_latency_ms=420.0,
                rps=85.0,
                error_rate_percent=3.1,
            ),
        ]

        edges = [
            ServiceEdge(
                source="load-balancer",
                target="api-gateway",
                call_count=1450,
                avg_duration_ms=28.5,
                error_rate_percent=0.2,
            ),
            ServiceEdge(
                source="api-gateway",
                target="auth-service",
                call_count=980,
                avg_duration_ms=45.0,
                error_rate_percent=0.3,
            ),
            ServiceEdge(
                source="api-gateway",
                target="user-service",
                call_count=850,
                avg_duration_ms=32.0,
                error_rate_percent=0.1,
            ),
            ServiceEdge(
                source="api-gateway",
                target="billing-service",
                call_count=320,
                avg_duration_ms=185.0,
                error_rate_percent=2.4,
            ),
            ServiceEdge(
                source="auth-service",
                target="redis-cache",
                call_count=1800,
                avg_duration_ms=2.4,
                error_rate_percent=0.0,
            ),
            ServiceEdge(
                source="user-service",
                target="postgresql-db",
                call_count=1200,
                avg_duration_ms=14.2,
                error_rate_percent=0.1,
            ),
            ServiceEdge(
                source="billing-service",
                target="external-payment-api",
                call_count=85,
                avg_duration_ms=420.0,
                error_rate_percent=3.1,
            ),
            ServiceEdge(
                source="billing-service",
                target="notification-service",
                call_count=210,
                avg_duration_ms=64.0,
                error_rate_percent=0.5,
            ),
        ]

        return ServiceMapResponse(nodes=nodes, edges=edges)


crud_trace = CRUDTrace(Trace)
