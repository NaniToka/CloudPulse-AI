"""add ai security center fields to security_scans

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-12

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("security_scans", sa.Column("resource_type", sa.String(length=100), server_default="s3_bucket", nullable=False))
    op.add_column("security_scans", sa.Column("risk_score", sa.Float(), server_default="7.5", nullable=False))
    op.add_column("security_scans", sa.Column("confidence", sa.Float(), server_default="0.90", nullable=False))
    op.add_column("security_scans", sa.Column("evidence", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("security_scans", sa.Column("first_detected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("security_scans", sa.Column("last_detected_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("security_scans", "last_detected_at")
    op.drop_column("security_scans", "first_detected_at")
    op.drop_column("security_scans", "evidence")
    op.drop_column("security_scans", "confidence")
    op.drop_column("security_scans", "risk_score")
    op.drop_column("security_scans", "resource_type")
