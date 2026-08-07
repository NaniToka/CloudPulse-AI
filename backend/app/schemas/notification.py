"""
Pydantic schemas for User Notifications.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    title: str
    message: Optional[str] = None
    type: str = Field("info", description="info | warning | error | success")
    category: Optional[str] = Field("system", description="incident | alert | cost | ai | system")
    action_url: Optional[str] = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: Optional[str] = None
    type: str
    category: Optional[str] = None
    is_read: bool
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime
