"""
Cost Analysis Engine — calculations and aggregations for cloud spending.
"""

from __future__ import annotations

from typing import Any


def calculate_efficiency_score(monthly_cost: float, potential_savings: float) -> int:
    """
    Calculate cloud efficiency score (0 - 100).
    Higher score indicates higher efficiency (lower wasted/idle spending ratio).
    """
    if monthly_cost <= 0:
        return 100
    waste_ratio = min(1.0, max(0.0, potential_savings / monthly_cost))
    # Scale: 0% waste = 100 score, 50% waste = 50 score
    return max(0, min(100, int((1.0 - waste_ratio) * 100)))


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
