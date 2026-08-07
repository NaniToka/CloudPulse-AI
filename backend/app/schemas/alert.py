"""
Pydantic schemas for Monitoring Alerts.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    title: str
    message: Optional[str] = None
    severity: str = Field("medium", description="critical | high | medium | low")
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None


class AlertUpdate(BaseModel):
    status: str = Field(..., description="active | acknowledged | resolved")


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: Optional[str] = None
    severity: str
    status: str
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    tags: Dict[str, Any] = Field(default_factory=dict)
    resource_id: Optional[uuid.UUID] = None
    incident_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
