"""
Repository for Monitoring Alerts.
"""

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.alert import Alert


class CRUDAlert(CRUDBase[Alert, Any, Any]):
    """Alert Repository for active and historical monitoring alerts."""

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        severity: str | None = None,
        search: str | None = None,
    ) -> list[Alert]:
        stmt = select(Alert)
        if status and status != "all":
            stmt = stmt.where(Alert.status == status)
        if severity and severity != "all":
            stmt = stmt.where(Alert.severity == severity)
        if search:
            stmt = stmt.where(
                or_(
                    Alert.title.ilike(f"%{search}%"),
                    Alert.message.ilike(f"%{search}%"),
                    Alert.metric_name.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def bulk_acknowledge(self, db: AsyncSession) -> int:
        stmt = select(Alert).where(Alert.status == "active")
        res = await db.execute(stmt)
        active_alerts = list(res.scalars().all())
        for a in active_alerts:
            a.status = "acknowledged"
        await db.commit()
        return len(active_alerts)


crud_alert = CRUDAlert(Alert)
