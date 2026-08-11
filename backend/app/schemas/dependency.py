"""
Pydantic Schemas for AI Service Dependency & Root-Cause Intelligence Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# ServiceNode Schemas
# ---------------------------------------------------------------------------
class ServiceNodeBase(BaseModel):
    name: str = Field(..., description="Unique service identifier/name (e.g. payment-service)")
    type: str = Field(
        "service",
        description="Node type (service, api, database, queue, k8s_workload, cloud_resource, external)",
    )
    environment: str = Field("production", description="Environment (production, staging, dev)")
    region: str = Field("us-east-1", description="Cloud region")
    status: str = Field("HEALTHY", description="Status (HEALTHY, DEGRADED, CRITICAL, UNKNOWN)")
    health_score: float = Field(100.0, ge=0.0, le=100.0, description="Health score (0-100)")
    error_rate: float = Field(0.0, ge=0.0, le=100.0, description="Error rate percentage")
    latency_p99_ms: float = Field(45.0, ge=0.0, description="P99 latency in ms")
    request_rate: float = Field(120.0, ge=0.0, description="Requests per second")
    active_incidents_count: int = Field(0, ge=0, description="Active incidents count")
    metadata_json: dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")


class ServiceNodeCreate(ServiceNodeBase):
    organization_id: uuid.UUID | None = None


class ServiceNodeUpdate(BaseModel):
    type: str | None = None
    environment: str | None = None
    region: str | None = None
    status: str | None = None
    health_score: float | None = None
    error_rate: float | None = None
    latency_p99_ms: float | None = None
    request_rate: float | None = None
    active_incidents_count: int | None = None
    metadata_json: dict[str, Any] | None = None


class ServiceNodeResponse(ServiceNodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class ServiceNodeDetailResponse(ServiceNodeResponse):
    upstream_dependencies: list[ServiceDependencyResponse] = Field(default_factory=list)
    downstream_dependents: list[ServiceDependencyResponse] = Field(default_factory=list)
    recent_incidents: list[dict[str, Any]] = Field(default_factory=list)
    recent_alerts: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# ServiceDependency Schemas
# ---------------------------------------------------------------------------
class ServiceDependencyBase(BaseModel):
    source_service: str = Field(..., description="Calling/Upstream service name")
    target_service: str = Field(..., description="Called/Downstream service name")
    dependency_type: str = Field(
        "http",
        description="Dependency type (http, database, queue, network, kubernetes, cloud_resource, grpc, internal)",
    )
    protocol: str = Field(
        "HTTP/1.1",
        description="Protocol (HTTP/1.1, HTTP/2, gRPC, PostgreSQL, Redis, AMQP, Kafka, TCP)",
    )
    discovered_from: str = Field(
        "traces",
        description="Telemetry source (traces, logs, metrics, kubernetes, cloud_resources, config, manual)",
    )
    confidence: float = Field(0.85, ge=0.0, le=1.0, description="Confidence score (0.0 - 1.0)")
    latency_ms: float = Field(42.5, ge=0.0, description="Average response latency in ms")
    avg_duration_ms: float = Field(42.5, ge=0.0, description="Average duration in ms")
    error_rate: float = Field(0.0, ge=0.0, le=100.0, description="Call failure error rate percent")
    request_rate: float = Field(50.0, ge=0.0, description="Call rate in requests/sec")
    call_count: int = Field(1250, ge=0, description="Observed call volume")
    error_count: int = Field(0, ge=0, description="Observed error count")
    evidence_count: int = Field(1, ge=1, description="Number of distinct evidence observations")
    evidence_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Discovery telemetry attributes"
    )


class ServiceDependencyCreate(ServiceDependencyBase):
    organization_id: uuid.UUID | None = None
    source_service_id: uuid.UUID | None = None
    target_service_id: uuid.UUID | None = None


class ServiceDependencyUpdate(BaseModel):
    dependency_type: str | None = None
    protocol: str | None = None
    confidence: float | None = None
    latency_ms: float | None = None
    avg_duration_ms: float | None = None
    error_rate: float | None = None
    request_rate: float | None = None
    call_count: int | None = None
    error_count: int | None = None
    evidence_count: int | None = None
    evidence_metadata: dict[str, Any] | None = None


class ServiceDependencyResponse(ServiceDependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    source_service_id: uuid.UUID | None = None
    target_service_id: uuid.UUID | None = None
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Graph & Health Schemas
# ---------------------------------------------------------------------------
class DependencyGraphResponse(BaseModel):
    nodes: list[ServiceNodeResponse] = Field(default_factory=list)
    edges: list[ServiceDependencyResponse] = Field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0
    critical_path: list[str] = Field(default_factory=list)
    unhealthy_services_count: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ServiceHealthResponse(BaseModel):
    service_id: uuid.UUID | None = None
    service_name: str
    health_score: float = Field(..., ge=0.0, le=100.0)
    status: str = Field(..., description="HEALTHY, DEGRADED, CRITICAL, UNKNOWN")
    error_rate: float = 0.0
    latency_p99_ms: float = 0.0
    active_incidents_count: int = 0
    dependency_health_penalty: float = 0.0
    factors: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Blast Radius & Failure Propagation Schemas
# ---------------------------------------------------------------------------
class BlastRadiusRequest(BaseModel):
    service_name: str
    depth: int = Field(5, ge=1, le=20)
    simulate_total_failure: bool = True


class FailurePropagationHop(BaseModel):
    source: str
    target: str
    latency_increase_percent: float = 0.0
    error_rate: float = 0.0
    propagation_risk: str = "LOW"  # CRITICAL, HIGH, MEDIUM, LOW


class BlastRadiusResponse(BaseModel):
    root_component: str
    directly_affected_resources: list[str] = Field(default_factory=list)
    indirectly_affected_resources: list[str] = Field(default_factory=list)
    affected_services: list[str] = Field(default_factory=list)
    dependency_depth: int = 1
    propagation_paths: list[list[str]] = Field(default_factory=list)
    propagation_hops: list[FailurePropagationHop] = Field(default_factory=list)
    estimated_user_impact: str = "LOW"
    financial_risk_estimate: str = "$0 / hr"
    affected_endpoints: list[str] = Field(default_factory=list)
    affected_regions: list[str] = Field(default_factory=list)
    topology_graph: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Root Cause Ranking & Evidence Schemas
# ---------------------------------------------------------------------------
class RootCauseCandidate(BaseModel):
    service_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    rank: int = 1
    temporal_score: float = 0.0
    dependency_score: float = 0.0
    anomaly_score: float = 0.0
    propagation_score: float = 0.0
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    recommended_actions: list[dict[str, Any]] = Field(default_factory=list)


class RootCauseRankingRequest(BaseModel):
    service_name: str | None = None
    incident_id: uuid.UUID | None = None
    signals: list[dict[str, Any]] | None = None


class RootCauseRankingResponse(BaseModel):
    primary_root_cause: str
    primary_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    candidates: list[RootCauseCandidate] = Field(default_factory=list)
    reasoning_summary: str = ""
    evidence_graph: list[dict[str, Any]] = Field(default_factory=list)
    blast_radius: BlastRadiusResponse | None = None
    analysis_engine: str = "local"  # gemini | local
    recommended_actions: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Discovery & Pagination Schemas
# ---------------------------------------------------------------------------
class DependencyDiscoveryRequest(BaseModel):
    time_window_minutes: int = Field(60, ge=5, le=1440)
    include_traces: bool = True
    include_logs: bool = True
    include_k8s: bool = True
    include_cloud: bool = True


class DependencyDiscoveryResponse(BaseModel):
    discovered_nodes_count: int
    discovered_edges_count: int
    updated_edges_count: int
    sources_processed: list[str]
    discovered_at: datetime = Field(default_factory=datetime.utcnow)


class ServiceListResponse(BaseModel):
    items: list[ServiceNodeResponse]
    total: int
    page: int
    size: int
    pages: int
