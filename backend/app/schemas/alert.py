"""
Pydantic schemas for Monitoring Alerts.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    title: str
    message: str | None = None
    severity: str = Field("medium", description="critical | high | medium | low")
    metric_name: str | None = None
    metric_value: float | None = None
    threshold: float | None = None


class AlertUpdate(BaseModel):
    status: str = Field(..., description="active | acknowledged | resolved")


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: str | None = None
    severity: str
    status: str
    metric_name: str | None = None
    metric_value: float | None = None
    threshold: float | None = None
    tags: dict[str, Any] = Field(default_factory=dict)
    resource_id: uuid.UUID | None = None
    incident_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
