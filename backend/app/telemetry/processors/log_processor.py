"""
Log Processor for Unified Telemetry Platform.
Evaluates log severity, extracts error signatures, and classifies log events.
"""

from __future__ import annotations

from typing import Any
import structlog

log = structlog.get_logger(__name__)


class LogProcessor:
    """Processes collected logs, tags anomalies, and prepares event records."""

    def process(self, collected_log: dict[str, Any]) -> dict[str, Any]:
        msg = collected_log["message"]
        level = collected_log["level"]
        is_error = level in {"ERROR", "CRITICAL"} or any(
            err_kw in msg.lower()
            for err_kw in ["exception", "traceback", "fatal", "oomkilled", "crashloop", "timeout 504"]
        )

        severity = "CRITICAL" if "fatal" in msg.lower() or "oom" in msg.lower() else ("ERROR" if is_error else level)

        event_type = "log_error" if is_error else "log"

        return {
            "source": collected_log["source"],
            "event_type": event_type,
            "severity": severity,
            "timestamp": collected_log["timestamp"],
            "metadata_": {
                "service_name": collected_log["service_name"],
                "is_error": is_error,
                **collected_log["metadata"],
            },
            "raw_payload": {"message": msg, "original_level": level},
        }


log_processor = LogProcessor()
