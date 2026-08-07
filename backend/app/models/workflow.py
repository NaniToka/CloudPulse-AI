"""
Workflow Automation ORM Models (inspired by Google Cloud Workflows, AWS Step Functions, Temporal, n8n).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Workflow(UUIDMixin, TimestampMixin, Base):
    """Workflow Definition containing triggers, nodes (actions/conditions), and directed edges."""

    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active | paused | draft
    trigger_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="manual"
    )  # incident_created | alert_fired | cpu_threshold | cron | manual | webhook
    trigger_config: Mapped[dict] = mapped_column(
        JSON, default=dict
    )  # threshold values, cron expression, webhook secrets

    # Visual Canvas DAG representation
    nodes: Mapped[list] = mapped_column(
        JSON, default=list
    )  # list of { id, type, label, config, position: {x, y} }
    edges: Mapped[list] = mapped_column(
        JSON, default=list
    )  # list of { id, source, target, condition?: str }

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tags: Mapped[list] = mapped_column(
        JSON, default=list
    )  # ["k8s", "remediation", "incident", "slack"]

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    executions: Mapped[list[WorkflowExecution]] = relationship(
        "WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan"
    )


class WorkflowExecution(UUIDMixin, TimestampMixin, Base):
    """Workflow Execution Instance (run record)."""

    __tablename__ = "workflow_executions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="running"
    )  # running | completed | failed | awaiting_approval | rolled_back
    trigger_source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    trigger_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Execution telemetry & variables
    context_variables: Mapped[dict] = mapped_column(JSON, default=dict)
    step_results: Mapped[list] = mapped_column(JSON, default=list)  # timeline of step outcomes

    # Relationships
    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="executions")
    step_logs: Mapped[list[WorkflowStepLog]] = relationship(
        "WorkflowStepLog", back_populates="execution", cascade="all, delete-orphan"
    )
    approvals: Mapped[list[WorkflowApproval]] = relationship(
        "WorkflowApproval", back_populates="execution", cascade="all, delete-orphan"
    )


class WorkflowStepLog(UUIDMixin, TimestampMixin, Base):
    """Log record for an individual node/step execution inside a workflow run."""

    __tablename__ = "workflow_step_logs"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    node_label: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # k8s_restart | slack_notify | gemini_analyze | etc.
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="completed"
    )  # completed | failed | skipped | awaiting_approval

    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    execution: Mapped[WorkflowExecution] = relationship(
        "WorkflowExecution", back_populates="step_logs"
    )


class WorkflowApproval(UUIDMixin, TimestampMixin, Base):
    """Manual Approval Gate record for critical enterprise actions (e.g. Production VM restart)."""

    __tablename__ = "workflow_approvals"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    step_title: Mapped[str] = mapped_column(String(255), nullable=False)
    approver_role: Mapped[str] = mapped_column(
        String(100), nullable=False, default="admin"
    )  # admin | sre | devops
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending | approved | rejected

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    execution: Mapped[WorkflowExecution] = relationship(
        "WorkflowExecution", back_populates="approvals"
    )


class WorkflowTemplate(UUIDMixin, TimestampMixin, Base):
    """Pre-built enterprise automation templates."""

    __tablename__ = "workflow_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Kubernetes"
    )  # Kubernetes | Security | Incident | Cost
    description: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    nodes: Mapped[list] = mapped_column(JSON, default=list)
    edges: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    icon: Mapped[str] = mapped_column(String(100), nullable=False, default="Zap")
