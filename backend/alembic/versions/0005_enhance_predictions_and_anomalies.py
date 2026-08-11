"""add anomaly_events table and enhance predictions table

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # anomaly_events                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "anomaly_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("service", sa.String(length=255), nullable=False),
        sa.Column("metric_name", sa.String(length=200), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("baseline_value", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("anomaly_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("severity", sa.String(length=20), server_default="NORMAL", nullable=False),
        sa.Column("direction", sa.String(length=30), server_default="SPIKE_HIGH", nullable=False),
        sa.Column("method", sa.String(length=50), server_default="z_score", nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anomaly_events_organization_id", "anomaly_events", ["organization_id"])
    op.create_index("ix_anomaly_events_service", "anomaly_events", ["service"])
    op.create_index("ix_anomaly_events_metric_name", "anomaly_events", ["metric_name"])
    op.create_index("ix_anomaly_events_resource_id", "anomaly_events", ["resource_id"])
    op.create_index("ix_anomaly_events_severity", "anomaly_events", ["severity"])
    op.create_index("ix_anomaly_events_detected_at", "anomaly_events", ["detected_at"])


def downgrade() -> None:
    op.drop_index("ix_anomaly_events_detected_at", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_severity", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_resource_id", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_metric_name", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_service", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_organization_id", table_name="anomaly_events")
    op.drop_table("anomaly_events")
