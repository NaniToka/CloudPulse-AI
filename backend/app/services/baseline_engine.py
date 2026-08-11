"""
Deterministic Statistical Baseline Engine for Observability Metrics.

Calculates:
- Mean, Median, Standard Deviation, Variance, Min, Max
- Percentile Distributions (P50, P90, P95, P99)
- Rolling window averages and standard deviations
- Rigorous Data Sufficiency verification
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Sequence

import structlog

from app.services.telemetry_normalizer import NormalizedTimeSeries

log = structlog.get_logger(__name__)


@dataclass
class DataSufficiency:
    """Evaluation of statistical sample size adequacy."""

    samples: int
    minimum_required: int
    sufficient: bool
    confidence_factor: float = 1.0  # 0.0 to 1.0 multiplier based on sample completeness


@dataclass
class MetricBaseline:
    """Calculated deterministic statistical baseline container."""

    metric_name: str
    window: str  # "5m", "15m", "1h", "6h", "24h", "7d"
    samples_count: int
    mean: float
    median: float
    standard_deviation: float
    variance: float
    min_value: float
    max_value: float
    p50: float
    p90: float
    p95: float
    p99: float
    rolling_average: float
    rolling_std: float
    data_sufficiency: DataSufficiency
    calculated_at: datetime


class BaselineEngine:
    """Computes deterministic baseline metrics with sufficiency guards."""

    MINIMUM_SAMPLES_MAP = {
        "5m": 5,
        "15m": 8,
        "1h": 15,
        "6h": 25,
        "24h": 30,
        "7d": 60,
    }

    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Calculates exact linear interpolation percentile (0.0 to 1.0)."""
        if not sorted_data:
            return 0.0
        n = len(sorted_data)
        if n == 1:
            return sorted_data[0]

        k = (n - 1) * percentile
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1

    def calculate_data_sufficiency(
        self,
        samples_count: int,
        window: str = "1h",
        custom_minimum: int | None = None,
    ) -> DataSufficiency:
        """Evaluates whether the sample count provides mathematical statistical validity."""
        min_required = custom_minimum or self.MINIMUM_SAMPLES_MAP.get(window, 10)
        is_sufficient = samples_count >= min_required
        confidence = min(1.0, max(0.1, samples_count / max(1, min_required * 2)))

        return DataSufficiency(
            samples=samples_count,
            minimum_required=min_required,
            sufficient=is_sufficient,
            confidence_factor=round(confidence, 2),
        )

    def calculate_baseline(
        self,
        series: NormalizedTimeSeries | Sequence[float],
        window: str = "1h",
        metric_name: str = "metric",
    ) -> MetricBaseline:
        """
        Calculates complete deterministic statistical baseline for given series.
        """
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        values: list[float] = (
            series.values if isinstance(series, NormalizedTimeSeries) else [float(v) for v in series]
        )
        name = series.metric_name if isinstance(series, NormalizedTimeSeries) else metric_name

        n = len(values)
        sufficiency = self.calculate_data_sufficiency(n, window=window)

        if n == 0:
            return MetricBaseline(
                metric_name=name,
                window=window,
                samples_count=0,
                mean=0.0,
                median=0.0,
                standard_deviation=0.0,
                variance=0.0,
                min_value=0.0,
                max_value=0.0,
                p50=0.0,
                p90=0.0,
                p95=0.0,
                p99=0.0,
                rolling_average=0.0,
                rolling_std=0.0,
                data_sufficiency=sufficiency,
                calculated_at=now,
            )

        mean_val = sum(values) / n
        sorted_vals = sorted(values)
        median_val = self._percentile(sorted_vals, 0.50)

        # Variance and Standard Deviation
        variance_val = sum((x - mean_val) ** 2 for x in values) / max(1, n - 1 if n > 1 else 1)
        std_val = math.sqrt(variance_val)

        min_val = sorted_vals[0]
        max_val = sorted_vals[-1]

        p50 = median_val
        p90 = self._percentile(sorted_vals, 0.90)
        p95 = self._percentile(sorted_vals, 0.95)
        p99 = self._percentile(sorted_vals, 0.99)

        # Rolling Window (last min(10, n) points)
        rolling_window_size = min(10, n)
        recent_window = values[-rolling_window_size:]
        rolling_avg = sum(recent_window) / rolling_window_size
        rolling_var = sum((x - rolling_avg) ** 2 for x in recent_window) / max(
            1, rolling_window_size - 1 if rolling_window_size > 1 else 1
        )
        rolling_std = math.sqrt(rolling_var)

        return MetricBaseline(
            metric_name=name,
            window=window,
            samples_count=n,
            mean=round(mean_val, 4),
            median=round(median_val, 4),
            standard_deviation=round(std_val, 4),
            variance=round(variance_val, 4),
            min_value=round(min_val, 4),
            max_value=round(max_val, 4),
            p50=round(p50, 4),
            p90=round(p90, 4),
            p95=round(p95, 4),
            p99=round(p99, 4),
            rolling_average=round(rolling_avg, 4),
            rolling_std=round(rolling_std, 4),
            data_sufficiency=sufficiency,
            calculated_at=now,
        )


baseline_engine = BaselineEngine()
