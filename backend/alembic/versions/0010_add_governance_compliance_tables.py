"""Add governance_policies and governance_violations tables for Enterprise Governance & Compliance Center

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("governance_policies"):
        op.create_table(
            "governance_policies",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=50), server_default="Security", nullable=False, index=True),
            sa.Column("severity", sa.String(length=20), server_default="MEDIUM", nullable=False, index=True),
            sa.Column("provider", sa.String(length=50), server_default="Multi-Cloud", nullable=False, index=True),
            sa.Column("resource_type", sa.String(length=100), nullable=False),
            sa.Column("rule_identifier", sa.String(length=100), nullable=False, unique=True, index=True),
            sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    if not inspector.has_table("governance_violations"):
        op.create_table(
            "governance_violations",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("governance_policies.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("policy_name", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False, index=True),
            sa.Column("severity", sa.String(length=20), nullable=False, index=True),
            sa.Column("provider", sa.String(length=50), nullable=False, index=True),
            sa.Column("resource_id", sa.String(length=255), nullable=False, index=True),
            sa.Column("resource_name", sa.String(length=255), nullable=False),
            sa.Column("resource_type", sa.String(length=100), nullable=False),
            sa.Column("region", sa.String(length=100), server_default="us-east-1", nullable=False),
            sa.Column("status", sa.String(length=30), server_default="OPEN", nullable=False, index=True),
            sa.Column("evidence", sa.Text(), nullable=False),
            sa.Column("recommended_action", sa.Text(), nullable=False),
            sa.Column("waived_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("waiver_reason", sa.Text(), nullable=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("governance_violations"):
        op.drop_table("governance_violations")
    if inspector.has_table("governance_policies"):
        op.drop_table("governance_policies")
