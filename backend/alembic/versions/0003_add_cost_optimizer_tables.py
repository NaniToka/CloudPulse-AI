"""add cloud_costs and optimization_recommendations tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # cloud_costs                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "cloud_costs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_name", sa.String(length=255), nullable=False),
        sa.Column("service", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=50), server_default="gcp", nullable=False),
        sa.Column("region", sa.String(length=100), server_default="us-central1", nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("daily_cost", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("usage_amount", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("usage_unit", sa.String(length=50), server_default="hrs", nullable=False),
        sa.Column("environment", sa.String(length=50), server_default="production", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column(
            "tags",
            postgresql.JSON(astext_type=sa.Text()),
            server_default=sa.text("'{}'::json"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_cloud_costs_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cloud_costs_id", "cloud_costs", ["id"])
    op.create_index("ix_cloud_costs_service", "cloud_costs", ["service"])
    op.create_index("ix_cloud_costs_region", "cloud_costs", ["region"])
    op.create_index("ix_cloud_costs_timestamp", "cloud_costs", ["timestamp"])
    op.create_index("ix_cloud_costs_user_id", "cloud_costs", ["user_id"])

    # ------------------------------------------------------------------ #
    # optimization_recommendations                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "optimization_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resource_name", sa.String(length=255), nullable=False),
        sa.Column("service", sa.String(length=100), nullable=False),
        sa.Column("recommendation_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("current_cost", sa.Float(), nullable=False),
        sa.Column("estimated_savings", sa.Float(), nullable=False),
        sa.Column("effort_level", sa.String(length=20), server_default="medium", nullable=False),
        sa.Column("risk_level", sa.String(length=20), server_default="low", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["cloud_costs.id"],
            ondelete="SET NULL",
            name="fk_optimization_recommendations_resource_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_optimization_recommendations_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_optimization_recommendations_id", "optimization_recommendations", ["id"])
    op.create_index("ix_optimization_recommendations_user_id", "optimization_recommendations", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_optimization_recommendations_user_id", table_name="optimization_recommendations")
    op.drop_index("ix_optimization_recommendations_id", table_name="optimization_recommendations")
    op.drop_table("optimization_recommendations")

    op.drop_index("ix_cloud_costs_user_id", table_name="cloud_costs")
    op.drop_index("ix_cloud_costs_timestamp", table_name="cloud_costs")
    op.drop_index("ix_cloud_costs_region", table_name="cloud_costs")
    op.drop_index("ix_cloud_costs_service", table_name="cloud_costs")
    op.drop_index("ix_cloud_costs_id", table_name="cloud_costs")
    op.drop_table("cloud_costs")
