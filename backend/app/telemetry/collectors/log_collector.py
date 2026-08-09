"""
Log Collector for Unified Telemetry Platform.
Normalizes incoming log payloads, extracts severity levels and service metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from app.telemetry.schemas.telemetry import LogIngestPayload

log = structlog.get_logger(__name__)


class LogCollector:
    """Collects and standardizes raw infrastructure and application logs."""

    def collect(self, payload: LogIngestPayload) -> dict[str, Any]:
        normalized_level = payload.level.upper()
        if normalized_level not in {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"}:
            normalized_level = "INFO"
        if normalized_level == "WARNING":
            normalized_level = "WARN"

        log.debug("telemetry_log_collected", source=payload.source, level=normalized_level)

        return {
            "source": payload.source,
            "level": normalized_level,
            "message": payload.message,
            "timestamp": payload.timestamp or datetime.now(UTC),
            "service_name": payload.service_name or payload.source,
            "metadata": payload.metadata,
        }


log_collector = LogCollector()
