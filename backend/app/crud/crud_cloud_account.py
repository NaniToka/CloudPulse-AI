"""
Repository for Multi-Cloud Accounts (AWS, Azure, GCP).
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.cloud_account import CloudAccount


class CRUDCloudAccount(CRUDBase[CloudAccount, Any, Any]):
    """CRUD Repository for CloudAccount."""

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        provider: str | None = None,
        status: str | None = None,
    ) -> list[CloudAccount]:
        stmt = select(CloudAccount).where(CloudAccount.user_id == user_id)
        if provider and provider != "all":
            stmt = stmt.where(CloudAccount.provider == provider)
        if status and status != "all":
            stmt = stmt.where(CloudAccount.status == status)
        stmt = stmt.order_by(CloudAccount.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())


crud_cloud_account = CRUDCloudAccount(CloudAccount)
