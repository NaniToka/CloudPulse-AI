"""Alert model."""

import uuid
from sqlalchemy import String, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # critical | high | medium | low
    status: Mapped[str] = mapped_column(String(20), default="active")    # active | acknowledged | resolved
    metric_name: Mapped[str] = mapped_column(String(200), nullable=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=True)
    tags: Mapped[dict] = mapped_column(JSON, default=dict)

    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="SET NULL"),
        nullable=True,
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="alerts")
    incident: Mapped["Incident"] = relationship("Incident", back_populates="alerts")
