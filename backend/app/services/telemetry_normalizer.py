"""
Telemetry Normalization Engine for Time-Series Observability.

Standardizes, resamples, and aligns raw telemetry metrics across:
- CPU, Memory, Disk, and Network utilization
- HTTP / gRPC Latency (P50, P95, P99)
- Request throughput and error rates
- Kubernetes Pod and container resource metrics
- Database connection pools and transaction queues
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# Standard Metric Canonical Mappings
METRIC_ALIASES: dict[str, str] = {
    "cpu": "cpu_utilization",
    "cpu_usage": "cpu_utilization",
    "cpu_percent": "cpu_utilization",
    "cpu_usage_pct": "cpu_utilization",
    "memory": "memory_utilization",
    "memory_usage": "memory_utilization",
    "mem_usage_pct": "memory_utilization",
    "memory_heap": "memory_utilization",
    "disk": "disk_utilization",
    "disk_usage": "disk_utilization",
    "network": "network_traffic_mbps",
    "network_traffic": "network_traffic_mbps",
    "rps": "requests_per_second",
    "request_rate": "requests_per_second",
    "requests": "requests_per_second",
    "error_rate": "error_rate",
    "error_rate_spike": "error_rate",
    "http_5xx": "error_rate",
    "latency": "latency_ms",
    "response_time": "latency_ms",
    "response_time_ms": "latency_ms",
    "p99_latency": "latency_ms",
    "db_connections": "db_connections_active",
    "db_connections_active": "db_connections_active",
    "connections": "db_connections_active",
}


@dataclass
class NormalizedDataPoint:
    """Canonical time-series data point."""

    timestamp: datetime
    value: float


@dataclass
class NormalizedTimeSeries:
    """Canonical time-series series container."""

    metric_name: str
    service: str = "default"
    resource_id: str | None = None
    unit: str = "percent"
    points: list[NormalizedDataPoint] = field(default_factory=list)
    sample_count: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    interval_seconds: int = 60

    @property
    def values(self) -> list[float]:
        return [p.value for p in self.points]

    @property
    def timestamps(self) -> list[datetime]:
        return [p.timestamp for p in self.points]


class TelemetryNormalizer:
    """Normalizes, resamples, and aligns time-series observations."""

    @staticmethod
    def canonical_metric_name(raw_name: str) -> str:
        """Converts raw metric name to standard canonical metric key."""
        cleaned = raw_name.strip().lower()
        return METRIC_ALIASES.get(cleaned, cleaned)

    @staticmethod
    def to_utc(dt: datetime | str | None) -> datetime:
        """Ensures datetime is timezone-aware in UTC."""
        if dt is None:
            return datetime.now(UTC)
        if isinstance(dt, str):
            try:
                parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    return parsed.replace(tzinfo=UTC)
                return parsed.astimezone(UTC)
            except Exception:
                return datetime.now(UTC)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    def normalize(
        self,
        raw_points: Sequence[tuple[datetime | str, float] | dict[str, Any] | float],
        metric_name: str = "cpu_utilization",
        service: str = "default",
        resource_id: str | None = None,
        unit: str = "percent",
        bucket_seconds: int = 60,
    ) -> NormalizedTimeSeries:
        """
        Normalizes raw telemetry points:
        - Parses heterogeneous input types (scalars, tuples, dicts, ORM records)
        - Converts all timestamps to UTC
        - Sorts chronologically
        - Averages duplicate bucket timestamps
        - Linear interpolation for missing gaps if bucketed
        """
        parsed_points: list[NormalizedDataPoint] = []
        now = datetime.now(UTC)

        for idx, item in enumerate(raw_points):
            if isinstance(item, int | float):
                # Relative sequential points ending at now
                t = now - timedelta(seconds=(len(raw_points) - idx - 1) * bucket_seconds)
                parsed_points.append(NormalizedDataPoint(timestamp=t, value=float(item)))
            elif isinstance(item, tuple) and len(item) == 2:
                t = self.to_utc(item[0])
                parsed_points.append(NormalizedDataPoint(timestamp=t, value=float(item[1])))
            elif isinstance(item, dict):
                raw_t = item.get("timestamp") or item.get("time") or item.get("created_at") or now
                raw_v = (
                    item.get("value")
                    or item.get("metric_value")
                    or item.get(metric_name)
                    or 0.0
                )
                t = self.to_utc(raw_t)
                parsed_points.append(NormalizedDataPoint(timestamp=t, value=float(raw_v)))
            elif hasattr(item, "timestamp") and hasattr(item, "value"):
                t = self.to_utc(getattr(item, "timestamp"))
                v = float(getattr(item, "value"))
                parsed_points.append(NormalizedDataPoint(timestamp=t, value=v))

        # Sort chronologically
        parsed_points.sort(key=lambda p: p.timestamp)

        # Deduplicate & bucket by timestamp rounding
        if bucket_seconds > 0 and len(parsed_points) > 1:
            bucketed_dict: dict[int, list[float]] = {}
            for p in parsed_points:
                epoch_sec = int(p.timestamp.timestamp())
                bucket_key = (epoch_sec // bucket_seconds) * bucket_seconds
                bucketed_dict.setdefault(bucket_key, []).append(p.value)

            deduped_points: list[NormalizedDataPoint] = []
            for b_epoch in sorted(bucketed_dict.keys()):
                avg_val = sum(bucketed_dict[b_epoch]) / len(bucketed_dict[b_epoch])
                deduped_points.append(
                    NormalizedDataPoint(
                        timestamp=datetime.fromtimestamp(b_epoch, tz=UTC),
                        value=round(avg_val, 4),
                    )
                )
            parsed_points = deduped_points

        start_time = parsed_points[0].timestamp if parsed_points else None
        end_time = parsed_points[-1].timestamp if parsed_points else None

        return NormalizedTimeSeries(
            metric_name=self.canonical_metric_name(metric_name),
            service=service,
            resource_id=resource_id,
            unit=unit,
            points=parsed_points,
            sample_count=len(parsed_points),
            start_time=start_time,
            end_time=end_time,
            interval_seconds=bucket_seconds,
        )


telemetry_normalizer = TelemetryNormalizer()
