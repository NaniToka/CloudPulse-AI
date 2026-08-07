"""Infrastructure resource model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.organization import Organization


class Resource(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "resources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ec2, rds, gke, etc.
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # aws, gcp, azure, on-prem
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    availability_zone: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="healthy")  # healthy, degraded, down
    environment: Mapped[str] = mapped_column(String(50), default="production")

    # Metrics snapshot (refreshed periodically)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=True)
    memory_percent: Mapped[float] = mapped_column(Float, nullable=True)
    disk_percent: Mapped[float] = mapped_column(Float, nullable=True)
    cost_per_hour: Mapped[float] = mapped_column(Float, nullable=True)

    # Flexible metadata (instance type, tags, etc.)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    tags: Mapped[dict] = mapped_column(JSON, default=dict)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="resources")
    alerts: Mapped[list[Alert]] = relationship("Alert", back_populates="resource")
