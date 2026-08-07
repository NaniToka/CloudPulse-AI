"""
Repository for User Notifications.
"""

import uuid
from typing import List, Optional, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.notification import Notification


class CRUDNotification(CRUDBase[Notification, Any, Any]):
    """Notification Repository managing user alert digests & system messages."""

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        unread_only: bool = False,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        if category and category != "all":
            stmt = stmt.where(Notification.category == category)
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def mark_all_read(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        stmt = select(Notification).where(
            Notification.user_id == user_id, Notification.is_read == False
        )
        res = await db.execute(stmt)
        unread = list(res.scalars().all())
        for n in unread:
            n.is_read = True
        await db.commit()
        return len(unread)


crud_notification = CRUDNotification(Notification)
