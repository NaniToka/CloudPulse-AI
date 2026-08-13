"""
CRUD Operations for Enterprise SLO, SLA & Error Budget Intelligence Center.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sre import ServiceObjective
from app.schemas.slo import SloObjectiveCreate, SloObjectiveUpdate


async def get_objectives(
    db: AsyncSession, *, service: str | None = None, limit: int = 100
) -> list[ServiceObjective]:
    stmt = select(ServiceObjective).order_by(ServiceObjective.created_at.desc()).limit(limit)
    if service:
        stmt = stmt.where(ServiceObjective.service == service)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_objective_by_id(db: AsyncSession, obj_id: uuid.UUID) -> ServiceObjective | None:
    stmt = select(ServiceObjective).where(ServiceObjective.id == obj_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_objective(
    db: AsyncSession, *, obj_in: SloObjectiveCreate, user_id: uuid.UUID | None = None
) -> ServiceObjective:
    objective = ServiceObjective(
        user_id=user_id,
        service=obj_in.service,
        name=obj_in.name,
        description=obj_in.description,
        indicator_type=obj_in.indicator_type,
        target=obj_in.target,
        target_threshold_ms=obj_in.target_threshold_ms,
        window=obj_in.window,
        enabled=obj_in.enabled,
    )
    db.add(objective)
    await db.commit()
    await db.refresh(objective)
    return objective


async def update_objective(
    db: AsyncSession, *, objective: ServiceObjective, obj_in: SloObjectiveUpdate
) -> ServiceObjective:
    if obj_in.name is not None:
        objective.name = obj_in.name
    if obj_in.description is not None:
        objective.description = obj_in.description
    if obj_in.target is not None:
        objective.target = obj_in.target
    if obj_in.target_threshold_ms is not None:
        objective.target_threshold_ms = obj_in.target_threshold_ms
    if obj_in.window is not None:
        objective.window = obj_in.window
    if obj_in.enabled is not None:
        objective.enabled = obj_in.enabled

    await db.commit()
    await db.refresh(objective)
    return objective


async def delete_objective(db: AsyncSession, objective: ServiceObjective) -> None:
    await db.delete(objective)
    await db.commit()
