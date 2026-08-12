"""
Cost Analysis Engine — calculations, aggregations, anomaly detection, forecasting,
and budget evaluation for enterprise cloud spending.
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime
from typing import Any


def calculate_efficiency_score(monthly_cost: float, potential_savings: float) -> int:
    """
    Calculate cloud efficiency score (0 - 100).
    Higher score indicates higher efficiency (lower wasted/idle spending ratio).
    """
    if monthly_cost <= 0:
        return 100
    waste_ratio = min(1.0, max(0.0, potential_savings / monthly_cost))
    return max(0, min(100, int((1.0 - waste_ratio) * 100)))


def group_costs_by_provider(costs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group list of resource cost dicts by cloud provider."""
    total_cost = sum(c.get("cost", 0.0) for c in costs)
    providers: dict[str, dict[str, Any]] = {}

    for c in costs:
        raw_p = str(c.get("provider", "other")).lower()
        if "aws" in raw_p:
            p_name = "AWS"
        elif "azure" in raw_p:
            p_name = "Azure"
        elif "gcp" in raw_p or "google" in raw_p:
            p_name = "GCP"
        elif "k8s" in raw_p or "kubernetes" in raw_p:
            p_name = "Kubernetes"
        else:
            p_name = raw_p.upper()

        if p_name not in providers:
            providers[p_name] = {"provider": p_name, "cost": 0.0, "resource_count": 0}
        providers[p_name]["cost"] += c.get("cost", 0.0)
        providers[p_name]["resource_count"] += 1

    result = []
    for p_name, data in sorted(providers.items(), key=lambda x: x[1]["cost"], reverse=True):
        pct = (data["cost"] / total_cost * 100.0) if total_cost > 0 else 0.0
        result.append(
            {
                "provider": p_name,
                "cost": round(data["cost"], 2),
                "percentage": round(pct, 1),
                "resource_count": data["resource_count"],
            }
        )
    return result


def group_costs_by_service(costs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group list of resource cost dicts by service name."""
    total_cost = sum(c.get("cost", 0.0) for c in costs)
    services: dict[str, dict[str, Any]] = {}

    for c in costs:
        svc = c.get("service", "Other")
        if svc not in services:
            services[svc] = {"service": svc, "cost": 0.0, "resource_count": 0}
        services[svc]["cost"] += c.get("cost", 0.0)
        services[svc]["resource_count"] += 1

    result = []
    for svc, data in sorted(services.items(), key=lambda x: x[1]["cost"], reverse=True):
        pct = (data["cost"] / total_cost * 100.0) if total_cost > 0 else 0.0
        result.append(
            {
                "service": svc,
                "cost": round(data["cost"], 2),
                "percentage": round(pct, 1),
                "resource_count": data["resource_count"],
            }
        )
    return result


def group_costs_by_region(costs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group list of resource cost dicts by region."""
    total_cost = sum(c.get("cost", 0.0) for c in costs)
    regions: dict[str, dict[str, Any]] = {}

    for c in costs:
        reg = c.get("region", "global")
        if reg not in regions:
            regions[reg] = {"region": reg, "cost": 0.0, "resource_count": 0}
        regions[reg]["cost"] += c.get("cost", 0.0)
        regions[reg]["resource_count"] += 1

    result = []
    for reg, data in sorted(regions.items(), key=lambda x: x[1]["cost"], reverse=True):
        pct = (data["cost"] / total_cost * 100.0) if total_cost > 0 else 0.0
        result.append(
            {
                "region": reg,
                "cost": round(data["cost"], 2),
                "percentage": round(pct, 1),
                "resource_count": data["resource_count"],
            }
        )
    return result


def detect_cost_anomalies(costs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Detect spending anomalies deterministically using statistical variance & baseline checks.
    Returns anomaly objects with severity, anomaly_score, expected vs actual cost, and explanations.
    """
    anomalies = []
    if not costs:
        return anomalies

    avg_cost = sum(c.get("cost", 0.0) for c in costs) / len(costs)

    for c in costs:
        cost_val = c.get("cost", 0.0)
        status_val = c.get("status", "active")
        res_name = c.get("resource_name", "unknown")
        service = c.get("service", "General")
        provider = c.get("provider", "gcp").upper()

        # Trigger anomaly condition: idle resource with > $1000 cost OR cost > 1.8x average
        is_idle_waste = status_val == "idle" and cost_val > 500.0
        is_overprovisioned = status_val == "overprovisioned"
        is_spike = cost_val > (avg_cost * 1.8) and cost_val > 3000.0

        if is_idle_waste or is_overprovisioned or is_spike:
            baseline = round(cost_val * 0.4, 2) if is_idle_waste else round(avg_cost, 2)
            diff = round(cost_val - baseline, 2)
            ratio = cost_val / max(1.0, baseline)
            score = round(min(10.0, max(1.0, math.log2(ratio + 1) * 3.2)), 1)

            if score >= 8.0:
                severity = "CRITICAL"
            elif score >= 6.0:
                severity = "HIGH"
            elif score >= 4.0:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            if is_idle_waste:
                explanation = f"Resource '{res_name}' is tagged as IDLE but incurring ${cost_val:.2f}/mo waste."
            elif is_overprovisioned:
                explanation = f"Resource '{res_name}' is overprovisioned for current workload traffic."
            else:
                explanation = f"Spending spike detected on '{res_name}' ({ratio:.1f}x baseline average)."

            now_iso = datetime.now(UTC).strftime("%Y-%m-%d")

            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "anomaly_score": score,
                    "severity": severity,
                    "detected_date": now_iso,
                    "provider": provider,
                    "service": service,
                    "resource": res_name,
                    "expected_cost": baseline,
                    "actual_cost": round(cost_val, 2),
                    "difference": diff,
                    "explanation": explanation,
                }
            )

    anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
    return anomalies


def calculate_cost_forecast(
    daily_trend: list[dict[str, Any]], monthly_cost: float
) -> dict[str, Any]:
    """
    Calculate deterministic 7-day, 30-day, and month-end forecast based on rolling daily spend regression.
    """
    if not daily_trend:
        return {
            "forecast_7_day": round(monthly_cost * 0.25, 2),
            "forecast_30_day": round(monthly_cost * 1.05, 2),
            "projected_month_end": round(monthly_cost * 1.08, 2),
            "confidence": 0.85,
            "historical_basis": "Insufficient historical points — baseline monthly extrapolation fallback",
            "trend_direction": "stable",
        }

    daily_costs = [d.get("cost", 0.0) for d in daily_trend]
    avg_daily = sum(daily_costs) / len(daily_costs) if daily_costs else (monthly_cost / 30.0)

    # Linear slope trend calculation
    n = len(daily_costs)
    if n >= 2:
        x_avg = (n - 1) / 2.0
        y_avg = avg_daily
        num = sum((i - x_avg) * (y - y_avg) for i, y in enumerate(daily_costs))
        den = sum((i - x_avg) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0.0
    else:
        slope = 0.0

    trend_dir = "increasing" if slope > 0.5 else ("decreasing" if slope < -0.5 else "stable")
    confidence = min(0.98, max(0.65, round(0.70 + (n / 100.0), 2)))

    daily_projected = max(10.0, avg_daily + (slope * 5.0))
    forecast_7 = round(daily_projected * 7.0, 2)
    forecast_30 = round(daily_projected * 30.0, 2)
    projected_month_end = round(monthly_cost + (daily_projected * 5.0), 2)

    return {
        "forecast_7_day": forecast_7,
        "forecast_30_day": forecast_30,
        "projected_month_end": projected_month_end,
        "confidence": confidence,
        "historical_basis": f"Calculated from {n} daily cost records with linear trend slope coefficient {slope:.2f}",
        "trend_direction": trend_dir,
    }


def evaluate_budget(
    budget_amount: float, current_spend: float, projected_spend: float
) -> dict[str, Any]:
    """
    Evaluate budget utilization, threshold status (50%, 75%, 90%, 100%), and remaining allocation.
    """
    if budget_amount <= 0:
        return {
            "budget": 0.0,
            "current_spend": round(current_spend, 2),
            "utilization_pct": 0.0,
            "projected_spend": round(projected_spend, 2),
            "remaining": 0.0,
            "threshold_status": "EXCEEDED_100",
            "thresholds_reached": [50, 75, 90, 100],
        }

    utilization_pct = round((current_spend / budget_amount) * 100.0, 1)
    remaining = round(max(0.0, budget_amount - current_spend), 2)

    thresholds_reached = []
    for t in [50, 75, 90, 100]:
        if utilization_pct >= t:
            thresholds_reached.append(t)

    if utilization_pct >= 100.0:
        status_str = "EXCEEDED_100"
    elif utilization_pct >= 90.0:
        status_str = "CRITICAL_90"
    elif utilization_pct >= 75.0:
        status_str = "WARNING_75"
    elif utilization_pct >= 50.0:
        status_str = "WARNING_50"
    else:
        status_str = "NORMAL"

    return {
        "budget": round(budget_amount, 2),
        "current_spend": round(current_spend, 2),
        "utilization_pct": utilization_pct,
        "projected_spend": round(projected_spend, 2),
        "remaining": remaining,
        "threshold_status": status_str,
        "thresholds_reached": thresholds_reached,
    }


def calculate_savings_summary(
    recommendations: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Calculate total monthly savings, annual savings (monthly * 12), and active opportunity count.
    """
    active_recs = [r for r in recommendations if r.get("status") in ("active", "OPEN")]
    monthly_savings = sum(r.get("estimated_savings", 0.0) for r in active_recs)
    annual_savings = round(monthly_savings * 12.0, 2)

    return {
        "total_monthly_savings": round(monthly_savings, 2),
        "total_annual_savings": annual_savings,
        "opportunity_count": len(active_recs),
    }
