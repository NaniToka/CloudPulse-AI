"""
ServiceObjective ORM Model for Enterprise SRE & Reliability Intelligence Center.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class ServiceObjective(UUIDMixin, TimestampMixin, Base):
    """
    Represents a Service Level Objective (SLO) for a target service.
    Defines availability, latency, error rate, or throughput targets and time windows.
    """

    __tablename__ = "service_objectives"

    service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicator_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="availability", index=True
    )  # availability | latency | error_rate | throughput
    target: Mapped[float] = mapped_column(Float, nullable=False, default=99.9)  # Target value (e.g. 99.9%)
    target_threshold_ms: Mapped[float | None] = mapped_column(Float, nullable=True)  # For latency SLO (e.g. 500ms)
    window: Mapped[str] = mapped_column(String(20), nullable=False, default="30d")  # 30d | 7d | 24h | 1h
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ServiceObjective service={self.service!r} target={self.target}% type={self.indicator_type!r}>"
