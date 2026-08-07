"""
OpenTelemetry & W3C Trace Context Distributed Tracing integration.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import structlog

log = structlog.get_logger(__name__)


def generate_trace_id() -> str:
    """Generate a standard 32-hex character OpenTelemetry trace ID."""
    return uuid.uuid4().hex


def generate_span_id() -> str:
    """Generate a standard 16-hex character OpenTelemetry span ID."""
    return uuid.uuid4().hex[:16]


class SpanContext:
    """Represents an active OpenTelemetry distributed trace span."""

    def __init__(
        self,
        name: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.trace_id = trace_id or generate_trace_id()
        self.parent_span_id = parent_span_id
        self.span_id = generate_span_id()
        self.attributes = attributes or {}
        self.start_time = time.time()
        self.end_time: float | None = None
        self.duration_ms: float = 0.0
        self.status = "OK"

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def finish(self, status: str = "OK") -> dict[str, Any]:
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
        }

    def to_w3c_traceparent(self) -> str:
        """Format as W3C traceparent header: 00-{trace_id}-{span_id}-01."""
        return f"00-{self.trace_id}-{self.span_id}-01"

    @classmethod
    def from_w3c_traceparent(cls, name: str, traceparent: str) -> SpanContext:
        """Parse incoming W3C traceparent header."""
        try:
            parts = traceparent.split("-")
            if len(parts) >= 4:
                return cls(name=name, trace_id=parts[1], parent_span_id=parts[2])
        except Exception:
            pass
        return cls(name=name)
