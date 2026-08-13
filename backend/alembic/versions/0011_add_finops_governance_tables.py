"""Add FinOps Governance & Cost Control Center tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. finops_cost_policies
    if not inspector.has_table("finops_cost_policies"):
        op.create_table(
            "finops_cost_policies",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=50), server_default="SPENDING", nullable=False, index=True),
            sa.Column("provider", sa.String(length=50), server_default="all", nullable=False, index=True),
            sa.Column("scope", sa.String(length=50), server_default="all", nullable=False),
            sa.Column("metric", sa.String(length=100), nullable=False),
            sa.Column("operator", sa.String(length=10), server_default=">", nullable=False),
            sa.Column("threshold_value", sa.Float(), nullable=False),
            sa.Column("severity", sa.String(length=20), server_default="MEDIUM", nullable=False, index=True),
            sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False, index=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    # 2. finops_cost_violations
    if not inspector.has_table("finops_cost_violations"):
        op.create_table(
            "finops_cost_violations",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("finops_cost_policies.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("policy_name", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False, index=True),
            sa.Column("severity", sa.String(length=20), nullable=False, index=True),
            sa.Column("provider", sa.String(length=50), nullable=False, index=True),
            sa.Column("service", sa.String(length=100), server_default="all", nullable=False),
            sa.Column("resource_id", sa.String(length=255), nullable=True),
            sa.Column("resource_name", sa.String(length=255), server_default="N/A", nullable=False),
            sa.Column("actual_value", sa.Float(), nullable=False),
            sa.Column("threshold_value", sa.Float(), nullable=False),
            sa.Column("difference", sa.Float(), nullable=False),
            sa.Column("status", sa.String(length=30), server_default="OPEN", nullable=False, index=True),
            sa.Column("explanation", sa.Text(), nullable=False),
            sa.Column("recommended_action", sa.Text(), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    # 3. finops_policy_exceptions
    if not inspector.has_table("finops_policy_exceptions"):
        op.create_table(
            "finops_policy_exceptions",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("finops_cost_policies.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("scope", sa.String(length=100), server_default="all", nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("requested_by", sa.String(length=255), nullable=False),
            sa.Column("approved_by", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False, index=True),
            sa.Column("expiration_date", sa.DateTime(timezone=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    # 4. finops_remediation_actions
    if not inspector.has_table("finops_remediation_actions"):
        op.create_table(
            "finops_remediation_actions",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("violation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("finops_cost_violations.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("action_type", sa.String(length=100), nullable=False),
            sa.Column("resource_name", sa.String(length=255), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("estimated_savings", sa.Float(), nullable=False),
            sa.Column("risk_level", sa.String(length=20), server_default="low", nullable=False),
            sa.Column("rollback_supported", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("execution_mode", sa.String(length=20), server_default="DRY_RUN", nullable=False),
            sa.Column("approval_status", sa.String(length=30), server_default="PENDING", nullable=False, index=True),
            sa.Column("requested_by", sa.String(length=255), nullable=False),
            sa.Column("approved_by", sa.String(length=255), nullable=True),
            sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("original_config", sa.JSON(), nullable=False),
            sa.Column("recommended_config", sa.JSON(), nullable=False),
            sa.Column("rollback_config", sa.JSON(), nullable=False),
            sa.Column("execution_result", sa.Text(), nullable=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    # 5. finops_governance_audit_logs
    if not inspector.has_table("finops_governance_audit_logs"):
        op.create_table(
            "finops_governance_audit_logs",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("actor_email", sa.String(length=255), nullable=False),
            sa.Column("action", sa.String(length=100), nullable=False, index=True),
            sa.Column("entity_type", sa.String(length=50), nullable=False),
            sa.Column("entity_id", sa.String(length=255), nullable=False),
            sa.Column("result", sa.String(length=50), server_default="SUCCESS", nullable=False),
            sa.Column("metadata_json", sa.JSON(), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = [
        "finops_governance_audit_logs",
        "finops_remediation_actions",
        "finops_policy_exceptions",
        "finops_cost_violations",
        "finops_cost_policies",
    ]
    for tbl in tables:
        if inspector.has_table(tbl):
            op.drop_table(tbl)
