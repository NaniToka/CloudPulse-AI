"""
SLO Reliability Forecasting Engine for Enterprise SLO Center.
Calculates projected month-end SLO, projected error budget consumption, and exhaustion date.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


def calculate_slo_forecast(
    target_slo: float,
    current_availability_pct: float,
    remaining_budget_pct: float,
    burn_rate_x: float,
    days_elapsed: int = 14,
    total_days: int = 30,
) -> dict[str, Any]:
    """
    Calculates deterministic reliability forecast for month-end SLO and budget exhaustion.
    """
    days_remaining = max(1, total_days - days_elapsed)
    daily_budget_burn_pct = round((100.0 - remaining_budget_pct) / max(1, days_elapsed), 2)

    projected_budget_consumed_pct = round(
        min(100.0, (100.0 - remaining_budget_pct) + (daily_budget_burn_pct * days_remaining * burn_rate_x)), 1
    )
    projected_remaining_budget_pct = round(max(0.0, 100.0 - projected_budget_consumed_pct), 1)

    projected_slo_pct = round(
        max(90.0, min(100.0, current_availability_pct - (0.01 * (burn_rate_x - 1.0) * (days_remaining / 30.0)))), 2
    )

    now = datetime.now(UTC)
    if burn_rate_x > 1.0 and remaining_budget_pct < 100.0:
        days_to_exhaustion = max(1, int(remaining_budget_pct / max(0.1, daily_budget_burn_pct * burn_rate_x)))
        exhaustion_date = (now + timedelta(days=days_to_exhaustion)).strftime("%Y-%m-%d")
    else:
        days_to_exhaustion = 999
        exhaustion_date = "N/A (Budget Healthy)"

    is_compliant_projected = projected_slo_pct >= target_slo

    return {
        "target_slo": target_slo,
        "current_availability_pct": current_availability_pct,
        "projected_month_end_slo_pct": projected_slo_pct,
        "projected_budget_consumed_pct": projected_budget_consumed_pct,
        "projected_remaining_budget_pct": projected_remaining_budget_pct,
        "days_to_exhaustion": days_to_exhaustion,
        "projected_exhaustion_date": exhaustion_date,
        "is_compliant_projected": is_compliant_projected,
        "confidence_pct": 94.5 if days_elapsed >= 7 else 75.0,
    }
