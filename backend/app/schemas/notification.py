"""
Pydantic schemas for User Notifications.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    title: str
    message: str | None = None
    type: str = Field("info", description="info | warning | error | success")
    category: str | None = Field("system", description="incident | alert | cost | ai | system")
    action_url: str | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str | None = None
    type: str
    category: str | None = None
    is_read: bool
    action_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime
