"""
ORM Models for Enterprise SLO, SLA & Error Budget Intelligence Center.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class SloMeasurement(UUIDMixin, TimestampMixin, Base):
    """
    Time-series measurement data for Service Level Indicators (SLIs).
    Calculates good events vs total events, error rates, and latency percentiles.
    """

    __tablename__ = "slo_measurements"

    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    indicator_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # availability, latency, error_rate, throughput
    total_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    good_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bad_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    availability_pct: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    error_rate_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency_p50_ms: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    latency_p90_ms: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    latency_p95_ms: Mapped[float] = mapped_column(Float, nullable=False, default=80.0)
    latency_p99_ms: Mapped[float] = mapped_column(Float, nullable=False, default=150.0)
    throughput_rps: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    window: Mapped[str] = mapped_column(String(20), nullable=False, default="30d")
    is_fixture: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SloViolationRecord(UUIDMixin, TimestampMixin, Base):
    """
    Recorded SLO & SLA breaches and threshold violations.
    """

    __tablename__ = "slo_violations"

    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_objectives.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # availability, latency, error_rate, budget_exhaustion, burn_rate
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    difference: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, RESOLVED, ACKNOWLEDGED


class ErrorBudgetLog(UUIDMixin, TimestampMixin, Base):
    """
    Historical record of Error Budget consumption for a target service.
    """

    __tablename__ = "error_budget_logs"

    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slo_target: Mapped[float] = mapped_column(Float, nullable=False, default=99.9)
    total_budget_sec: Mapped[float] = mapped_column(Float, nullable=False, default=2592.0)  # 30d @ 99.9% = 2592s allowed downtime
    consumed_budget_sec: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    remaining_budget_pct: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    burn_rate_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="HEALTHY")  # HEALTHY, WARNING, EXHAUSTED


class BurnRateAlert(UUIDMixin, TimestampMixin, Base):
    """
    Multi-window burn rate detection alerts.
    """

    __tablename__ = "burn_rate_alerts"

    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    burn_rate_x: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL", index=True)  # NORMAL, ELEVATED, HIGH, CRITICAL
    window_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 1h, 6h, 24h, 72h
    observed_failure_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    allowed_failure_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.001)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
