"""
Pydantic v2 schemas for Distributed Tracing Platform.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SpanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    span_kind: str = "SERVER"
    status_code: str = "OK"
    duration_ms: float
    start_time: datetime
    end_time: datetime
    attributes_json: Dict[str, Any] = Field(default_factory=dict)
    events_json: List[Any] = Field(default_factory=list)


class TraceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trace_id: str
    name: str
    root_service: str
    http_method: str = "GET"
    http_status: int = 200
    duration_ms: float
    status: str = "ok"
    span_count: int = 1
    created_at: datetime
    spans: List[SpanResponse] = Field(default_factory=list)
    ai_analysis_json: Optional[Dict[str, Any]] = None


class TraceListResponse(BaseModel):
    items: List[TraceResponse]
    total: int
    page: int
    size: int
    pages: int


class ServiceNode(BaseModel):
    id: str
    label: str
    type: str = "service"  # service, database, cache, gateway, external
    status: str = "healthy"  # healthy, warning, critical
    avg_latency_ms: float
    rps: float
    error_rate_percent: float


class ServiceEdge(BaseModel):
    source: str
    target: str
    call_count: int
    avg_duration_ms: float
    error_rate_percent: float


class ServiceMapResponse(BaseModel):
    nodes: List[ServiceNode]
    edges: List[ServiceEdge]


class ServiceMetricsResponse(BaseModel):
    service_name: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    requests_per_second: float
    error_rate_percent: float
    dependencies: List[str]
    ai_summary: str


class TraceAIAnalysisResponse(BaseModel):
    trace_id: str
    bottleneck_detected: bool
    slowest_service: str
    root_cause: str
    latency_breakdown: Dict[str, float]
    optimization_suggestions: List[str]
    retry_recommendations: List[str]
    scaling_suggestions: List[str]
    performance_score: float  # 0 to 100
    confidence_score: float  # 0.0 to 1.0
