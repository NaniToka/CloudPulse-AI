"""
Deterministic Time-Series Forecasting Engine.

Implements:
- Holt's Double Exponential Smoothing (Level + Trend)
- Linear Drift with Dynamic Confidence Intervals (95% CI)
- Multi-Horizon Projections: 5m, 15m, 30m, 1h, 6h, 24h
- Strict Lower and Upper Uncertainty Bounds
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog

from app.services.baseline_engine import BaselineEngine, baseline_engine
from app.services.telemetry_normalizer import NormalizedTimeSeries

log = structlog.get_logger(__name__)

HORIZON_MINUTES_MAP: dict[str, int] = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "6h": 360,
    "24h": 1440,
}


@dataclass
class ForecastPoint:
    """Individual projected time-series point with uncertainty bounds."""

    horizon: str  # "5m", "15m", "30m", "1h", "6h", "24h"
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float  # 0.0 to 1.0


@dataclass
class ForecastResult:
    """Complete forecast response with historical and projected points."""

    metric_name: str
    service: str
    current_value: float
    forecast_points: list[ForecastPoint]
    historical_points: list[dict]
    model_used: str
    data_sufficiency: dict
    generated_at: datetime


class ForecastingEngine:
    """Generates multi-horizon deterministic forecasts with confidence envelopes."""

    def __init__(self, baseline_service: BaselineEngine = baseline_engine) -> None:
        self.baseline = baseline_service

    def generate_forecast(
        self,
        values: Sequence[float] | NormalizedTimeSeries,
        metric_name: str = "cpu_utilization",
        service: str = "default",
        alpha: float = 0.4,
        beta: float = 0.2,
        horizons: Sequence[str] = ("5m", "15m", "30m", "1h", "6h", "24h"),
        step_minutes: int = 1,
    ) -> ForecastResult:
        """
        Generates multi-horizon forecast using Holt's Linear Exponential Smoothing.
        """
        now = datetime.now(UTC)
        vals: list[float] = (
            values.values if isinstance(values, NormalizedTimeSeries) else [float(v) for v in values]
        )
        name = values.metric_name if isinstance(values, NormalizedTimeSeries) else metric_name
        svc = values.service if isinstance(values, NormalizedTimeSeries) else service

        n = len(vals)
        b = self.baseline.calculate_baseline(vals, metric_name=name)

        # Baseline standard deviation for interval widening
        sigma = max(0.5, b.standard_deviation)
        current_val = vals[-1] if vals else 50.0

        # Handle few samples fallback
        if n < 3:
            level = current_val
            trend = 0.0
        else:
            # Holt's Double Exponential Smoothing
            level = vals[0]
            trend = (vals[-1] - vals[0]) / max(1, n - 1)

            for i in range(1, n):
                prev_level = level
                level = alpha * vals[i] + (1.0 - alpha) * (level + trend)
                trend = beta * (level - prev_level) + (1.0 - beta) * trend

        # Generate Forecast Points for each requested horizon
        forecast_pts: list[ForecastPoint] = []
        is_percentage = any(
            k in name.lower() for k in ["percent", "pct", "cpu", "memory", "mem", "disk", "usage"]
        )

        for h in horizons:
            horizon_mins = HORIZON_MINUTES_MAP.get(h, 15)
            steps = horizon_mins / max(1, step_minutes)

            # Dampen extreme trend projections over long horizons
            damping_factor = min(1.0, 1.0 / (1.0 + (steps * 0.005)))
            projected = level + (steps * trend * damping_factor)

            # Uncertainty widening with horizon distance
            uncertainty = 1.96 * sigma * math.sqrt(1.0 + (steps * 0.05))

            lower = projected - uncertainty
            upper = projected + uncertainty

            # Bound percentages logically
            if is_percentage:
                projected = max(0.0, min(100.0, projected))
                lower = max(0.0, min(100.0, lower))
                upper = max(0.0, min(100.0, upper))
            else:
                projected = max(0.0, projected)
                lower = max(0.0, lower)
                upper = max(0.0, upper)

            confidence = round(
                max(0.20, min(0.98, (b.data_sufficiency.confidence_factor * 0.95) / (1.0 + (steps * 0.008)))),
                2,
            )

            forecast_pts.append(
                ForecastPoint(
                    horizon=h,
                    timestamp=now + timedelta(minutes=horizon_mins),
                    predicted_value=round(projected, 2),
                    lower_bound=round(lower, 2),
                    upper_bound=round(upper, 2),
                    confidence=confidence,
                )
            )

        # Format historical points (last 20 points)
        hist_pts = []
        if isinstance(values, NormalizedTimeSeries) and values.points:
            for p in values.points[-20:]:
                hist_pts.append({"timestamp": p.timestamp.isoformat(), "value": p.value})
        else:
            for idx, v in enumerate(vals[-20:]):
                t = now - timedelta(minutes=(len(vals[-20:]) - idx - 1))
                hist_pts.append({"timestamp": t.isoformat(), "value": v})

        return ForecastResult(
            metric_name=name,
            service=svc,
            current_value=round(current_val, 2),
            forecast_points=forecast_pts,
            historical_points=hist_pts,
            model_used="holt_linear_exponential_smoothing",
            data_sufficiency={
                "samples": b.data_sufficiency.samples,
                "minimum_required": b.data_sufficiency.minimum_required,
                "sufficient": b.data_sufficiency.sufficient,
                "confidence_factor": b.data_sufficiency.confidence_factor,
            },
            generated_at=now,
        )


forecasting_engine = ForecastingEngine()
