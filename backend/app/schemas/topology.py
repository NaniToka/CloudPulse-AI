"""
Pydantic Schemas for Enterprise Cloud Topology & Blast-Radius Intelligence.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TopologyNodeItem(BaseModel):
    id: str
    name: str
    type: str  # service, api, database, queue, k8s_workload, cloud_resource, vpc, cluster, region, provider
    provider: str  # AWS, Azure, GCP, Kubernetes
    region: str
    environment: str = "production"
    status: str = "HEALTHY"  # HEALTHY, DEGRADED, CRITICAL, UNKNOWN
    health_score: float = 100.0
    monthly_cost: float = 0.0
    risk_score: int = 0
    security_findings_count: int = 0
    governance_status: str = "COMPLIANT"
    active_incidents_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class TopologyEdgeItem(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str  # DEPENDS_ON, CALLS, CONNECTS_TO, HOSTS, ROUTES_TO, READS_FROM, WRITES_TO, CONTAINS, RUNS_ON, EXPOSES
    protocol: str = "HTTP/1.1"
    confidence: float = 1.0
    latency_ms: float | None = None
    error_rate: float | None = None


class TopologyOverviewResponse(BaseModel):
    total_nodes: int
    total_edges: int
    total_providers: int
    total_regions: int
    unhealthy_nodes_count: int
    spof_count: int
    total_monthly_cost: float
    updated_at: datetime


class TopologyGraphResponse(BaseModel):
    nodes: list[TopologyNodeItem]
    edges: list[TopologyEdgeItem]
    total_nodes: int
    total_edges: int
    generated_at: datetime


class BlastRadiusAnalysisResponse(BaseModel):
    target_node_id: str
    target_node_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    affected_node_count: int
    affected_service_count: int
    affected_resource_count: int
    affected_providers: list[str]
    affected_regions: list[str]
    directly_affected_nodes: list[str]
    indirectly_affected_nodes: list[str]
    propagation_paths: list[list[str]]
    estimated_impact_level: str
    recommended_mitigation: str
    generated_at: datetime


class FailureSimulationRequest(BaseModel):
    node_id: str
    failure_type: str = "TOTAL_OUTAGE"  # TOTAL_OUTAGE, LATENCY_SPIKE, NETWORK_PARTITION, DISK_SATURATION


class FailureSimulationResponse(BaseModel):
    target_node_id: str
    target_node_name: str
    failure_type: str
    is_simulation: bool = True
    blast_radius: BlastRadiusAnalysisResponse
    critical_path: list[str]
    spof_detected: bool
    mitigation_steps: list[str]
    simulated_at: datetime


class SpofItem(BaseModel):
    node_id: str
    node_name: str
    node_type: str
    provider: str
    region: str
    dependent_count: int
    affected_services: list[str]
    risk_level: str  # CRITICAL, HIGH, MEDIUM
    reason: str
    recommendation: str


class SpofListResponse(BaseModel):
    total_spofs: int
    spofs: list[SpofItem]


class DependencyPathSegment(BaseModel):
    source_name: str
    target_name: str
    relationship_type: str
    latency_ms: float | None = None
    telemetry_status: str = "AVAILABLE"  # AVAILABLE, TELEMETRY_UNAVAILABLE


class DependencyPathItem(BaseModel):
    path_id: str
    start_node: str
    end_node: str
    segments: list[DependencyPathSegment]
    total_latency_ms: float | None = None
    health_status: str = "HEALTHY"
    monthly_cost: float = 0.0


class DependencyPathResponse(BaseModel):
    paths: list[DependencyPathItem]
