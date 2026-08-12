"""Add cost_budgets table for FinOps Budget Intelligence

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("cost_budgets"):
        op.create_table(
            "cost_budgets",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("provider", sa.String(length=50), server_default="all", nullable=False),
            sa.Column("service", sa.String(length=100), server_default="all", nullable=False),
            sa.Column("environment", sa.String(length=50), server_default="all", nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("period", sa.String(length=20), server_default="monthly", nullable=False),
            sa.Column("threshold_percentages", sa.JSON(), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("cost_budgets"):
        op.drop_table("cost_budgets")
