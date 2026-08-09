"""
Trace Collector for Unified Telemetry Platform.
Collects and aggregates distributed tracing spans and execution trees.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from app.telemetry.schemas.telemetry import TraceIngestPayload

log = structlog.get_logger(__name__)


class TraceCollector:
    """Collects distributed traces and calculates aggregate span durations."""

    def collect(self, payload: TraceIngestPayload) -> list[dict[str, Any]]:
        results = []
        base_ts = payload.timestamp or datetime.now(UTC)
        for span in payload.spans:
            results.append({
                "service_name": payload.service_name,
                "operation": span.operation,
                "duration": span.duration_ms,
                "status": span.status.upper(),
                "timestamp": base_ts,
                "tags": span.tags,
                "trace_id": payload.trace_id,
            })
        log.debug("telemetry_trace_collected", service=payload.service_name, span_count=len(payload.spans))
        return results


trace_collector = TraceCollector()
