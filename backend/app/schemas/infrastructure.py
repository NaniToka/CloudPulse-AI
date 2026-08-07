"""
Pydantic schemas for Server Infrastructure.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ServerCreate(BaseModel):
    name: str = Field(..., description="Server name")
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    server_type: str = Field("linux", description="linux | windows | container | vm")
    provider: str = Field("AWS", description="AWS | GCP | Azure | on-prem")
    region: Optional[str] = "us-east-1"
    environment: str = Field("production", description="production | staging | dev")


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_percent: Optional[float] = None


class ServerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    hostname: str
    ip_address: Optional[str] = None
    server_type: str
    provider: str
    region: Optional[str] = None
    environment: str
    status: str
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_percent: Optional[float] = None
    network_in_mbps: Optional[float] = None
    network_out_mbps: Optional[float] = None
    uptime_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime
