"""add resolution verification fields to incidents

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-11

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("incidents", sa.Column("resolution_verified", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("incidents", sa.Column("verification_evidence", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("incidents", sa.Column("remaining_risk", sa.String(length=50), server_default="NONE", nullable=False))
    op.add_column("incidents", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("incidents", "verified_at")
    op.drop_column("incidents", "remaining_risk")
    op.drop_column("incidents", "verification_evidence")
    op.drop_column("incidents", "resolution_verified")
