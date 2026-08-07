"""
CloudAccount ORM Model for AWS, Azure, GCP accounts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class CloudAccount(UUIDMixin, TimestampMixin, Base):
    """Connected multi-cloud account (AWS, Azure, Google Cloud)."""

    __tablename__ = "cloud_accounts"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # AWS | Azure | GCP
    account_id: Mapped[str] = mapped_column(String(100), nullable=False)  # AWS Account ID, Azure Subscription ID, GCP Project ID
    credentials_type: Mapped[str] = mapped_column(String(50), nullable=False, default="role_arn")  # role_arn | service_principal | service_account_key
    credentials_meta: Mapped[dict] = mapped_column(JSON, default=dict)  # Role ARN, Tenant ID, Service Account Email, etc.
    default_region: Mapped[str] = mapped_column(String(50), nullable=False, default="us-east-1")
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")  # production | staging | dev
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="connected")  # connected | syncing | error | disconnected
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    resources: Mapped[list["CloudResource"]] = relationship(
        "CloudResource", back_populates="account", cascade="all, delete-orphan"
    )
