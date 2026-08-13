"""
CRUD helper for persisting snapshots and insight records.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.command_center import ExecutiveCommandSnapshot


async def get_latest_snapshot(
    db: AsyncSession, user_id: uuid.UUID | None = None
) -> ExecutiveCommandSnapshot | None:
    stmt = (
        select(ExecutiveCommandSnapshot)
        .order_by(ExecutiveCommandSnapshot.created_at.desc())
        .limit(1)
    )
    if user_id:
        stmt = stmt.where(ExecutiveCommandSnapshot.user_id == user_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_snapshot(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None = None,
    health_score: float,
    health_status: str,
    risk_score: float,
    risk_level: str,
    active_incidents_count: int,
    slo_compliance_pct: float,
    security_risk_score: float,
    monthly_spend: float,
    potential_savings: float,
    executive_brief: str,
    is_ai_powered: bool = False,
    metadata_json: dict[str, Any] | None = None,
) -> ExecutiveCommandSnapshot:
    snapshot = ExecutiveCommandSnapshot(
        user_id=user_id,
        platform_health_score=health_score,
        health_status=health_status,
        operational_risk_score=risk_score,
        risk_level=risk_level,
        active_incidents_count=active_incidents_count,
        slo_compliance_pct=slo_compliance_pct,
        security_risk_score=security_risk_score,
        monthly_spend=monthly_spend,
        potential_savings=potential_savings,
        executive_brief=executive_brief,
        is_ai_powered=is_ai_powered,
        snapshot_metadata=metadata_json,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot
