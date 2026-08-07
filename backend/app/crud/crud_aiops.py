"""
CRUD Repository for AIOps Agent, Recommendations, & Executions.
"""

import math
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.aiops import AgentRecommendation, AIOpsAgent


class CRUDAIOps(CRUDBase[AIOpsAgent, Any, Any]):
    """AIOps Repository implementing search, filtering, and approval state management."""

    async def get_active_agent(self, db: AsyncSession) -> AIOpsAgent | None:
        """Fetch active agent or load with tasks."""
        stmt = (
            select(AIOpsAgent)
            .options(
                selectinload(AIOpsAgent.tasks),
                selectinload(AIOpsAgent.recommendations),
            )
            .order_by(AIOpsAgent.created_at.desc())
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    async def get_filtered_recommendations(
        self,
        db: AsyncSession,
        *,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[AgentRecommendation], int, int]:
        """Filter agent recommendations with pagination and search."""
        query = select(AgentRecommendation).options(selectinload(AgentRecommendation.executions))

        filters = []
        if category and category.upper() != "ALL":
            filters.append(func.lower(AgentRecommendation.category) == category.lower())
        if priority and priority.upper() != "ALL":
            filters.append(func.upper(AgentRecommendation.priority) == priority.upper())
        if status and status.upper() != "ALL":
            filters.append(func.lower(AgentRecommendation.status) == status.lower())

        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(AgentRecommendation.title).like(pattern),
                    func.lower(AgentRecommendation.executive_summary).like(pattern),
                    func.lower(AgentRecommendation.root_cause).like(pattern),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Sort & Paginate
        query = query.order_by(AgentRecommendation.created_at.desc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())
        pages = math.ceil(total / size) if total > 0 else 1

        return items, total, pages


crud_aiops = CRUDAIOps(AIOpsAgent)
