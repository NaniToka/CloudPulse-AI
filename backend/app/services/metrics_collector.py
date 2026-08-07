"""
Prometheus Metrics Registry and Exporter for CloudPulse AI.
Emits standard Prometheus text format without external heavy dependencies.
"""

from __future__ import annotations

import time
from typing import ClassVar


class PrometheusMetricsCollector:
    """Collects and renders application runtime metrics in Prometheus exposition format."""

    _instance: ClassVar[PrometheusMetricsCollector | None] = None

    def __init__(self) -> None:
        self.request_counts: dict[str, int] = {}
        self.request_latencies: dict[str, list[float]] = {}
        self.status_counts: dict[str, int] = {}
        self.start_time = time.time()

    @classmethod
    def get_instance(cls) -> PrometheusMetricsCollector:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def record_request(self, method: str, path: str, status_code: int, duration_sec: float) -> None:
        # Group path prefixes to avoid unbounded cardinality
        norm_path = path.split("?")[0]
        if norm_path.startswith("/api/v1/"):
            parts = norm_path.split("/")
            if len(parts) > 4:
                norm_path = f"/api/v1/{parts[3]}/..."

        key = f"{method}:{norm_path}"
        self.request_counts[key] = self.request_counts.get(key, 0) + 1

        status_key = f"{status_code}"
        self.status_counts[status_key] = self.status_counts.get(status_key, 0) + 1

        times = self.request_latencies.get(key, [])
        times.append(duration_sec)
        if len(times) > 100:
            times.pop(0)
        self.request_latencies[key] = times

    def render_prometheus(self) -> str:
        lines = [
            "# HELP cloudpulse_http_requests_total Total number of HTTP requests processed.",
            "# TYPE cloudpulse_http_requests_total counter",
        ]

        total_reqs = sum(self.request_counts.values())
        lines.append(f"cloudpulse_http_requests_total {total_reqs}")

        for key, count in self.request_counts.items():
            method, path = key.split(":", 1)
            lines.append(
                f'cloudpulse_http_requests_by_endpoint{{method="{method}",path="{path}"}} {count}'
            )

        lines.extend(
            [
                "",
                "# HELP cloudpulse_http_requests_by_status Total number of HTTP requests grouped by status code.",
                "# TYPE cloudpulse_http_requests_by_status counter",
            ]
        )
        for code, count in self.status_counts.items():
            lines.append(f'cloudpulse_http_requests_by_status{{status="{code}"}} {count}')

        lines.extend(
            [
                "",
                "# HELP cloudpulse_http_request_duration_seconds Average latency in seconds.",
                "# TYPE cloudpulse_http_request_duration_seconds gauge",
            ]
        )
        for key, times in self.request_latencies.items():
            if times:
                avg = sum(times) / len(times)
                method, path = key.split(":", 1)
                lines.append(
                    f'cloudpulse_http_request_duration_seconds{{method="{method}",path="{path}"}} {avg:.6f}'
                )

        lines.extend(
            [
                "",
                "# HELP cloudpulse_app_uptime_seconds Application uptime in seconds.",
                "# TYPE cloudpulse_app_uptime_seconds gauge",
                f"cloudpulse_app_uptime_seconds {time.time() - self.start_time:.1f}",
                "",
                "# HELP cloudpulse_healthy Indicator of overall system health (1=healthy, 0=unhealthy).",
                "# TYPE cloudpulse_healthy gauge",
                "cloudpulse_healthy 1",
            ]
        )

        return "\n".join(lines) + "\n"


metrics_collector = PrometheusMetricsCollector.get_instance()
