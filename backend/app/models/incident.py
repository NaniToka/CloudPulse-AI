"""Incident model & Timeline Event model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.organization import Organization


class Incident(UUIDMixin, TimestampMixin, Base):
    """
    Enterprise Incident entity.
    Represents an active or resolved incident correlated from multi-source observability streams.
    """

    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="HIGH"
    )  # CRITICAL, HIGH, MEDIUM, LOW (also P0, P1, P2, P3)
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="High"
    )  # Critical, High, Medium, Low
    status: Mapped[str] = mapped_column(
        String(50), default="INVESTIGATING"
    )  # OPEN, ACKNOWLEDGED, INVESTIGATING, MITIGATING, RESOLVED, CLOSED, DETECTED, IDENTIFIED
    source: Mapped[str] = mapped_column(
        String(100), nullable=False, default="correlation_engine"
    )  # correlation_engine | alertmanager | datadog | kubernetes | cloud | manual
    affected_service: Mapped[str] = mapped_column(
        String(255), nullable=True, default="api-gateway"
    )
    affected_services: Mapped[list] = mapped_column(JSON, default=list)
    affected_resources: Mapped[list] = mapped_column(JSON, default=list)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(
        String(50), nullable=False, default="production"
    )
    affected_region: Mapped[str] = mapped_column(
        String(100), nullable=True, default="us-east-1"
    )
    assigned_engineer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default="System"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # manual | ai | auto | Engineer

    # SLA & MTTR Tracking
    mttr_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    sla_target_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1800
    )  # CRITICAL: 900, HIGH: 1800, MEDIUM: 7200, LOW: 28800
    sla_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING | AT_RISK | MET | BREACHED
    correlation_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.94
    )
    fingerprint: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    # Root Cause & Multi-modal Analysis
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.94
    )
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    correlation_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)
    blast_radius: Mapped[dict] = mapped_column(JSON, default=dict)

    # AI Analysis Fields (Structured & Extended)
    ai_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    analysis_engine: Mapped[str] = mapped_column(
        String(50), default="local"
    )  # gemini | local
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_business_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_suggested_resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_immediate_mitigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_long_term_prevention: Mapped[list] = mapped_column(
        JSON, nullable=True, default=list
    )
    ai_preventive_actions: Mapped[list] = mapped_column(
        JSON, nullable=True, default=list
    )
    ai_similar_incidents: Mapped[list] = mapped_column(
        JSON, nullable=True, default=list
    )
    ai_estimated_resolution_time: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    ai_confidence_score: Mapped[float | None] = mapped_column(
        Float, nullable=True, default=0.94
    )

    # Resolution Verification Engine Fields
    resolution_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    verification_evidence: Mapped[list] = mapped_column(
        JSON, default=list, nullable=False
    )
    remaining_risk: Mapped[str] = mapped_column(
        String(50), default="NONE", nullable=False
    )  # NONE | LOW | MEDIUM | HIGH
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="incidents"
    )
    alerts: Mapped[list[Alert]] = relationship("Alert", back_populates="incident")
    timeline_events: Mapped[list[IncidentTimelineEvent]] = relationship(
        "IncidentTimelineEvent",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentTimelineEvent.timestamp.asc()",
    )

    @property
    def service(self) -> str:
        return self.affected_service or "api-gateway"

    @service.setter
    def service(self, val: str) -> None:
        self.affected_service = val

    @property
    def region(self) -> str:
        return self.affected_region or "us-east-1"

    @region.setter
    def region(self, val: str) -> None:
        self.affected_region = val


class IncidentTimelineEvent(UUIDMixin, TimestampMixin, Base):
    """Chronological event log for an incident."""

    __tablename__ = "incident_timeline_events"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="anomaly_detected"
    )  # metric_anomaly | alert_triggered | trace_failure | log_error | incident_created | incident_declared | acknowledged | investigating | rca_identified | mitigating | remediation_recommended | remediation_executed | status_changed | resolved | engineer_note
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default="System"
    )

    # Relationship
    incident: Mapped[Incident] = relationship(
        "Incident", back_populates="timeline_events"
    )

    @property
    def message(self) -> str:
        return self.description or self.title


IncidentEvent = IncidentTimelineEvent
