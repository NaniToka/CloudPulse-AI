"""
Runbook, AutomationStep, and RunbookExecution models for Auto Remediation Center.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Runbook(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "runbooks"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    incident_id: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False, default="api-gateway")
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="P1"
    )  # P0, P1, P2, P3
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Draft"
    )  # Draft, Approved, Executing, Completed, Failed

    executive_summary: Mapped[str] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    rollback_procedure: Mapped[str] = mapped_column(Text, nullable=True)
    verification_checklist: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    post_recovery_checklist: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    estimated_resolution_time: Mapped[str] = mapped_column(String(100), default="15 mins")
    risk_score: Mapped[float] = mapped_column(Float, default=2.5)  # 0.0 to 10.0
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95)  # 0.0 to 1.0

    # Relationships
    steps: Mapped[list["AutomationStep"]] = relationship(
        "AutomationStep", back_populates="runbook", cascade="all, delete-orphan"
    )
    executions: Mapped[list["RunbookExecution"]] = relationship(
        "RunbookExecution", back_populates="runbook", cascade="all, delete-orphan"
    )


class AutomationStep(UUIDMixin, Base):
    __tablename__ = "automation_steps"

    runbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runbooks.id", ondelete="CASCADE"), nullable=False
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    command: Mapped[str] = mapped_column(Text, nullable=False)  # CLI, K8s, Terraform
    expected_output: Mapped[str] = mapped_column(Text, nullable=True)
    rollback_command: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_time: Mapped[str] = mapped_column(String(50), default="2 mins")
    verification_method: Mapped[str] = mapped_column(String(255), default="HTTP 200 Health Probe")
    status: Mapped[str] = mapped_column(
        String(50), default="Pending"
    )  # Pending, Running, Completed, Failed

    # Relationship
    runbook: Mapped["Runbook"] = relationship("Runbook", back_populates="steps")


class RunbookExecution(UUIDMixin, Base):
    __tablename__ = "runbook_executions"

    runbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runbooks.id", ondelete="CASCADE"), nullable=False
    )
    executed_by: Mapped[str] = mapped_column(
        String(255), nullable=False, default="CloudPulse AI Auto-Remediator"
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="In_Progress"
    )  # In_Progress, Completed, Failed
    logs_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)

    # Relationship
    runbook: Mapped["Runbook"] = relationship("Runbook", back_populates="executions")
