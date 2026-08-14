"""
Autonomous Cloud Operations & Self-Healing Center ORM Models.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class RemediationPlan(UUIDMixin, TimestampMixin, Base):
    """
    Remediation Plan entity created from incident/anomaly/security/FinOps signals.
    """

    __tablename__ = "remediation_plans"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    trigger_source: Mapped[str] = mapped_column(
        String(100), nullable=False, default="incident_intelligence"
    )  # incident_intelligence, anomaly_detection, predictive_aiops, security_center, finops, governance, capacity, k8s
    source_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    affected_resource: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="AWS"
    )  # AWS, Azure, GCP, Kubernetes
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="MEDIUM"
    )  # LOW, MEDIUM, HIGH, CRITICAL
    expected_impact: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_downtime_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rollback_supported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    execution_mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="SIMULATED"
    )  # DRY_RUN, SIMULATED, LIVE
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.92)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PLANNED"
    )  # PLANNED, BLOCKED, APPROVED, REJECTED, EXECUTING, COMPLETED, FAILED, ROLLED_BACK
    plan_details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    executions = relationship("RemediationExecution", back_populates="plan", cascade="all, delete-orphan")
    approvals = relationship("RemediationApproval", back_populates="plan", cascade="all, delete-orphan")


class RemediationExecution(UUIDMixin, TimestampMixin, Base):
    """
    Execution instance tracking lifecycle, verification, and audit result.
    """

    __tablename__ = "remediation_executions"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    execution_mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="SIMULATED"
    )  # DRY_RUN, SIMULATED, LIVE
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="QUEUED"
    )  # QUEUED, VALIDATING, WAITING_APPROVAL, APPROVED, EXECUTING, VERIFYING, COMPLETED, FAILED, ROLLED_BACK, BLOCKED, CANCELLED
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    precondition_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    execution_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    verification_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    previous_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    new_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    rollback_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="NOT_SUPPORTED"
    )  # ROLLBACK_AVAILABLE, ROLLBACK_REQUESTED, ROLLBACK_SUCCESS, ROLLBACK_FAILED, NOT_SUPPORTED

    plan = relationship("RemediationPlan", back_populates="executions")


class RemediationApproval(UUIDMixin, TimestampMixin, Base):
    """
    Approval record for medium/high/critical risk autonomous actions.
    """

    __tablename__ = "remediation_approvals"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False
    )
    approver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approver_role: Mapped[str] = mapped_column(String(50), nullable=False, default="Admin")
    approval_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # NOT_REQUIRED, PENDING, APPROVED, REJECTED, EXPIRED
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan = relationship("RemediationPlan", back_populates="approvals")


class AutonomyPolicy(UUIDMixin, TimestampMixin, Base):
    """
    Configurable system-wide autonomy & self-healing rules.
    """

    __tablename__ = "autonomy_policies"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    autonomy_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )  # 0: Observe, 1: Recommend, 2: Require Approval, 3: Auto Low-Risk, 4: Policy Controlled
    max_autonomous_risk: Mapped[str] = mapped_column(
        String(20), nullable=False, default="LOW"
    )  # LOW, MEDIUM, HIGH
    allowed_providers: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=lambda: ["AWS", "Azure", "GCP", "Kubernetes"]
    )
    allowed_environments: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=lambda: ["development", "staging", "production"]
    )
    excluded_resources: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    excluded_namespaces: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    default_execution_mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="SIMULATED"
    )  # DRY_RUN, SIMULATED, LIVE
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MaintenanceWindow(UUIDMixin, TimestampMixin, Base):
    """
    Operational maintenance window blocking autonomous execution.
    """

    __tablename__ = "maintenance_windows"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    block_all_actions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allowed_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class RemediationAuditLog(UUIDMixin, TimestampMixin, Base):
    """
    Immutable audit log entry for autonomous action lifecycle events.
    """

    __tablename__ = "remediation_audit_logs"

    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("remediation_plans.id", ondelete="SET NULL"), nullable=True
    )
    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("remediation_executions.id", ondelete="SET NULL"), nullable=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # PLAN_CREATED, PRECONDITION_CHECK, POLICY_EVALUATED, APPROVED, EXECUTED, VERIFIED, ROLLED_BACK, BLOCKED
    target_resource: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutionLock(UUIDMixin, TimestampMixin, Base):
    """
    Lock entity ensuring concurrency protection for target resources.
    """

    __tablename__ = "execution_locks"

    resource_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RemediationPolicyRecord(UUIDMixin, TimestampMixin, Base):
    """
    Granular trigger-condition-action policy for automated AIOps remediation.
    """

    __tablename__ = "remediation_policies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    trigger_signal: Mapped[str] = mapped_column(String(100), nullable=False)  # INCIDENT, ANOMALY, CAPACITY, FINOPS, SLO
    condition_logic: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    execution_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="APPROVED")  # DRY_RUN, SIMULATION, MANUAL, APPROVED, AUTOMATED
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system")

