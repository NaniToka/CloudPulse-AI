"""
Deterministic Capacity Risk & Resource Exhaustion Prediction Engine.

Predicts:
- Linear and exponential resource capacity exhaustion
- Memory leaks & Kubernetes OOMKilled risks
- CPU saturation and thread pool starvation
- Disk storage exhaustion
- Database connection pool saturation
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import structlog

from app.services.telemetry_normalizer import NormalizedTimeSeries
from app.services.trend_engine import TrendEngine, trend_engine

log = structlog.get_logger(__name__)

CAPACITY_THRESHOLDS: dict[str, float] = {
    "cpu_utilization": 85.0,
    "memory_utilization": 85.0,
    "disk_utilization": 85.0,
    "db_connections_active": 85.0,
    "error_rate": 5.0,
    "latency_ms": 1000.0,
}


@dataclass
class CapacityRiskResult:
    """Resource capacity exhaustion assessment."""

    resource_name: str
    current_value: float
    capacity_limit: float
    exhaustion_threshold: float
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    is_exhaustion_imminent: bool
    estimated_time_to_threshold_minutes: float | None
    rate_of_growth_per_minute: float
    data_status: str  # "sufficient", "insufficient_data", "stable"
    summary: str
    recommended_mitigation: str


class CapacityRiskEngine:
    """Predicts time to capacity exhaustion and calculates risk scoring."""

    def __init__(self, trend_service: TrendEngine = trend_engine) -> None:
        self.trend = trend_service

    def evaluate_capacity_risk(
        self,
        values: Sequence[float] | NormalizedTimeSeries,
        resource_name: str = "memory_utilization",
        custom_threshold: float | None = None,
        capacity_limit: float = 100.0,
        sample_interval_minutes: float = 1.0,
    ) -> CapacityRiskResult:
        """
        Calculates deterministic resource exhaustion and estimated time to breach.
        """
        vals: list[float] = (
            values.values if isinstance(values, NormalizedTimeSeries) else [float(v) for v in values]
        )
        name = (
            values.metric_name if isinstance(values, NormalizedTimeSeries) else resource_name
        )

        n = len(vals)
        target_threshold = custom_threshold or CAPACITY_THRESHOLDS.get(name, 85.0)

        # Insufficient data check
        if n < 4:
            curr = vals[-1] if vals else 0.0
            return CapacityRiskResult(
                resource_name=name,
                current_value=curr,
                capacity_limit=capacity_limit,
                exhaustion_threshold=target_threshold,
                risk_score=0.10,
                risk_level="LOW",
                is_exhaustion_imminent=False,
                estimated_time_to_threshold_minutes=None,
                rate_of_growth_per_minute=0.0,
                data_status="insufficient_data",
                summary=f"Insufficient telemetry samples ({n}/4) to project {name} exhaustion.",
                recommended_mitigation="Collect additional historical telemetry samples.",
            )

        current_val = vals[-1]
        trend_res = self.trend.analyze_trend(vals, metric_name=name)
        slope = trend_res.slope  # delta per sample

        # If already breached threshold
        if current_val >= target_threshold:
            risk_score = 0.96 if current_val >= (target_threshold * 1.05) else 0.88
            risk_level = "CRITICAL" if risk_score >= 0.90 else "HIGH"
            return CapacityRiskResult(
                resource_name=name,
                current_value=round(current_val, 2),
                capacity_limit=capacity_limit,
                exhaustion_threshold=target_threshold,
                risk_score=round(risk_score, 2),
                risk_level=risk_level,
                is_exhaustion_imminent=True,
                estimated_time_to_threshold_minutes=0.0,
                rate_of_growth_per_minute=round(slope / max(0.1, sample_interval_minutes), 4),
                data_status="sufficient",
                summary=f"CRITICAL: {name} is at {current_val:.1f}%, currently breaching threshold of {target_threshold:.1f}%.",
                recommended_mitigation="Scale capacity or restart worker instances immediately.",
            )

        # Non-increasing slope or negative trend
        if slope <= 1e-4:
            risk_score = min(0.40, max(0.05, (current_val / target_threshold) * 0.40))
            return CapacityRiskResult(
                resource_name=name,
                current_value=round(current_val, 2),
                capacity_limit=capacity_limit,
                exhaustion_threshold=target_threshold,
                risk_score=round(risk_score, 2),
                risk_level="LOW",
                is_exhaustion_imminent=False,
                estimated_time_to_threshold_minutes=None,
                rate_of_growth_per_minute=round(slope / max(0.1, sample_interval_minutes), 4),
                data_status="stable",
                summary=f"{name} is operating nominally at {current_val:.1f}% with stable consumption.",
                recommended_mitigation="Maintain standard observability monitoring.",
            )

        # Upward Slope — Calculate Time to Threshold
        remaining_buffer = target_threshold - current_val
        steps_to_threshold = remaining_buffer / slope
        est_minutes = steps_to_threshold * sample_interval_minutes

        growth_rate_per_min = slope / max(0.1, sample_interval_minutes)

        # Risk level determination based on estimated time to breach and current saturation
        if est_minutes <= 30.0 or current_val >= 80.0:
            risk_level = "CRITICAL"
            risk_score = round(min(0.99, max(0.85, 0.95 - (est_minutes / 300.0))), 2)
            is_imminent = True
            summary = (
                f"Memory/Resource exhaustion risk: {name} will breach critical threshold "
                f"({target_threshold:.1f}%) in approximately {int(est_minutes)} minutes."
            )
            mitigation = f"Autoscale pod replicas or clear cached allocations for {name}."
        elif est_minutes <= 120.0 or current_val >= 70.0:
            risk_level = "HIGH"
            risk_score = round(min(0.84, max(0.60, 0.80 - (est_minutes / 600.0))), 2)
            is_imminent = True
            summary = (
                f"Elevated capacity growth: {name} projected to reach {target_threshold:.1f}% "
                f"in ~{int(est_minutes)} minutes (+{growth_rate_per_min:.2f}%/min)."
            )
            mitigation = "Review horizontal scaling policies and schedule capacity expansion."
        elif est_minutes <= 360.0:
            risk_level = "MEDIUM"
            risk_score = round(min(0.59, max(0.35, 0.50 - (est_minutes / 1200.0))), 2)
            is_imminent = False
            summary = f"Moderate upward consumption on {name}: breach estimated in {int(est_minutes / 60)} hours."
            mitigation = "Monitor trend slope during next maintenance cycle."
        else:
            risk_level = "LOW"
            risk_score = 0.25
            is_imminent = False
            summary = f"{name} consumption slope is mild with ample capacity buffer ({int(est_minutes / 60)}h+)."
            mitigation = "No immediate remediation needed."

        return CapacityRiskResult(
            resource_name=name,
            current_value=round(current_val, 2),
            capacity_limit=capacity_limit,
            exhaustion_threshold=target_threshold,
            risk_score=risk_score,
            risk_level=risk_level,
            is_exhaustion_imminent=is_imminent,
            estimated_time_to_threshold_minutes=round(est_minutes, 1),
            rate_of_growth_per_minute=round(growth_rate_per_min, 4),
            data_status="sufficient",
            summary=summary,
            recommended_mitigation=mitigation,
        )


capacity_risk_engine = CapacityRiskEngine()
