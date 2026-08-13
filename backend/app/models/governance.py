"""
SQLAlchemy ORM models for Enterprise Cloud Governance & Compliance Center:
- GovernancePolicy
- GovernanceViolation
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin


class GovernancePolicy(UUIDMixin, Base):
    """Represents a cloud governance & security policy rule."""

    __tablename__ = "governance_policies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), default="Security", nullable=False, index=True
    )  # Security, FinOps, SRE, Kubernetes, Tagging, Network, Operations
    severity: Mapped[str] = mapped_column(
        String(20), default="MEDIUM", nullable=False, index=True
    )  # LOW, MEDIUM, HIGH, CRITICAL
    provider: Mapped[str] = mapped_column(
        String(50), default="Multi-Cloud", nullable=False, index=True
    )  # AWS, Azure, GCP, Kubernetes, Multi-Cloud
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_identifier: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    violations: Mapped[list[GovernanceViolation]] = relationship(
        "GovernanceViolation", back_populates="policy", cascade="all, delete-orphan"
    )


class GovernanceViolation(UUIDMixin, Base):
    """Represents a detected non-compliant resource policy violation."""

    __tablename__ = "governance_violations"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("governance_policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    resource_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), default="us-east-1", nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), default="OPEN", nullable=False, index=True
    )  # OPEN, ACKNOWLEDGED, IN_REMEDIATION, RESOLVED, WAIVED

    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)

    waived_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    waiver_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    policy: Mapped[GovernancePolicy] = relationship("GovernancePolicy", back_populates="violations")
