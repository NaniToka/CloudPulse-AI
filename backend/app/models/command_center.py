"""
SQLAlchemy ORM models for Enterprise Executive Intelligence & Operations Command Center.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ExecutiveCommandSnapshot(Base):
    """
    Stores aggregated snapshots of enterprise executive health, operational risk,
    costs, security posture, and SLO metrics.
    """

    __tablename__ = "executive_command_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    platform_health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    health_status: Mapped[str] = mapped_column(String(32), default="HEALTHY", nullable=False)
    operational_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW", nullable=False)

    active_incidents_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    slo_compliance_pct: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    security_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    monthly_spend: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    potential_savings: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    executive_brief: Mapped[str] = mapped_column(Text, nullable=False)
    is_ai_powered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    snapshot_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class CommandInsightRecord(Base):
    """
    Stores correlated cross-domain intelligence insights and top risks.
    """

    __tablename__ = "command_insight_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("executive_command_snapshots.id", ondelete="CASCADE"), nullable=True
    )

    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    affected_service: Mapped[str | None] = mapped_column(String(128), nullable=True)
    affected_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    affected_region: Mapped[str | None] = mapped_column(String(64), nullable=True)

    business_impact: Mapped[str] = mapped_column(Text, nullable=False)
    technical_impact: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=95.0, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)

    source_system: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
