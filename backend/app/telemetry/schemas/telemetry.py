"""
Pydantic v2 schemas for Unified Telemetry Intelligence Platform.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogIngestPayload(BaseModel):
    source: str = Field("app", description="Source of log (e.g. k8s, aws, app, postgres)")
    level: str = Field("INFO", description="Log level: DEBUG, INFO, WARN, ERROR, CRITICAL")
    message: str = Field(..., min_length=1, description="Log message text")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
    service_name: str | None = Field(None, description="Originating service name")


class MetricIngestPayload(BaseModel):
    resource_id: str = Field(..., description="Target resource or pod ID")
    metric_name: str = Field(..., description="Metric identifier, e.g. cpu_usage_pct, mem_usage_pct, db_latency_ms")
    value: float = Field(..., description="Numerical metric value")
    unit: str = Field("percent", description="Measurement unit: percent, ms, count, bytes, rps")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    labels: dict[str, str] = Field(default_factory=dict)


class TraceSpanItem(BaseModel):
    operation: str = Field(..., description="Operation / endpoint name")
    duration_ms: float = Field(..., ge=0.0, description="Duration in milliseconds")
    status: str = Field("OK", description="Status code or text: OK, ERROR, TIMEOUT")
    tags: dict[str, Any] = Field(default_factory=dict)


class TraceIngestPayload(BaseModel):
    service_name: str = Field(..., description="Service emitting the trace")
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    spans: list[TraceSpanItem] = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TelemetryEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None
    source: str
    event_type: str
    severity: str
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_")
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class MetricRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resource_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime


class TraceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_name: str
    operation: str
    duration: float
    status: str
    timestamp: datetime


class TelemetryHealthResponse(BaseModel):
    status: str
    pipelines: dict[str, str]
    events_ingested_total: int
    metrics_ingested_total: int
    traces_ingested_total: int
    active_anomalies_count: int
    ai_status: str
    timestamp: datetime


class AIAnomalyReport(BaseModel):
    metric_name: str
    resource_id: str
    anomaly_detected: bool
    deviation_factor: float
    message: str
    severity: str
    suggested_action: str


class AIOperationalSummary(BaseModel):
    summary: str
    root_cause_analysis: str
    impacted_services: list[str]
    confidence_score: float
    recommended_mitigations: list[str]
