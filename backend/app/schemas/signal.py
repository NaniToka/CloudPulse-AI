"""
Normalized Signal Schema & Ingestion Normalizer.

Standardizes signals across metrics, logs, alerts, traces, anomalies,
Kubernetes events, and cloud infrastructure signals into a unified representation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SignalSource(str, Enum):
    TELEMETRY = "telemetry"
    ALERT = "alert"
    LOG = "log"
    TRACE = "trace"
    ANOMALY = "anomaly"
    KUBERNETES = "kubernetes"
    INFRASTRUCTURE = "infrastructure"


class SignalSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


SEVERITY_MAPPING: dict[str, SignalSeverity] = {
    "critical": SignalSeverity.CRITICAL,
    "crit": SignalSeverity.CRITICAL,
    "fatal": SignalSeverity.CRITICAL,
    "p0": SignalSeverity.CRITICAL,
    "error": SignalSeverity.HIGH,
    "high": SignalSeverity.HIGH,
    "p1": SignalSeverity.HIGH,
    "warn": SignalSeverity.MEDIUM,
    "warning": SignalSeverity.MEDIUM,
    "medium": SignalSeverity.MEDIUM,
    "p2": SignalSeverity.MEDIUM,
    "info": SignalSeverity.LOW,
    "low": SignalSeverity.LOW,
    "p3": SignalSeverity.LOW,
    "debug": SignalSeverity.LOW,
}


class NormalizedSignal(BaseModel):
    """
    Unified signal representation across all observability data sources.
    """

    model_config = ConfigDict(populate_by_name=True)

    signal_id: str = Field(
        default_factory=lambda: f"sig-{uuid.uuid4().hex[:12]}",
        description="Unique identifier for the signal",
    )
    source: SignalSource = Field(
        default=SignalSource.TELEMETRY,
        description="Source type: telemetry, alert, log, trace, anomaly, kubernetes, infrastructure",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the signal occurred",
    )
    service: str = Field(
        default="api-gateway",
        description="Primary affected service name",
    )
    resource_id: str | None = Field(
        default=None,
        description="Resource / host / pod / container / database ID",
    )
    environment: str = Field(
        default="production",
        description="Environment: production, staging, development",
    )
    region: str = Field(
        default="us-east-1",
        description="Cloud region",
    )
    severity: SignalSeverity = Field(
        default=SignalSeverity.HIGH,
        description="Normalized severity: CRITICAL, HIGH, MEDIUM, LOW",
    )
    title: str = Field(
        ...,
        description="Short title or event name",
    )
    message: str = Field(
        default="",
        description="Detailed signal description, message, or log excerpt",
    )
    metric: str | None = Field(
        default=None,
        description="Metric name if metric anomaly (e.g. cpu_usage_percent, memory_usage_bytes)",
    )
    value: float | None = Field(
        default=None,
        description="Numerical metric value or latency in ms",
    )
    threshold: float | None = Field(
        default=None,
        description="Breached threshold value",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional signal metadata (trace_id, error_code, labels)",
    )


def normalize_signal(raw: dict[str, Any] | Any) -> NormalizedSignal:
    """
    Converts any arbitrary dictionary or ORM record into a NormalizedSignal.
    """
    if isinstance(raw, NormalizedSignal):
        return raw

    if not isinstance(raw, dict):
        # Extract attributes from object
        data: dict[str, Any] = {}
        for attr in [
            "signal_id",
            "id",
            "source",
            "timestamp",
            "created_at",
            "service",
            "service_name",
            "affected_service",
            "resource_id",
            "resource",
            "host",
            "environment",
            "region",
            "severity",
            "title",
            "name",
            "message",
            "description",
            "metric",
            "metric_name",
            "value",
            "metric_value",
            "threshold",
            "metadata",
            "event_metadata",
            "raw_payload",
        ]:
            if hasattr(raw, attr):
                data[attr] = getattr(raw, attr)
        raw = data

    # 1. Source resolution
    raw_source = str(raw.get("source") or raw.get("event_type") or "telemetry").lower()
    if "alert" in raw_source:
        source = SignalSource.ALERT
    elif "log" in raw_source:
        source = SignalSource.LOG
    elif "trace" in raw_source or "span" in raw_source:
        source = SignalSource.TRACE
    elif "k8s" in raw_source or "kube" in raw_source or "pod" in raw_source:
        source = SignalSource.KUBERNETES
    elif "anomaly" in raw_source:
        source = SignalSource.ANOMALY
    elif "infra" in raw_source or "cloud" in raw_source:
        source = SignalSource.INFRASTRUCTURE
    else:
        source = SignalSource.TELEMETRY

    # 2. Timestamp resolution
    raw_time = raw.get("timestamp") or raw.get("created_at") or raw.get("time")
    if isinstance(raw_time, str):
        try:
            timestamp = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        except Exception:
            timestamp = datetime.now(UTC)
    elif isinstance(raw_time, datetime):
        timestamp = raw_time if raw_time.tzinfo else raw_time.replace(tzinfo=UTC)
    else:
        timestamp = datetime.now(UTC)

    # 3. Severity normalization
    raw_sev = str(raw.get("severity") or "HIGH").lower()
    severity = SEVERITY_MAPPING.get(raw_sev, SignalSeverity.HIGH)

    # 4. Service and resource
    service = str(
        raw.get("service")
        or raw.get("service_name")
        or raw.get("affected_service")
        or raw.get("app")
        or "api-gateway"
    )
    resource_id = raw.get("resource_id") or raw.get("resource") or raw.get("host") or raw.get("pod")
    if resource_id is not None:
        resource_id = str(resource_id)

    # 5. Title & Message
    title = str(
        raw.get("title")
        or raw.get("name")
        or raw.get("event_type")
        or raw.get("metric_name")
        or f"Signal on {service}"
    )
    message = str(
        raw.get("message")
        or raw.get("description")
        or raw.get("detail")
        or title
    )

    # 6. Metric & Value
    metric = raw.get("metric") or raw.get("metric_name")
    if metric is not None:
        metric = str(metric)

    val = raw.get("value") or raw.get("metric_value") or raw.get("duration") or raw.get("duration_ms")
    value = float(val) if val is not None else None

    thresh = raw.get("threshold")
    threshold = float(thresh) if thresh is not None else None

    # 7. Metadata
    metadata = raw.get("metadata") or raw.get("event_metadata") or raw.get("tags") or {}
    if not isinstance(metadata, dict):
        metadata = {"raw": str(metadata)}

    # Check for trace_id in raw
    if raw.get("trace_id") and "trace_id" not in metadata:
        metadata["trace_id"] = str(raw.get("trace_id"))
    if raw.get("request_id") and "request_id" not in metadata:
        metadata["request_id"] = str(raw.get("request_id"))
    if raw.get("error_code") and "error_code" not in metadata:
        metadata["error_code"] = str(raw.get("error_code"))

    signal_id = str(raw.get("signal_id") or raw.get("id") or f"sig-{uuid.uuid4().hex[:12]}")
    environment = str(raw.get("environment") or "production")
    region = str(raw.get("region") or raw.get("affected_region") or "us-east-1")

    return NormalizedSignal(
        signal_id=signal_id,
        source=source,
        timestamp=timestamp,
        service=service,
        resource_id=resource_id,
        environment=environment,
        region=region,
        severity=severity,
        title=title,
        message=message,
        metric=metric,
        value=value,
        threshold=threshold,
        metadata=metadata,
    )
