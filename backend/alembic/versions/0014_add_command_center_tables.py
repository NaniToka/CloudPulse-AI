"""Add Command Center tables for enterprise executive intelligence.

Revision ID: 0014
Revises: 0013
Create Date: 2026-08-14 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as pb
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. executive_command_snapshots
    op.create_table(
        "executive_command_snapshots",
        pb.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        pb.Column("user_id", postgresql.UUID(as_uuid=True), pb.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        pb.Column("platform_health_score", pb.Float(), nullable=False, server_default="100.0"),
        pb.Column("health_status", pb.String(length=32), nullable=False, server_default="HEALTHY"),
        pb.Column("operational_risk_score", pb.Float(), nullable=False, server_default="0.0"),
        pb.Column("risk_level", pb.String(length=32), nullable=False, server_default="LOW"),
        pb.Column("active_incidents_count", pb.Integer(), nullable=False, server_default="0"),
        pb.Column("slo_compliance_pct", pb.Float(), nullable=False, server_default="100.0"),
        pb.Column("security_risk_score", pb.Float(), nullable=False, server_default="0.0"),
        pb.Column("monthly_spend", pb.Float(), nullable=False, server_default="0.0"),
        pb.Column("potential_savings", pb.Float(), nullable=False, server_default="0.0"),
        pb.Column("executive_brief", pb.Text(), nullable=False),
        pb.Column("is_ai_powered", pb.Boolean(), nullable=False, server_default="false"),
        pb.Column("snapshot_metadata", pb.JSON(), nullable=True),
        pb.Column("created_at", pb.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_executive_command_snapshots_id",
        "executive_command_snapshots",
        ["id"],
        unique=False,
    )

    # 2. command_insight_records
    op.create_table(
        "command_insight_records",
        pb.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        pb.Column("snapshot_id", postgresql.UUID(as_uuid=True), pb.ForeignKey("executive_command_snapshots.id", ondelete="CASCADE"), nullable=True),
        pb.Column("category", pb.String(length=64), nullable=False),
        pb.Column("severity", pb.String(length=32), nullable=False),
        pb.Column("title", pb.String(length=255), nullable=False),
        pb.Column("summary", pb.Text(), nullable=False),
        pb.Column("affected_service", pb.String(length=128), nullable=True),
        pb.Column("affected_provider", pb.String(length=64), nullable=True),
        pb.Column("affected_region", pb.String(length=64), nullable=True),
        pb.Column("business_impact", pb.Text(), nullable=False),
        pb.Column("technical_impact", pb.Text(), nullable=False),
        pb.Column("confidence", pb.Float(), nullable=False, server_default="95.0"),
        pb.Column("recommended_action", pb.Text(), nullable=False),
        pb.Column("source_system", pb.String(length=64), nullable=False),
        pb.Column("created_at", pb.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_command_insight_records_id",
        "command_insight_records",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_command_insight_records_id", table_name="command_insight_records")
    op.drop_table("command_insight_records")
    op.drop_index("ix_executive_command_snapshots_id", table_name="executive_command_snapshots")
    op.drop_table("executive_command_snapshots")
