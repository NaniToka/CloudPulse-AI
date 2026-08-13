"""Add autonomous operations and self-healing tables

Revision ID: 0012
Revises: 0011
Create Date: 2026-08-13 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. remediation_plans
    op.create_table(
        "remediation_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("trigger_source", sa.String(100), nullable=False, server_default="incident_intelligence"),
        sa.Column("source_event_id", sa.String(255), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("affected_resource", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="AWS"),
        sa.Column("environment", sa.String(50), nullable=False, server_default="production"),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="MEDIUM"),
        sa.Column("expected_impact", sa.Text(), nullable=False),
        sa.Column("estimated_downtime_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_impact", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("rollback_supported", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("execution_mode", sa.String(50), nullable=False, server_default="SIMULATED"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.92"),
        sa.Column("status", sa.String(50), nullable=False, server_default="PLANNED"),
        sa.Column("plan_details", sa.JSON(), nullable=False, server_default="{}"),
    )

    # 2. remediation_executions
    op.create_table(
        "remediation_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True),
        sa.Column("execution_mode", sa.String(50), nullable=False, server_default="SIMULATED"),
        sa.Column("status", sa.String(50), nullable=False, server_default="QUEUED"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("precondition_result", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("execution_result", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("verification_result", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("previous_state", sa.JSON(), nullable=True),
        sa.Column("new_state", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("rollback_status", sa.String(50), nullable=False, server_default="NOT_SUPPORTED"),
    )

    # 3. remediation_approvals
    op.create_table(
        "remediation_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approver_role", sa.String(50), nullable=False, server_default="Admin"),
        sa.Column("approval_status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("comments", sa.Text(), nullable=True),
    )

    # 4. autonomy_policies
    op.create_table(
        "autonomy_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("autonomy_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_autonomous_risk", sa.String(20), nullable=False, server_default="LOW"),
        sa.Column("allowed_providers", sa.JSON(), nullable=False, server_default='["AWS", "Azure", "GCP", "Kubernetes"]'),
        sa.Column("allowed_environments", sa.JSON(), nullable=False, server_default='["development", "staging", "production"]'),
        sa.Column("excluded_resources", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("excluded_namespaces", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("default_execution_mode", sa.String(50), nullable=False, server_default="SIMULATED"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # 5. maintenance_windows
    op.create_table(
        "maintenance_windows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("environment", sa.String(50), nullable=False, server_default="production"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("block_all_actions", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("allowed_actions", sa.JSON(), nullable=False, server_default="[]"),
    )

    # 6. remediation_audit_logs
    op.create_table(
        "remediation_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remediation_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remediation_executions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("target_resource", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("execution_mode", sa.String(50), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False, server_default="{}"),
    )

    # 7. execution_locks
    op.create_table(
        "execution_locks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resource_name", sa.String(255), nullable=False, unique=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("execution_locks")
    op.drop_table("remediation_audit_logs")
    op.drop_table("maintenance_windows")
    op.drop_table("autonomy_policies")
    op.drop_table("remediation_approvals")
    op.drop_table("remediation_executions")
    op.drop_table("remediation_plans")
