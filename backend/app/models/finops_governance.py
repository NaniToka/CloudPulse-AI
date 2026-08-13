"""
SQLAlchemy ORM models for FinOps Governance & Cost Control Center:
- FinOpsCostPolicy
- FinOpsCostViolation
- FinOpsPolicyException
- FinOpsRemediationAction
- FinOpsGovernanceAuditLog
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class FinOpsCostPolicy(UUIDMixin, TimestampMixin, Base):
    """Represents an enterprise FinOps cost policy rule."""

    __tablename__ = "finops_cost_policies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), default="SPENDING", nullable=False, index=True
    )  # BUDGET, SPENDING, RESOURCE, SERVICE, PROVIDER, REGION, WASTE, ANOMALY, FORECAST, KUBERNETES
    provider: Mapped[str] = mapped_column(
        String(50), default="all", nullable=False, index=True
    )  # aws, azure, gcp, kubernetes, all
    scope: Mapped[str] = mapped_column(
        String(50), default="all", nullable=False
    )  # production, staging, development, all
    metric: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # monthly_spend, daily_spend, resource_cost, waste_cost, anomaly_score, budget_utilization
    operator: Mapped[str] = mapped_column(
        String(10), default=">", nullable=False
    )  # >, >=, <, <=, ==, !=
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default="MEDIUM", nullable=False, index=True
    )  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    violations: Mapped[list[FinOpsCostViolation]] = relationship(
        "FinOpsCostViolation", back_populates="policy", cascade="all, delete-orphan"
    )
    exceptions: Mapped[list[FinOpsPolicyException]] = relationship(
        "FinOpsPolicyException", back_populates="policy", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinOpsCostPolicy name={self.name!r} threshold={self.threshold_value}>"


class FinOpsCostViolation(UUIDMixin, TimestampMixin, Base):
    """Represents a detected non-compliant cost policy violation."""

    __tablename__ = "finops_cost_violations"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("finops_cost_policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    service: Mapped[str] = mapped_column(String(100), default="all", nullable=False)

    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource_name: Mapped[str] = mapped_column(String(255), default="N/A", nullable=False)
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    difference: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), default="OPEN", nullable=False, index=True
    )  # OPEN, ACKNOWLEDGED, IN_REVIEW, RESOLVED, EXEMPTED

    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    policy: Mapped[FinOpsCostPolicy] = relationship("FinOpsCostPolicy", back_populates="violations")
    remediations: Mapped[list[FinOpsRemediationAction]] = relationship(
        "FinOpsRemediationAction", back_populates="violation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinOpsCostViolation policy={self.policy_name!r} status={self.status}>"


class FinOpsPolicyException(UUIDMixin, TimestampMixin, Base):
    """Represents an approved or pending policy exception/waiver."""

    __tablename__ = "finops_policy_exceptions"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("finops_cost_policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scope: Mapped[str] = mapped_column(String(100), default="all", nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False, index=True
    )  # PENDING, APPROVED, REJECTED, EXPIRED

    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    policy: Mapped[FinOpsCostPolicy] = relationship("FinOpsCostPolicy", back_populates="exceptions")

    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expiration_date

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinOpsPolicyException policy_id={self.policy_id} status={self.status}>"


class FinOpsRemediationAction(UUIDMixin, TimestampMixin, Base):
    """Represents a controlled remediation action with approval workflow & rollback payload."""

    __tablename__ = "finops_remediation_actions"

    violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("finops_cost_violations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # stop_idle_compute, resize_resource, delete_unattached_storage, reduce_log_retention, scale_down_k8s, remove_unused_ip, archive_snapshot, change_tier
    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_savings: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="low", nullable=False)  # low, medium, high
    rollback_supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    execution_mode: Mapped[str] = mapped_column(
        String(20), default="DRY_RUN", nullable=False
    )  # DRY_RUN, SIMULATED, LIVE
    approval_status: Mapped[str] = mapped_column(
        String(30), default="PENDING", nullable=False, index=True
    )  # PENDING, APPROVED, REJECTED, EXECUTED, ROLLED_BACK

    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    original_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    rollback_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    execution_result: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    violation: Mapped[FinOpsCostViolation | None] = relationship(
        "FinOpsCostViolation", back_populates="remediations"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinOpsRemediationAction action={self.action_type!r} status={self.approval_status}>"


class FinOpsGovernanceAuditLog(UUIDMixin, Base):
    """Immutable audit trail for FinOps governance actions."""

    __tablename__ = "finops_governance_audit_logs"

    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # POLICY_CREATED, POLICY_UPDATED, POLICY_ENABLED, POLICY_DISABLED, POLICY_EVALUATED, VIOLATION_CREATED, VIOLATION_ACKNOWLEDGED, EXCEPTION_CREATED, EXCEPTION_APPROVED, REMEDIATION_REQUESTED, REMEDIATION_APPROVED, REMEDIATION_EXECUTED, REMEDIATION_ROLLED_BACK
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # POLICY, VIOLATION, EXCEPTION, REMEDIATION
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinOpsGovernanceAuditLog action={self.action!r} actor={self.actor_email!r}>"
