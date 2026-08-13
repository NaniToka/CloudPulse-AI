"""
Error Budget Engine for Enterprise SLO Center.
Calculates total allowed failure budget, consumed error budget, remaining budget percentage,
and status over rolling time windows (e.g. 30 days = 2,592,000s).
"""

from __future__ import annotations

from typing import Any


def calculate_error_budget(
    target_slo: float,
    current_availability_pct: float,
    window_days: int = 30,
) -> dict[str, Any]:
    """
    Calculates deterministic error budget metrics.
    For a 30-day window (2,592,000 seconds):
    - Target SLO = 99.9% -> Allowed downtime = 0.1% = 2,592 seconds.
    - If current availability = 99.98% -> Consumed downtime = 0.02% = 518.4 seconds.
    - Remaining budget = 2,592 - 518.4 = 2,073.6s (80.0% remaining).
    """
    total_window_sec = float(window_days * 86400)
    allowed_unreliability = max(0.00001, (100.0 - target_slo) / 100.0)
    total_budget_sec = round(total_window_sec * allowed_unreliability, 1)

    actual_unreliability = max(0.0, (100.0 - current_availability_pct) / 100.0)
    consumed_budget_sec = round(total_window_sec * actual_unreliability, 1)

    remaining_budget_sec = max(0.0, total_budget_sec - consumed_budget_sec)
    remaining_budget_pct = round(max(0.0, min(100.0, (remaining_budget_sec / max(0.1, total_budget_sec)) * 100.0)), 1)
    consumed_budget_pct = round(max(0.0, min(100.0, 100.0 - remaining_budget_pct)), 1)

    burn_rate_multiplier = round(actual_unreliability / max(0.000001, allowed_unreliability), 2)

    if remaining_budget_pct > 50.0:
        status = "HEALTHY"
    elif remaining_budget_pct > 15.0:
        status = "WARNING"
    else:
        status = "EXHAUSTED"

    return {
        "target_slo": target_slo,
        "window_days": window_days,
        "total_budget_sec": total_budget_sec,
        "consumed_budget_sec": consumed_budget_sec,
        "remaining_budget_sec": remaining_budget_sec,
        "consumed_budget_pct": consumed_budget_pct,
        "remaining_budget_pct": remaining_budget_pct,
        "burn_rate_multiplier": burn_rate_multiplier,
        "status": status,
    }
