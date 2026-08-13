"""
Burn Rate Intelligence Engine for Enterprise SLO Center.
Calculates multi-window burn rates (1h, 6h, 24h, 7d) and severity classification.
"""

from __future__ import annotations

from typing import Any


def calculate_burn_rate(
    target_slo: float,
    observed_error_rate_pct: float,
    window_hours: int = 1,
) -> dict[str, Any]:
    """
    Calculates burn rate multiplier = observed_error_rate / allowed_error_rate.
    Example:
      Target SLO = 99.9% -> Allowed error rate = 0.1%
      Observed error rate = 0.5%
      Burn rate = 0.5 / 0.1 = 5.0x
    Severity Classification:
      - <= 1.0x: NORMAL
      - 1.0x - 3.0x: ELEVATED
      - 3.0x - 10.0x: HIGH
      - > 10.0x: CRITICAL
    """
    allowed_failure_rate = max(0.0001, (100.0 - target_slo) / 100.0)
    observed_failure_rate = max(0.0, observed_error_rate_pct / 100.0)

    burn_rate_x = round(observed_failure_rate / allowed_failure_rate, 2)

    if burn_rate_x <= 1.0:
        severity = "NORMAL"
        explanation = f"Normal burn rate ({burn_rate_x}x). Error budget consumption is within expected parameters."
    elif burn_rate_x <= 3.0:
        severity = "ELEVATED"
        explanation = f"Elevated burn rate ({burn_rate_x}x). Error budget is consuming {burn_rate_x}x faster than allowed over {window_hours}h window."
    elif burn_rate_x <= 10.0:
        severity = "HIGH"
        explanation = f"High burn rate ({burn_rate_x}x). Error budget will be exhausted rapidly if unaddressed over {window_hours}h window."
    else:
        severity = "CRITICAL"
        explanation = f"CRITICAL burn rate ({burn_rate_x}x). Rapid error budget depletion detected over {window_hours}h window!"

    return {
        "burn_rate_x": burn_rate_x,
        "severity": severity,
        "window_hours": window_hours,
        "observed_failure_rate": observed_failure_rate,
        "allowed_failure_rate": allowed_failure_rate,
        "explanation": explanation,
    }
