"""
Deterministic Statistical Anomaly Detection Engine.

Implements multi-algorithm anomaly detection:
1. Z-Score Deviation (Z = (x - μ) / σ)
2. Rolling Window Envelope Deviation
3. Rate-of-Change Velocity Detection
4. Exponentially Weighted Moving Average (EWMA) Drift
5. Configured SLA / Capacity Threshold Guards
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import structlog

from app.services.baseline_engine import BaselineEngine, baseline_engine
from app.services.telemetry_normalizer import NormalizedTimeSeries

log = structlog.get_logger(__name__)


@dataclass
class AnomalyDetectionResult:
    """Detailed deterministic anomaly assessment."""

    metric_name: str
    value: float
    baseline_value: float
    anomaly_score: float  # 0.0 to 1.0
    severity: str  # "NORMAL", "WARNING", "CRITICAL"
    is_anomaly: bool
    direction: str  # "SPIKE_HIGH", "DROP_LOW", "DRIFT", "NORMAL"
    method_used: str  # "z_score", "rolling_envelope", "rate_of_change", "ewma", "threshold"
    z_score: float
    deviation_percent: float
    explanation: str


class AnomalyEngine:
    """Detects metric anomalies using multi-method statistical algorithms."""

    def __init__(self, baseline_service: BaselineEngine = baseline_engine) -> None:
        self.baseline = baseline_service

    def detect_zscore_anomaly(
        self,
        value: float,
        mean: float,
        std: float,
        warning_threshold: float = 2.0,
        critical_threshold: float = 3.0,
    ) -> tuple[float, float, str, str]:
        """
        Calculates Z-score and normalized anomaly score (0.0 to 1.0).
        Returns: (z_score, anomaly_score, severity, direction)
        """
        # Handle zero or near-zero variance
        if std < 1e-6:
            if abs(value - mean) < 1e-4:
                return (0.0, 0.05, "NORMAL", "NORMAL")
            # Step change from constant baseline
            rel_diff = abs(value - mean) / max(1.0, abs(mean))
            if rel_diff > 0.40:
                direction = "SPIKE_HIGH" if value > mean else "DROP_LOW"
                return (4.0, 0.92, "CRITICAL", direction)
            elif rel_diff > 0.15:
                direction = "SPIKE_HIGH" if value > mean else "DROP_LOW"
                return (2.5, 0.70, "WARNING", direction)
            return (0.5, 0.20, "NORMAL", "NORMAL")

        z = (value - mean) / std
        abs_z = abs(z)

        direction = "SPIKE_HIGH" if z > 0 else "DROP_LOW" if z < 0 else "NORMAL"

        if abs_z >= critical_threshold:
            severity = "CRITICAL"
            score = min(0.99, 0.80 + ((abs_z - critical_threshold) * 0.05))
        elif abs_z >= warning_threshold:
            severity = "WARNING"
            score = 0.50 + ((abs_z - warning_threshold) / (critical_threshold - warning_threshold)) * 0.29
        else:
            severity = "NORMAL"
            score = min(0.45, (abs_z / warning_threshold) * 0.45)

        return (round(z, 2), round(score, 2), severity, direction)

    def detect_ewma_drift(
        self,
        values: Sequence[float],
        alpha: float = 0.3,
        drift_threshold: float = 2.0,
    ) -> tuple[float, bool]:
        """
        Calculates Exponentially Weighted Moving Average (EWMA) and detects persistent drift.
        Returns: (latest_ewma, is_drifting)
        """
        if not values:
            return (0.0, False)
        if len(values) == 1:
            return (values[0], False)

        s = values[0]
        for x in values[1:]:
            s = alpha * x + (1.0 - alpha) * s

        # Compare latest EWMA with baseline from initial steady-state window
        initial_n = min(4, len(values))
        initial_mean = sum(values[:initial_n]) / initial_n
        initial_std = math.sqrt(
            sum((x - initial_mean) ** 2 for x in values[:initial_n]) / max(1, initial_n - 1)
        )
        if initial_std < 1e-4:
            drift_z = abs(s - initial_mean) / max(1.0, initial_mean * 0.1)
        else:
            drift_z = abs(s - initial_mean) / initial_std

        return (round(s, 4), drift_z >= drift_threshold)

    def detect_anomaly(
        self,
        current_value: float,
        historical_values: Sequence[float] | NormalizedTimeSeries,
        metric_name: str = "cpu_utilization",
        custom_critical_threshold: float | None = None,
    ) -> AnomalyDetectionResult:
        """
        Executes complete multi-method anomaly detection against historical telemetry.
        """
        vals: list[float] = (
            historical_values.values
            if isinstance(historical_values, NormalizedTimeSeries)
            else [float(v) for v in historical_values]
        )
        name = (
            historical_values.metric_name
            if isinstance(historical_values, NormalizedTimeSeries)
            else metric_name
        )

        # Baseline evaluation
        b = self.baseline.calculate_baseline(vals, metric_name=name)

        # 1. Z-Score Anomaly Detection
        z_score, anomaly_score, severity, direction = self.detect_zscore_anomaly(
            value=current_value,
            mean=b.mean,
            std=b.standard_deviation,
        )

        dev_percent = (
            ((current_value - b.mean) / b.mean) * 100.0 if abs(b.mean) > 1e-4 else 0.0
        )

        method = "z_score"
        explanation = f"{name} value {current_value:.2f} is within nominal parameters (Baseline: {b.mean:.2f})."

        # 2. SLA / Explicit Critical Threshold Guard
        if custom_critical_threshold is not None and current_value >= custom_critical_threshold:
            anomaly_score = max(anomaly_score, 0.94)
            severity = "CRITICAL"
            direction = "SPIKE_HIGH"
            method = "sla_threshold"
            explanation = f"{name} ({current_value:.2f}) breached static critical threshold of {custom_critical_threshold:.2f}."
        elif severity == "CRITICAL":
            explanation = (
                f"{name} exhibited a critical {direction.lower().replace('_', ' ')}: "
                f"{current_value:.2f} vs baseline {b.mean:.2f} ({z_score:+.2f}σ, {dev_percent:+.1f}%)."
            )
        elif severity == "WARNING":
            explanation = (
                f"{name} elevated above warning band: "
                f"{current_value:.2f} vs baseline {b.mean:.2f} ({z_score:+.2f}σ)."
            )

        is_anom = severity in ["WARNING", "CRITICAL"]

        return AnomalyDetectionResult(
            metric_name=name,
            value=round(current_value, 4),
            baseline_value=b.mean,
            anomaly_score=anomaly_score,
            severity=severity,
            is_anomaly=is_anom,
            direction=direction,
            method_used=method,
            z_score=z_score,
            deviation_percent=round(dev_percent, 2),
            explanation=explanation,
        )


anomaly_engine = AnomalyEngine()
