"""
Pydantic Schemas for Platform Health & Readiness API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DependencyHealthItem(BaseModel):
    """Dependency health item metadata."""

    status: str = Field(..., example="healthy")
    latency_ms: float = Field(..., example=1.45)
    last_checked: str
    message: str = Field(..., example="Operational")
    provider_mode: str | None = None
    cloud_credential_status: str | None = None


class SystemMetrics(BaseModel):
    """System resource & process metrics."""

    cpu_usage_pct: float
    process_memory_mb: float
    system_memory_pct: float
    process_uptime_seconds: float
    total_requests: int
    error_count: int
    error_rate_pct: float
    avg_latency_ms: float


class SlowestEndpointItem(BaseModel):
    """Slowest endpoint latency item."""

    method: str
    endpoint: str
    avg_latency_ms: float
    requests: int


class ApiPerformanceSummary(BaseModel):
    """API performance telemetry summary."""

    requests_per_minute: float
    avg_latency_ms: float
    error_rate_pct: float
    slowest_endpoints: list[SlowestEndpointItem]


class SystemEventItem(BaseModel):
    """System event log item."""

    timestamp: str
    severity: str
    component: str
    message: str


class EnvironmentInfo(BaseModel):
    """Environment operational metadata."""

    environment: str
    ai_mode: str
    ai_mode_label: str
    cloud_credential_status: str
    demo_mode: bool


class PlatformHealthSummaryResponse(BaseModel):
    """Basic platform health summary response."""

    status: str
    app: str
    version: str
    env: str
    overall_health_score: int
    overall_status: str
    dependencies: dict[str, DependencyHealthItem]


class PlatformHealthDetailedResponse(BaseModel):
    """Detailed platform health response for Platform Health Dashboard."""

    overall_health_score: int
    overall_status: str
    availability_pct: float
    healthy_components_count: int
    degraded_components_count: int
    unhealthy_components_count: int
    dependencies: dict[str, DependencyHealthItem]
    system_metrics: SystemMetrics
    api_performance: ApiPerformanceSummary
    system_events: list[SystemEventItem]
    environment_info: EnvironmentInfo


class ReadinessResponse(BaseModel):
    """Kubernetes / Docker readiness response."""

    status: str
    ready: bool
    timestamp: float
    dependencies: dict[str, str]


class LivenessResponse(BaseModel):
    """Kubernetes / Docker liveness response."""

    status: str
    alive: bool
    timestamp: float
