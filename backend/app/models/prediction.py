"""
Prediction & Anomaly Event ORM Models for Predictive AIOps & Anomaly Intelligence Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class AnomalyEvent(UUIDMixin, TimestampMixin, Base):
    """Persistent record of statistical and multi-metric anomaly occurrences."""

    __tablename__ = "anomaly_events"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 - 1.0
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL", index=True)  # NORMAL, WARNING, CRITICAL
    direction: Mapped[str] = mapped_column(String(30), nullable=False, default="SPIKE_HIGH")  # SPIKE_HIGH, DROP_LOW, DRIFT
    method: Mapped[str] = mapped_column(String(50), nullable=False, default="z_score")  # z_score, rolling_dev, ewma, rate_of_change
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships
    organization: Mapped[Organization | None] = relationship("Organization")


class Prediction(UUIDMixin, TimestampMixin, Base):
    """Predictive failure, capacity exhaustion, and incident probability record."""

    __tablename__ = "predictions"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    service: Mapped[str] = mapped_column(String(255), nullable=False, default="api-gateway", index=True)
    metric_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production", index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="us-east-1", index=True)

    # Risk & Probability Scores
    prediction_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.85
    )  # 0.0 to 1.0
    failure_probability: Mapped[float] = mapped_column(
        Float, nullable=False, default=85.0
    )  # 0 to 100%
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.92
    )  # 0.0 to 1.0
    risk_level: Mapped[str] = mapped_column(
        String(50), nullable=False, default="High", index=True
    )  # Critical, High, Medium, Low
    status: Mapped[str] = mapped_column(
        String(50), default="Active", index=True
    )  # Active, Monitoring, Resolved, Expired, False_Positive, Mitigated, Dismissed, Triggered

    # Trend & Capacity Exhaustion Details
    trend_direction: Mapped[str] = mapped_column(String(50), nullable=False, default="STABLE")  # INCREASING, DECREASING, STABLE, ACCELERATING_DEGRADATION, RECOVERY
    trend_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    rate_of_change: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_failure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_time_to_threshold_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Topology & Evidence
    affected_services: Mapped[list] = mapped_column(JSON, default=list)
    likely_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_preventive_actions: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    triggering_metrics: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    data_sufficiency: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    forecast_points: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    correlated_signals: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Diagnostics Engine & Explanations
    analysis_engine: Mapped[str] = mapped_column(String(20), nullable=False, default="local")  # "gemini" | "local"
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_metrics_of_concern: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    ai_historical_pattern_comparison: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_possible_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_immediate_preventive_actions: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    ai_long_term_recommendations: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Relationships
    organization: Mapped[Organization | None] = relationship("Organization")
