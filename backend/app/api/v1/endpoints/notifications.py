"""
User Notifications REST API Endpoints.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import notification_service, NotificationService

router = APIRouter()


@router.get("", response_model=List[NotificationResponse], summary="List Notifications")
async def list_notifications(
    unread_only: bool = Query(False, description="Filter unread notifications only"),
    category: Optional[str] = Query(None, description="Filter category (incident, alert, cost, ai, system)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: NotificationService = Depends(lambda: notification_service),
):
    """Retrieve user notifications."""
    notifs = await service.get_notifications(
        db, user_id=current_user.id, unread_only=unread_only, category=category
    )
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED, summary="Create Notification")
async def create_notification(
    payload: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: NotificationService = Depends(lambda: notification_service),
):
    """Create a system or user notification."""
    notif = await service.create_notification(db, user_id=current_user.id, payload=payload)
    return NotificationResponse.model_validate(notif)


@router.patch("/{notif_id}/read", response_model=NotificationResponse, summary="Mark Notification Read")
async def mark_notification_read(
    notif_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: NotificationService = Depends(lambda: notification_service),
):
    """Mark a notification as read."""
    notif = await service.mark_read(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.model_validate(notif)


@router.post("/read-all", summary="Mark All Notifications Read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: NotificationService = Depends(lambda: notification_service),
):
    """Mark all unread notifications as read."""
    count = await service.mark_all_read(db, user_id=current_user.id)
    return {"status": "success", "marked_count": count}
