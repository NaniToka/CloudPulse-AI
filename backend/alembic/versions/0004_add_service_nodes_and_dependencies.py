"""add service_nodes and enhance service_dependencies tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # service_nodes                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "service_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), server_default="service", nullable=False),
        sa.Column("environment", sa.String(length=50), server_default="production", nullable=False),
        sa.Column("region", sa.String(length=50), server_default="us-east-1", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="HEALTHY", nullable=False),
        sa.Column("health_score", sa.Float(), server_default="100.0", nullable=False),
        sa.Column("error_rate", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("latency_p99_ms", sa.Float(), server_default="45.0", nullable=False),
        sa.Column("request_rate", sa.Float(), server_default="120.0", nullable=False),
        sa.Column("active_incidents_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_nodes_organization_id", "service_nodes", ["organization_id"])
    op.create_index("ix_service_nodes_name", "service_nodes", ["name"])
    op.create_index("ix_service_nodes_type", "service_nodes", ["type"])
    op.create_index("ix_service_nodes_environment", "service_nodes", ["environment"])
    op.create_index("ix_service_nodes_region", "service_nodes", ["region"])
    op.create_index("ix_service_nodes_status", "service_nodes", ["status"])


def downgrade() -> None:
    op.drop_index("ix_service_nodes_status", table_name="service_nodes")
    op.drop_index("ix_service_nodes_region", table_name="service_nodes")
    op.drop_index("ix_service_nodes_environment", table_name="service_nodes")
    op.drop_index("ix_service_nodes_type", table_name="service_nodes")
    op.drop_index("ix_service_nodes_name", table_name="service_nodes")
    op.drop_index("ix_service_nodes_organization_id", table_name="service_nodes")
    op.drop_table("service_nodes")
