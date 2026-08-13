"""Add Service Reliability Engine 2.0 tables.

Revision ID: 0015
Revises: 0014
Create Date: 2026-08-14 05:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. service_reliability_profiles
    op.create_table(
        "service_reliability_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("service_id", sa.String(length=255), nullable=False),
        sa.Column("service_name", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="AWS"),
        sa.Column("region", sa.String(length=50), nullable=False, server_default="us-east-1"),
        sa.Column("availability_pct", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("latency_p95_ms", sa.Float(), nullable=False, server_default="50.0"),
        sa.Column("latency_p99_ms", sa.Float(), nullable=False, server_default="120.0"),
        sa.Column("error_rate_pct", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("slo_target", sa.Float(), nullable=False, server_default="99.9"),
        sa.Column("current_slo", sa.Float(), nullable=False, server_default="99.9"),
        sa.Column("error_budget_total_sec", sa.Float(), nullable=False, server_default="2592.0"),
        sa.Column("error_budget_remaining_sec", sa.Float(), nullable=False, server_default="2592.0"),
        sa.Column("error_budget_consumed_pct", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("burn_rate", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("reliability_score", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="HEALTHY"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_service_reliability_profiles_service_id", "service_reliability_profiles", ["service_id"])
    op.create_index("ix_service_reliability_profiles_service_name", "service_reliability_profiles", ["service_name"])
    op.create_index("ix_service_reliability_profiles_status", "service_reliability_profiles", ["status"])

    # 2. reliability_risk_records
    op.create_table(
        "reliability_risk_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("service_name", sa.String(length=255), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="LOW"),
        sa.Column("top_factors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reliability_risk_records_service_name", "reliability_risk_records", ["service_name"])
    op.create_index("ix_reliability_risk_records_risk_level", "reliability_risk_records", ["risk_level"])

    # 3. reliability_recommendation_records
    op.create_table(
        "reliability_recommendation_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("service_name", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("category", sa.String(length=100), nullable=False, server_default="General Reliability"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("expected_impact", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reliability_recommendation_records_service_name", "reliability_recommendation_records", ["service_name"])
    op.create_index("ix_reliability_recommendation_records_priority", "reliability_recommendation_records", ["priority"])


def downgrade() -> None:
    op.drop_table("reliability_recommendation_records")
    op.drop_table("reliability_risk_records")
    op.drop_table("service_reliability_profiles")
