"""
CRUD operations (Repository Pattern) for MetricPoint telemetry history.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.metric import MetricPoint
from app.schemas.metric import MetricPointCreate


class CRUDMetric(CRUDBase[MetricPoint, MetricPointCreate, MetricPointCreate]):
    """Metric Repository for querying current and sliding window telemetry points."""

    async def get_current(self, db: AsyncSession) -> Optional[MetricPoint]:
        """Fetch latest single telemetry metric point."""
        stmt = select(MetricPoint).order_by(MetricPoint.timestamp.desc()).limit(1)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_history(self, db: AsyncSession, limit: int = 300) -> List[MetricPoint]:
        """Fetch last N telemetry points (default 300 points for sliding window)."""
        stmt = (
            select(MetricPoint)
            .order_by(MetricPoint.timestamp.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        items = list(res.scalars().all())
        items.reverse()  # Return in chronological order
        return items


crud_metric = CRUDMetric(MetricPoint)
