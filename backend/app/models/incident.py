"""Incident model."""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class Incident(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(10), nullable=False, default="P2")  # P0, P1, P2, P3
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="High")  # Critical, High, Medium, Low
    status: Mapped[str] = mapped_column(String(50), default="Open")  # Open, Investigating, Monitoring, Resolved, Closed
    affected_service: Mapped[str] = mapped_column(String(255), nullable=True, default="api-gateway")
    affected_services: Mapped[list] = mapped_column(JSON, default=list)
    assigned_engineer: Mapped[str] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=True, default="System")
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str] = mapped_column(String(50), nullable=True)  # manual | ai | auto

    # AI Analysis Fields
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    ai_root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    ai_business_impact: Mapped[str] = mapped_column(Text, nullable=True)
    ai_suggested_resolution: Mapped[str] = mapped_column(Text, nullable=True)
    ai_preventive_actions: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    ai_similar_incidents: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    ai_estimated_resolution_time: Mapped[str] = mapped_column(String(100), nullable=True)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="incidents"
    )
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="incident")

