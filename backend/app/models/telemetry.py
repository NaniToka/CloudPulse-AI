"""
Telemetry ORM Models for Unified Telemetry Intelligence Platform.
Tracks logs, metrics, distributed traces, and event pipelines.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class TelemetryEvent(UUIDMixin, TimestampMixin, Base):
    """Event pipeline storage for cloud and application signals."""

    __tablename__ = "telemetry_events"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # k8s, aws, azure, gcp, app
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # log, alert, state_change, audit
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")  # CRITICAL, ERROR, WARN, INFO, DEBUG
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class MetricRecord(UUIDMixin, TimestampMixin, Base):
    """High-frequency metric ingestion record."""

    __tablename__ = "telemetry_metric_records"

    resource_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)  # cpu_usage_pct, mem_usage_pct, rps
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="percent")  # percent, ms, bytes, count
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class TraceRecord(UUIDMixin, TimestampMixin, Base):
    """Distributed tracing span record."""

    __tablename__ = "telemetry_trace_records"

    service_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    duration: Mapped[float] = mapped_column(Float, nullable=False)  # in milliseconds
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OK")  # OK, ERROR, TIMEOUT
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
