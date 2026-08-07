"""
User Notification Service with auto-seeding.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.crud.crud_notification import crud_notification
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

log = structlog.get_logger(__name__)

DEFAULT_NOTIFICATIONS = [
    {
        "title": "Critical Incident INC-1042 Created",
        "message": "API Gateway elevated 5xx errors in us-east-1.",
        "type": "error",
        "category": "incident",
        "action_url": "/incidents",
    },
    {
        "title": "CPU Saturation Alert Triggered",
        "message": "api-prod-01 CPU exceeded 90% threshold.",
        "type": "warning",
        "category": "alert",
        "action_url": "/alerts",
    },
    {
        "title": "Monthly Cloud Cost Optimization Digest",
        "message": "AI detected $4,230/mo potential savings in idle EC2 instances.",
        "type": "info",
        "category": "cost",
        "action_url": "/cost",
    },
    {
        "title": "Autonomous AIOps Self-Healing Action",
        "message": "Cleared stale Redis sessions for auth-service automatically.",
        "type": "success",
        "category": "ai",
        "action_url": "/aiops",
    },
]


class NotificationService:
    """Service handling user alert digests & system messages."""

    def __init__(self, crud_repo=crud_notification) -> None:
        self.crud = crud_repo

    async def get_notifications(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        unread_only: bool = False,
        category: Optional[str] = None,
    ) -> List[Notification]:
        notifs = await self.crud.get_multi_by_user(
            db, user_id=user_id, unread_only=unread_only, category=category
        )
        if not notifs:
            notifs = await self.seed_default_notifications(db, user_id)
        return notifs

    async def seed_default_notifications(self, db: AsyncSession, user_id: uuid.UUID) -> List[Notification]:
        created = []
        now = datetime.now(timezone.utc)
        for data in DEFAULT_NOTIFICATIONS:
            n = Notification(
                id=uuid.uuid4(),
                user_id=user_id,
                title=data["title"],
                message=data["message"],
                type=data["type"],
                category=data["category"],
                is_read=False,
                action_url=data["action_url"],
                created_at=now,
                updated_at=now,
            )
            db.add(n)
            created.append(n)
        await db.commit()
        for item in created:
            await db.refresh(item)
        return created

    async def create_notification(self, db: AsyncSession, user_id: uuid.UUID, payload: NotificationCreate) -> Notification:
        now = datetime.now(timezone.utc)
        n = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            title=payload.title,
            message=payload.message,
            type=payload.type,
            category=payload.category,
            is_read=False,
            action_url=payload.action_url,
            created_at=now,
            updated_at=now,
        )
        db.add(n)
        await db.commit()
        await db.refresh(n)
        return n

    async def mark_read(self, db: AsyncSession, notif_id: uuid.UUID) -> Optional[Notification]:
        n = await self.crud.get(db, id=notif_id)
        if not n:
            return None
        n.is_read = True
        n.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(n)
        return n

    async def mark_all_read(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        return await self.crud.mark_all_read(db, user_id)


notification_service = NotificationService()
