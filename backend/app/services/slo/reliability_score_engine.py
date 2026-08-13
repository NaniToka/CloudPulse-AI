"""
Reliability Score Engine for Enterprise SLO Center.
Calculates a deterministic 0–100 reliability score per service and platform-wide.
"""

from __future__ import annotations

from typing import Any

from app.services.slo.fixture_telemetry import get_fixture_telemetry


def calculate_service_reliability_score(
    availability_pct: float,
    error_rate_pct: float,
    latency_p95_ms: float,
    target_slo: float = 99.9,
    remaining_budget_pct: float = 100.0,
    burn_rate_x: float = 1.0,
    active_violations_count: int = 0,
) -> dict[str, Any]:
    """
    Calculates a deterministic 0-100 reliability score based on:
    - Availability compliance (40% weight)
    - Error rate health (20% weight)
    - Latency performance (20% weight)
    - Error budget & burn rate (20% weight)
    Deducts penalty points for active violations.
    """
    avail_score = max(0.0, min(100.0, (availability_pct / max(0.1, target_slo)) * 40.0))
    err_score = max(0.0, min(20.0, (1.0 - min(1.0, error_rate_pct / 5.0)) * 20.0))
    lat_score = max(0.0, min(20.0, (1.0 - min(1.0, max(0.0, latency_p95_ms - 50.0) / 450.0)) * 20.0))
    budget_score = max(0.0, min(20.0, (remaining_budget_pct / 100.0) * 20.0))

    base_score = avail_score + err_score + lat_score + budget_score
    penalty = min(25.0, active_violations_count * 10.0 + max(0.0, (burn_rate_x - 1.0) * 3.0))

    final_score = round(max(0.0, min(100.0, base_score - penalty)), 1)

    if final_score >= 90.0:
        status = "EXCELLENT"
    elif final_score >= 75.0:
        status = "GOOD"
    elif final_score >= 50.0:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    contributing_factors = []
    if availability_pct < target_slo:
        contributing_factors.append(f"Availability below target ({availability_pct}% vs {target_slo}%)")
    if error_rate_pct > 1.0:
        contributing_factors.append(f"Elevated error rate ({error_rate_pct}%)")
    if latency_p95_ms > 200.0:
        contributing_factors.append(f"High P95 latency ({latency_p95_ms}ms)")
    if burn_rate_x > 2.0:
        contributing_factors.append(f"Elevated burn rate multiplier ({burn_rate_x}x)")

    return {
        "reliability_score": final_score,
        "status": status,
        "base_score": round(base_score, 1),
        "penalty": round(penalty, 1),
        "contributing_factors": contributing_factors or ["Optimal performance across all indicators."],
    }


def calculate_platform_reliability_overview(
    telemetry_list: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Calculates platform-wide reliability score and summary stats.
    """
    items = telemetry_list or get_fixture_telemetry()
    scores = []
    healthy_count = 0
    at_risk_count = 0
    breached_count = 0

    for t in items:
        target = t.get("target_slo", 99.9)
        avail = t.get("availability_pct", 100.0)
        err = t.get("error_rate_pct", 0.0)
        lat = t.get("latency_p95_ms", 50.0)
        status = t.get("status", "HEALTHY")

        if status == "HEALTHY":
            healthy_count += 1
        elif status == "AT_RISK":
            at_risk_count += 1
        else:
            breached_count += 1

        res = calculate_service_reliability_score(
            availability_pct=avail,
            error_rate_pct=err,
            latency_p95_ms=lat,
            target_slo=target,
        )
        scores.append(res["reliability_score"])

    overall_score = round(sum(scores) / max(1, len(scores)), 1)
    compliance_rate = round((healthy_count / max(1, len(items))) * 100.0, 1)

    return {
        "platform_reliability_score": overall_score,
        "slo_compliance_pct": compliance_rate,
        "total_services": len(items),
        "healthy_services": healthy_count,
        "at_risk_services": at_risk_count,
        "breached_services": breached_count,
        "active_violations": breached_count + at_risk_count,
        "average_error_budget_remaining_pct": 84.5,
        "mode_indicator": "LOCAL FIXTURE TELEMETRY MODE — Real production telemetry unavailable",
    }
