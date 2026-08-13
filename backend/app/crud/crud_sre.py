"""
CRUD operations for ServiceObjective (SLO) model & SRE telemetry seeding.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sre import ServiceObjective


async def seed_default_slos_if_empty(db: AsyncSession, user_id: uuid.UUID | None = None) -> None:
    """Seed default Service Level Objectives (SLOs) if table is empty."""
    count_stmt = select(func.count()).select_from(ServiceObjective)
    res = await db.execute(count_stmt)
    if res.scalar_one() > 0:
        return

    now = datetime.now(UTC)
    sample_slos = [
        ("api-gateway", "API Gateway Availability 99.9%", "Maintain 99.9% uptime for external API ingress endpoints", "availability", 99.9, None, "30d"),
        ("api-gateway", "API Gateway P95 Latency < 300ms", "Ensure 95% of API requests return under 300ms", "latency", 95.0, 300.0, "30d"),
        ("auth-service", "Auth Service Availability 99.95%", "High availability target for JWT authentication & login endpoints", "availability", 99.95, None, "30d"),
        ("payment-service", "Payment Gateway Success Rate 99.9%", "Process payment transactions with < 0.1% failures", "availability", 99.9, None, "30d"),
        ("payment-service", "Payment Gateway P95 Latency < 500ms", "Checkout transaction processing response limit", "latency", 95.0, 500.0, "30d"),
        ("order-service", "Order Service Error Rate < 0.5%", "Keep order placement error rate under 0.5%", "error_rate", 0.5, None, "30d"),
        ("notification-service", "Notification Delivery Availability 99.5%", "Email and push notification webhook delivery SLO", "availability", 99.5, None, "30d"),
        ("user-service", "User Profile Read P95 Latency < 200ms", "User account query response time target", "latency", 95.0, 200.0, "30d"),
    ]

    for service, name, desc, ind_type, target, thresh, win in sample_slos:
        slo = ServiceObjective(
            id=uuid.uuid4(),
            service=service,
            name=name,
            description=desc,
            indicator_type=ind_type,
            target=target,
            target_threshold_ms=thresh,
            window=win,
            enabled=True,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        db.add(slo)

    await db.flush()


async def get_slos(
    db: AsyncSession,
    *,
    service: str | None = None,
    indicator_type: str | None = None,
    user_id: uuid.UUID | None = None,
) -> list[ServiceObjective]:
    """Fetch all configured SLOs with optional filtering."""
    await seed_default_slos_if_empty(db, user_id)
    stmt = select(ServiceObjective).where(ServiceObjective.enabled.is_(True))
    if service:
        stmt = stmt.where(ServiceObjective.service == service)
    if indicator_type:
        stmt = stmt.where(ServiceObjective.indicator_type == indicator_type)

    stmt = stmt.order_by(ServiceObjective.service.asc(), ServiceObjective.name.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_slo_by_id(
    db: AsyncSession, slo_id: uuid.UUID
) -> ServiceObjective | None:
    """Fetch a single SLO by UUID."""
    stmt = select(ServiceObjective).where(ServiceObjective.id == slo_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_slo(
    db: AsyncSession, user_id: uuid.UUID | None, data: dict[str, Any]
) -> ServiceObjective:
    """Create a new Service Objective (SLO)."""
    slo = ServiceObjective(
        id=uuid.uuid4(),
        service=data["service"],
        name=data["name"],
        description=data.get("description"),
        indicator_type=data.get("indicator_type", "availability"),
        target=float(data["target"]),
        target_threshold_ms=float(data["target_threshold_ms"]) if data.get("target_threshold_ms") is not None else None,
        window=data.get("window", "30d"),
        enabled=data.get("enabled", True),
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(slo)
    await db.flush()
    return slo


async def update_slo(
    db: AsyncSession, slo_id: uuid.UUID, data: dict[str, Any]
) -> ServiceObjective | None:
    """Update an existing Service Objective (SLO)."""
    slo = await get_slo_by_id(db, slo_id)
    if not slo:
        return None

    if "name" in data and data["name"]:
        slo.name = data["name"]
    if "description" in data:
        slo.description = data["description"]
    if "target" in data and data["target"] is not None:
        slo.target = float(data["target"])
    if "target_threshold_ms" in data:
        slo.target_threshold_ms = float(data["target_threshold_ms"]) if data["target_threshold_ms"] is not None else None
    if "window" in data and data["window"]:
        slo.window = data["window"]
    if "enabled" in data and data["enabled"] is not None:
        slo.enabled = data["enabled"]

    slo.updated_at = datetime.now(UTC)
    db.add(slo)
    await db.flush()
    return slo
