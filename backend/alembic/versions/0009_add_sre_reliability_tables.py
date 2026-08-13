"""Add service_objectives table for SRE & Reliability Intelligence Center

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("service_objectives"):
        op.create_table(
            "service_objectives",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("service", sa.String(length=255), nullable=False, index=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("indicator_type", sa.String(length=50), server_default="availability", nullable=False, index=True),
            sa.Column("target", sa.Float(), server_default="99.9", nullable=False),
            sa.Column("target_threshold_ms", sa.Float(), nullable=True),
            sa.Column("window", sa.String(length=20), server_default="30d", nullable=False),
            sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("service_objectives"):
        op.drop_table("service_objectives")
