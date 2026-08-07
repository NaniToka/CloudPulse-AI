"""
Pydantic schemas for Server Infrastructure.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServerCreate(BaseModel):
    name: str = Field(..., description="Server name")
    hostname: str | None = None
    ip_address: str | None = None
    server_type: str = Field("linux", description="linux | windows | container | vm")
    provider: str = Field("AWS", description="AWS | GCP | Azure | on-prem")
    region: str | None = "us-east-1"
    environment: str = Field("production", description="production | staging | dev")


class ServerUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_percent: float | None = None


class ServerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    hostname: str
    ip_address: str | None = None
    server_type: str
    provider: str
    region: str | None = None
    environment: str
    status: str
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_percent: float | None = None
    network_in_mbps: float | None = None
    network_out_mbps: float | None = None
    uptime_seconds: int | None = None
    created_at: datetime
    updated_at: datetime
