"""
Pydantic schemas for Kubernetes & Container Intelligence.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class K8sClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    provider: str
    version: str
    region: str
    status: str
    node_count: int
    pod_count: int
    cpu_capacity_cores: float
    cpu_usage_cores: float
    memory_capacity_gb: float
    memory_usage_gb: float
    created_at: datetime
    updated_at: datetime


class K8sNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cluster_id: uuid.UUID
    name: str
    role: str
    status: str
    instance_type: str
    internal_ip: str
    kubelet_version: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    pod_capacity: int
    pods_running: int
    created_at: datetime
    updated_at: datetime


class K8sPodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cluster_id: uuid.UUID
    node_id: Optional[uuid.UUID] = None
    name: str
    namespace: str
    deployment_name: Optional[str] = None
    status: str
    restart_count: int
    cpu_usage_m: float
    memory_usage_mb: float
    container_images: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class K8sDeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cluster_id: uuid.UUID
    name: str
    namespace: str
    desired_replicas: int
    ready_replicas: int
    updated_replicas: int
    strategy: str
    image: str
    created_at: datetime
    updated_at: datetime


class K8sEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    reason: str
    object_kind: str
    object_name: str
    namespace: str
    message: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class K8sAnalysisResponse(BaseModel):
    cluster_health_score: int
    total_pods_monitored: int
    failed_pods_count: int
    warning_events_count: int
    root_cause_analysis: List[Dict[str, Any]]
