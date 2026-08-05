"""
CRUD Repository for Auto Remediation Runbooks & Execution Steps.
"""

import math
import uuid
from typing import List, Optional, Tuple, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.runbook import Runbook, AutomationStep, RunbookExecution


class CRUDRunbook(CRUDBase[Runbook, Any, Any]):
    """Runbook Repository implementing search, filtering, and execution tracking."""

    async def get_by_id_with_steps(self, db: AsyncSession, runbook_id: uuid.UUID) -> Optional[Runbook]:
        """Fetch single runbook with loaded steps and execution logs."""
        stmt = (
            select(Runbook)
            .options(
                selectinload(Runbook.steps),
                selectinload(Runbook.executions),
            )
            .where(Runbook.id == runbook_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        service: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> Tuple[List[Runbook], int, int]:
        """Filter runbooks with pagination and search."""
        query = select(Runbook).options(
            selectinload(Runbook.steps),
            selectinload(Runbook.executions),
        )

        filters = []
        if service:
            filters.append(func.lower(Runbook.service_name) == service.lower())
        if severity:
            filters.append(func.upper(Runbook.severity) == severity.upper())
        if status:
            filters.append(func.lower(Runbook.status) == status.lower())
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Runbook.title).like(pattern),
                    func.lower(Runbook.service_name).like(pattern),
                    func.lower(Runbook.root_cause).like(pattern),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Sort & Paginate
        query = query.order_by(Runbook.created_at.desc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())
        pages = math.ceil(total / size) if total > 0 else 1

        return items, total, pages


crud_runbook = CRUDRunbook(Runbook)
