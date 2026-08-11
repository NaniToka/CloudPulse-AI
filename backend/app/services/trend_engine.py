"""
Deterministic Trend & Drift Analysis Engine.

Calculates:
- First-order Ordinary Least Squares (OLS) Linear Regression slope
- Second-order acceleration/deceleration curve fitting
- Coefficient of Determination (R²) for noise filtering
- Trend classification: INCREASING, DECREASING, STABLE, ACCELERATING_DEGRADATION, RECOVERY
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import structlog

from app.services.telemetry_normalizer import NormalizedTimeSeries

log = structlog.get_logger(__name__)


@dataclass
class TrendAnalysisResult:
    """Mathematical trend evaluation container."""

    metric_name: str
    trend: str  # "INCREASING", "DECREASING", "STABLE", "ACCELERATING_DEGRADATION", "RECOVERY"
    trend_strength: float  # 0.0 to 1.0
    rate_of_change: float  # slope (delta per step)
    r_squared: float  # goodness of fit
    slope: float
    intercept: float
    is_statistically_significant: bool
    explanation: str


class TrendEngine:
    """Evaluates mathematical trend velocity and directional drift."""

    def analyze_trend(
        self,
        values: Sequence[float] | NormalizedTimeSeries,
        metric_name: str = "metric",
        min_samples: int = 4,
    ) -> TrendAnalysisResult:
        """
        Calculates linear regression slope, R², and trend classification.
        """
        vals: list[float] = (
            values.values if isinstance(values, NormalizedTimeSeries) else [float(v) for v in values]
        )
        name = values.metric_name if isinstance(values, NormalizedTimeSeries) else metric_name

        n = len(vals)
        if n < min_samples:
            return TrendAnalysisResult(
                metric_name=name,
                trend="STABLE",
                trend_strength=0.0,
                rate_of_change=0.0,
                r_squared=0.0,
                slope=0.0,
                intercept=vals[0] if vals else 0.0,
                is_statistically_significant=False,
                explanation=f"Insufficient samples ({n}/{min_samples}) for reliable trend estimation.",
            )

        # OLS Linear Regression
        x_vals = list(range(n))
        x_mean = (n - 1) / 2.0
        y_mean = sum(vals) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, vals, strict=False))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)

        if denominator < 1e-9:
            slope = 0.0
            intercept = y_mean
            r_squared = 1.0
        else:
            slope = numerator / denominator
            intercept = y_mean - slope * x_mean

            # Total Sum of Squares and Residual Sum of Squares
            ss_tot = sum((y - y_mean) ** 2 for y in vals)
            ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(x_vals, vals, strict=False))
            r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-9 else 1.0
            r_squared = max(0.0, min(1.0, r_squared))

        # Check for acceleration (second derivative)
        if n >= 6:
            mid = n // 2
            first_half_slope = (vals[mid] - vals[0]) / max(1, mid)
            second_half_slope = (vals[-1] - vals[mid]) / max(1, n - 1 - mid)
            is_accelerating = second_half_slope > (first_half_slope * 1.4) and second_half_slope > 0.5
        else:
            is_accelerating = False

        # Relative slope normalized against mean
        rel_slope = (slope / max(1.0, abs(y_mean))) if abs(y_mean) > 1e-4 else slope

        # Trend classification
        if is_accelerating and rel_slope > 0.01:
            trend = "ACCELERATING_DEGRADATION"
            trend_strength = round(min(0.99, max(0.60, r_squared * 0.95)), 2)
            explanation = f"{name} shows accelerating degradation with steepening slope ({slope:+.3f}/step)."
        elif rel_slope > 0.015 and r_squared >= 0.40:
            trend = "INCREASING"
            trend_strength = round(min(0.99, max(0.40, r_squared * (1.0 + min(1.0, abs(rel_slope) * 5)))), 2)
            explanation = f"{name} exhibits a steady upward trend (+{slope:.3f}/step, R²={r_squared:.2f})."
        elif rel_slope < -0.015 and r_squared >= 0.40:
            if y_mean < vals[0] * 0.75:
                trend = "RECOVERY"
                explanation = f"{name} is demonstrating rapid recovery toward baseline (-{abs(slope):.3f}/step)."
            else:
                trend = "DECREASING"
                explanation = f"{name} exhibits a downward trend ({slope:.3f}/step, R²={r_squared:.2f})."
            trend_strength = round(min(0.99, max(0.40, r_squared)), 2)
        else:
            trend = "STABLE"
            trend_strength = round(min(0.30, max(0.05, 1.0 - r_squared if abs(rel_slope) < 0.01 else 0.2)), 2)
            explanation = f"{name} baseline remains stable with no significant directional drift."

        return TrendAnalysisResult(
            metric_name=name,
            trend=trend,
            trend_strength=trend_strength,
            rate_of_change=round(slope, 4),
            r_squared=round(r_squared, 4),
            slope=round(slope, 4),
            intercept=round(intercept, 4),
            is_statistically_significant=r_squared >= 0.40 and trend != "STABLE",
            explanation=explanation,
        )


trend_engine = TrendEngine()
