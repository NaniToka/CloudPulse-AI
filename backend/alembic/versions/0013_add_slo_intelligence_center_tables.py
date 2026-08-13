"""Add SLO intelligence center tables

Revision ID: 0013
Revises: 0012
Create Date: 2026-08-14 04:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. slo_measurements
    op.create_table(
        "slo_measurements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(255), nullable=False, index=True),
        sa.Column("indicator_type", sa.String(50), nullable=False, index=True),
        sa.Column("total_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("good_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bad_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("availability_pct", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("error_rate_pct", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("latency_p50_ms", sa.Float(), nullable=False, server_default="20.0"),
        sa.Column("latency_p90_ms", sa.Float(), nullable=False, server_default="50.0"),
        sa.Column("latency_p95_ms", sa.Float(), nullable=False, server_default="80.0"),
        sa.Column("latency_p99_ms", sa.Float(), nullable=False, server_default="150.0"),
        sa.Column("throughput_rps", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("window", sa.String(20), nullable=False, server_default="30d"),
        sa.Column("is_fixture", sa.Boolean(), nullable=False, server_default="true"),
    )

    # 2. slo_violations
    op.create_table(
        "slo_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(255), nullable=False, index=True),
        sa.Column("slo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("service_objectives.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("violation_type", sa.String(50), nullable=False, index=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="HIGH", index=True),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("actual_value", sa.Float(), nullable=False),
        sa.Column("difference", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
    )

    # 3. error_budget_logs
    op.create_table(
        "error_budget_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(255), nullable=False, index=True),
        sa.Column("slo_target", sa.Float(), nullable=False, server_default="99.9"),
        sa.Column("total_budget_sec", sa.Float(), nullable=False, server_default="2592.0"),
        sa.Column("consumed_budget_sec", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("remaining_budget_pct", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("burn_rate_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="HEALTHY"),
    )

    # 4. burn_rate_alerts
    op.create_table(
        "burn_rate_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(255), nullable=False, index=True),
        sa.Column("burn_rate_x", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="NORMAL", index=True),
        sa.Column("window_hours", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("observed_failure_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("allowed_failure_rate", sa.Float(), nullable=False, server_default="0.001"),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
    )


def downgrade() -> None:
    op.drop_table("burn_rate_alerts")
    op.drop_table("error_budget_logs")
    op.drop_table("slo_violations")
    op.drop_table("slo_measurements")
