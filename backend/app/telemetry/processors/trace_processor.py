"""
Trace Processor for Unified Telemetry Platform.
Analyzes distributed tracing execution spans and pinpoints service bottlenecks.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class TraceProcessor:
    """Processes distributed tracing spans and identifies latency bottlenecks."""

    def process(self, spans_data: list[dict[str, Any]]) -> dict[str, Any]:
        slowest_span = None
        max_duration = 0.0
        error_spans = []

        for span in spans_data:
            dur = span["duration"]
            if dur > max_duration:
                max_duration = dur
                slowest_span = span
            if span["status"] in {"ERROR", "TIMEOUT"}:
                error_spans.append(span)

        is_bottleneck = max_duration > 500.0 or len(error_spans) > 0
        anomaly_event = None

        if is_bottleneck and slowest_span:
            serialized_errors = [
                {
                    **span,
                    "timestamp": span["timestamp"].isoformat()
                    if hasattr(span.get("timestamp"), "isoformat")
                    else str(span.get("timestamp")),
                }
                for span in error_spans
            ]
            anomaly_event = {
                "source": "trace_processor",
                "event_type": "trace_bottleneck",
                "severity": "CRITICAL" if len(error_spans) > 0 else "WARN",
                "timestamp": slowest_span["timestamp"],
                "metadata_": {
                    "slowest_service": slowest_span["service_name"],
                    "operation": slowest_span["operation"],
                    "duration_ms": max_duration,
                    "error_spans_count": len(error_spans),
                },
                "raw_payload": {"spans_count": len(spans_data), "errors": serialized_errors},
            }

        return {
            "spans": spans_data,
            "slowest_span": slowest_span,
            "error_spans": error_spans,
            "is_bottleneck": is_bottleneck,
            "anomaly_event": anomaly_event,
        }


trace_processor = TraceProcessor()
