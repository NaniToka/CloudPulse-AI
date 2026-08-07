"""
Repository for Servers & Infrastructure Monitoring.
"""

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.infrastructure import Server


class CRUDServer(CRUDBase[Server, Any, Any]):
    """Server Repository managing monitored infrastructure nodes."""

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        provider: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[Server]:
        stmt = select(Server).where(Server.user_id == user_id)
        if provider and provider != "all":
            stmt = stmt.where(Server.provider == provider)
        if status and status != "all":
            stmt = stmt.where(Server.status == status)
        if search:
            stmt = stmt.where(
                or_(
                    Server.name.ilike(f"%{search}%"),
                    Server.hostname.ilike(f"%{search}%"),
                    Server.ip_address.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(Server.created_at.desc()).offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_name(self, db: AsyncSession, name: str) -> Server | None:
        stmt = select(Server).where(Server.name == name)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


crud_server = CRUDServer(Server)
