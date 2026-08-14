"""
Pydantic Schemas for Enterprise Cloud Asset Intelligence & Resource Inventory.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AssetResourceItem(BaseModel):
    id: uuid.UUID
    name: str
    resource_type: str  # virtual_machine, kubernetes_cluster, database, storage, networking, function, load_balancer
    service: str  # EC2, GKE, RDS, S3, Cloud SQL, AKS, Azure Blob, etc.
    provider: str  # AWS, Azure, GCP, Kubernetes
    region: str
    availability_zone: str | None = None
    environment: str = "production"
    status: str = "healthy"  # healthy, warning, critical, stopped
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_percent: float | None = None
    network_in_mbps: float | None = None
    network_out_mbps: float | None = None
    monthly_cost: float = 0.0
    risk_score: int = 0
    owner: str = "Unassigned"
    lifecycle_state: str = "ACTIVE"  # ACTIVE, IDLE, DEGRADED, ORPHANED, DECOMMISSIONED
    is_orphaned: bool = False
    security_findings_count: int = 0
    governance_compliance_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, WAIVED
    tags: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetOverviewResponse(BaseModel):
    total_resources: int
    aws_count: int
    azure_count: int
    gcp_count: int
    kubernetes_count: int
    healthy_count: int
    warning_count: int
    critical_count: int
    orphaned_count: int
    idle_count: int
    total_monthly_cost: float
    total_potential_savings: float
    mode_indicator: str = "Demo / Local Asset Data"
    updated_at: datetime


class AssetProviderStat(BaseModel):
    provider: str
    resource_count: int
    monthly_cost: float
    percentage: float
    health_score: float


class AssetProviderDistributionResponse(BaseModel):
    providers: list[AssetProviderStat]


class AssetServiceStat(BaseModel):
    service: str
    provider: str
    resource_count: int
    monthly_cost: float


class AssetServiceDistributionResponse(BaseModel):
    services: list[AssetServiceStat]


class AssetRegionStat(BaseModel):
    region: str
    provider: str
    resource_count: int
    monthly_cost: float
    status: str


class AssetRegionDistributionResponse(BaseModel):
    regions: list[AssetRegionStat]


class AssetTypeStat(BaseModel):
    resource_type: str
    count: int
    total_cost: float


class AssetTypeDistributionResponse(BaseModel):
    types: list[AssetTypeStat]


class AssetRelationshipItem(BaseModel):
    id: str
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    relationship_type: str  # CONNECTED_TO, CONTAINS, DEPENDS_ON, MANAGES, EXPOSES
    direction: str = "OUTBOUND"  # INBOUND, OUTBOUND, BIDIRECTIONAL
    confidence: float = 1.0


class AssetTopologyNode(BaseModel):
    id: str
    name: str
    type: str
    provider: str
    region: str
    status: str
    cost: float


class AssetTopologyEdge(BaseModel):
    source: str
    target: str
    label: str


class AssetTopologyResponse(BaseModel):
    nodes: list[AssetTopologyNode]
    edges: list[AssetTopologyEdge]


class OrphanedResourceItem(BaseModel):
    resource_id: str
    resource_name: str
    provider: str
    service: str
    region: str
    reason: str
    monthly_cost: float
    potential_savings: float
    recommended_action: str


class OrphanedResourcesResponse(BaseModel):
    total_orphaned: int
    total_potential_savings: float
    orphaned_resources: list[OrphanedResourceItem]


class AssetDetailResponse(BaseModel):
    resource: AssetResourceItem
    relationships: list[AssetRelationshipItem]
    security_findings: list[dict[str, Any]]
    governance_violations: list[dict[str, Any]]
    finops_optimization: dict[str, Any] | None = None
    related_incidents: list[dict[str, Any]]
    telemetry_summary: dict[str, Any]
