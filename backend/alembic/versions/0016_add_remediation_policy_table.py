"""Add Remediation Policy table for AIOps Action Center.

Revision ID: 0016
Revises: 0015
Create Date: 2026-08-14 05:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "remediation_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("trigger_signal", sa.String(length=100), nullable=False),
        sa.Column("condition_logic", sa.JSON(), nullable=False),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("execution_mode", sa.String(length=50), nullable=False, server_default="APPROVED"),
        sa.Column("cooldown_minutes", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(length=255), nullable=False, server_default="system"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_remediation_policies_name"), "remediation_policies", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_remediation_policies_name"), table_name="remediation_policies")
    op.drop_table("remediation_policies")
