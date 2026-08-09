"""
Metric Processor for Unified Telemetry Platform.
Detects statistical deviations, metric spikes (e.g. 300% surge), and threshold violations.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class MetricProcessor:
    """Evaluates metrics against baseline thresholds and detects anomalies."""

    def process(self, collected_metric: dict[str, Any]) -> dict[str, Any]:
        val = collected_metric["value"]
        m_name = collected_metric["metric_name"]
        res_id = collected_metric["resource_id"]

        is_anomaly = False
        deviation = 1.0
        severity = "INFO"
        reason = "Normal telemetry signal"

        if "cpu" in m_name and val > 85.0:
            is_anomaly = True
            deviation = round(val / 25.0, 2)  # relative to 25% baseline
            severity = "CRITICAL" if val > 95 else "WARN"
            reason = f"CPU usage increased {int(deviation * 100)}% compared to normal baseline pattern ({val:.1f}%)"
        elif "latency" in m_name and val > 200.0:
            is_anomaly = True
            deviation = round(val / 20.0, 2)  # relative to 20ms baseline
            severity = "CRITICAL" if val > 800 else "WARN"
            reason = f"Database latency anomaly detected: latency reached {val:.1f}ms (>200ms threshold)"
        elif "mem" in m_name and val > 90.0:
            is_anomaly = True
            deviation = round(val / 40.0, 2)
            severity = "CRITICAL"
            reason = f"Memory usage saturated at {val:.1f}% with risk of OOMKilled eviction"

        event = None
        if is_anomaly:
            ts = collected_metric["timestamp"]
            ts_iso = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
            raw_payload_copy = {**collected_metric, "timestamp": ts_iso}

            event = {
                "source": "metric_processor",
                "event_type": "metric_anomaly",
                "severity": severity,
                "timestamp": ts,
                "metadata_": {
                    "resource_id": res_id,
                    "metric_name": m_name,
                    "value": val,
                    "deviation_factor": deviation,
                    "reason": reason,
                },
                "raw_payload": raw_payload_copy,
            }

        return {
            "record": {
                "resource_id": res_id,
                "metric_name": m_name,
                "value": val,
                "unit": collected_metric["unit"],
                "timestamp": collected_metric["timestamp"],
            },
            "is_anomaly": is_anomaly,
            "anomaly_event": event,
            "reason": reason,
            "deviation_factor": deviation,
        }


metric_processor = MetricProcessor()
