"""
CloudRegion ORM Model for multi-cloud global region metrics.
"""

from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class CloudRegion(UUIDMixin, TimestampMixin, Base):
    """Multi-cloud region health, latency, and resource density."""

    __tablename__ = "cloud_regions"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # AWS | Azure | GCP
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="healthy"
    )  # healthy | degraded | offline
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=15.0)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_spend: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
