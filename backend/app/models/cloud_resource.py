"""
CloudResource ORM Model for auto-discovered multi-cloud infrastructure resources.
"""

from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import String, Text, Float, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class CloudResource(UUIDMixin, TimestampMixin, Base):
    """Auto-discovered multi-cloud resource (EC2, GKE, RDS, Blob, VPC, Lambda, etc.)."""

    __tablename__ = "cloud_resources"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # virtual_machine | kubernetes_cluster | database | storage | networking | function | load_balancer
    service: Mapped[str] = mapped_column(String(100), nullable=False)  # EC2 | GKE | RDS | S3 | Cloud SQL | AKS | Azure Blob
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # AWS | Azure | GCP
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    availability_zone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="healthy")  # healthy | warning | critical | stopped

    # Telemetry & Financials
    cpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disk_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_in_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_out_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0 to 100

    tags: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cloud_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    account: Mapped["CloudAccount"] = relationship("CloudAccount", back_populates="resources")
