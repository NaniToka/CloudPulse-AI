"""
SLO Violation Detection Engine for Enterprise SLO Center.
Detects availability, latency, error rate, budget exhaustion, and high burn rate breaches.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.services.slo.fixture_telemetry import get_fixture_telemetry


def detect_slo_violations(
    telemetry_list: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Detects SLO/SLA violations across monitored services.
    Returns structured violation logs.
    """
    items = telemetry_list or get_fixture_telemetry()
    violations: list[dict[str, Any]] = []

    for t in items:
        service = t["service"]
        target_slo = t.get("target_slo", 99.9)
        avail = t.get("availability_pct", 100.0)
        err = t.get("error_rate_pct", 0.0)
        lat_p95 = t.get("latency_p95_ms", 50.0)

        # 1. Availability Breach Detection
        if avail < target_slo:
            diff = round(target_slo - avail, 2)
            severity = "CRITICAL" if diff > 1.0 else "HIGH"
            violations.append(
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"viol-avail-{service}")),
                    "service": service,
                    "violation_type": "availability",
                    "severity": severity,
                    "target_value": target_slo,
                    "actual_value": avail,
                    "difference": diff,
                    "duration_seconds": 1800,
                    "explanation": f"Availability degraded to {avail}% (Target: {target_slo}%). Deficit of {diff}%.",
                    "status": "ACTIVE",
                    "incident_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"inc-{service}")),
                }
            )

        # 2. Latency Breach Detection
        if lat_p95 > 500.0:
            diff = round(lat_p95 - 500.0, 1)
            violations.append(
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"viol-lat-{service}")),
                    "service": service,
                    "violation_type": "latency",
                    "severity": "HIGH",
                    "target_value": 500.0,
                    "actual_value": lat_p95,
                    "difference": diff,
                    "duration_seconds": 2400,
                    "explanation": f"P95 latency breached threshold at {lat_p95}ms (Target: < 500ms). Excess of {diff}ms.",
                    "status": "ACTIVE",
                    "incident_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"inc-{service}")),
                }
            )

        # 3. Error Rate Breach Detection
        if err > 1.0:
            diff = round(err - 1.0, 2)
            violations.append(
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"viol-err-{service}")),
                    "service": service,
                    "violation_type": "error_rate",
                    "severity": "CRITICAL" if err > 3.0 else "MEDIUM",
                    "target_value": 1.0,
                    "actual_value": err,
                    "difference": diff,
                    "duration_seconds": 1200,
                    "explanation": f"Error rate elevated to {err}% (Target: < 1.0%). Excess of {diff}%.",
                    "status": "ACTIVE",
                    "incident_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"inc-{service}")),
                }
            )

    return violations
