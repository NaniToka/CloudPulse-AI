"""
Metric Collector for Unified Telemetry Platform.
Collects and validates incoming numerical telemetry signals.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
import structlog

from app.telemetry.schemas.telemetry import MetricIngestPayload

log = structlog.get_logger(__name__)


class MetricCollector:
    """Collects and standardizes cloud resource metrics."""

    def collect(self, payload: MetricIngestPayload) -> dict[str, Any]:
        log.debug(
            "telemetry_metric_collected",
            resource=payload.resource_id,
            metric=payload.metric_name,
            value=payload.value,
        )
        return {
            "resource_id": payload.resource_id,
            "metric_name": payload.metric_name,
            "value": float(payload.value),
            "unit": payload.unit,
            "timestamp": payload.timestamp or datetime.now(UTC),
            "labels": payload.labels,
        }


metric_collector = MetricCollector()
