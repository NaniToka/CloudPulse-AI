"""
Pydantic v2 schemas for Real-Time Observability Platform.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class K8sPodStatus(BaseModel):
    name: str
    namespace: str = "default"
    node: str = "node-us-east-1a"
    service: str = "api-gateway"
    status: str = "Running"  # Running, Pending, Failed, Rebuilding
    cpu_percent: float = 42.5
    memory_mb: float = 380.0
    restarts: int = 0
    uptime: str = "4d 12h"


class MetricPointBase(BaseModel):
    cpu_usage: float = Field(..., ge=0.0, le=100.0, description="CPU usage %")
    memory_usage: float = Field(..., ge=0.0, le=100.0, description="Memory usage %")
    disk_usage: float = Field(..., ge=0.0, le=100.0, description="Disk usage %")
    network_traffic_mbps: float = Field(..., description="Network traffic in Mbps")
    active_users: int = Field(..., ge=0)
    requests_per_second: int = Field(..., ge=0)
    error_rate: float = Field(..., ge=0.0, le=100.0, description="Error rate %")
    response_time_ms: float = Field(..., ge=0.0)
    db_connections_active: int = Field(..., ge=0)
    db_connections_max: int = Field(..., ge=0)
    k8s_pods: list[K8sPodStatus] = Field(default_factory=list)
    timestamp: datetime


class MetricPointCreate(MetricPointBase):
    pass


class MetricPointResponse(MetricPointBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class MetricCurrentResponse(BaseModel):
    current: MetricPointResponse
    is_live: bool = True
    update_interval_ms: int = 2000


class MetricHistoryResponse(BaseModel):
    history: list[MetricPointResponse]
    total_points: int
    buffer_size: int = 300
