"""
SLO Evaluation Engine for Enterprise SLO Center.
Evaluates current compliance vs target SLO and status (HEALTHY, AT_RISK, BREACHED).
"""

from __future__ import annotations

from typing import Any


def evaluate_slo_compliance(
    indicator_type: str,
    target_slo: float,
    current_sli: float,
    target_threshold_ms: float | None = None,
) -> dict[str, Any]:
    """
    Evaluates SLO compliance against target threshold.
    Returns compliance_pct, status, and target vs actual values.
    """
    ind = indicator_type.lower()
    status = "HEALTHY"
    compliance_pct = 100.0

    if ind == "availability":
        # e.g., target = 99.9%, current_sli = 99.98%
        compliance_pct = round(min(100.0, max(0.0, (current_sli / max(0.01, target_slo)) * 100.0)), 2)
        if current_sli < target_slo:
            status = "BREACHED"
        elif current_sli < (target_slo + 0.05):
            status = "AT_RISK"
        else:
            status = "HEALTHY"

    elif ind == "error_rate":
        # e.g., target = < 1.0% error rate, current_sli = 3.2%
        if current_sli > target_slo:
            status = "BREACHED"
            compliance_pct = round(max(0.0, 100.0 - ((current_sli - target_slo) * 10.0)), 2)
        elif current_sli > (target_slo * 0.8):
            status = "AT_RISK"
            compliance_pct = round(100.0 - ((current_sli / target_slo) * 10.0), 2)
        else:
            status = "HEALTHY"
            compliance_pct = 100.0

    elif ind == "latency":
        # e.g., target = 99.9% under 500ms
        threshold = target_threshold_ms or 500.0
        if current_sli > threshold:
            status = "BREACHED"
            compliance_pct = round(max(0.0, (threshold / current_sli) * 100.0), 2)
        elif current_sli > (threshold * 0.8):
            status = "AT_RISK"
            compliance_pct = round(min(100.0, (threshold / current_sli) * 100.0), 2)
        else:
            status = "HEALTHY"
            compliance_pct = 100.0

    else:
        status = "HEALTHY" if current_sli >= target_slo else "BREACHED"
        compliance_pct = round(min(100.0, max(0.0, (current_sli / max(0.01, target_slo)) * 100.0)), 2)

    return {
        "indicator_type": indicator_type,
        "target_slo": target_slo,
        "current_sli": current_sli,
        "compliance_pct": compliance_pct,
        "status": status,
        "target_threshold_ms": target_threshold_ms,
    }
