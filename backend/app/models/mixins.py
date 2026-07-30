"""
Reusable SQLAlchemy ORM mixins.

UUIDMixin      — UUID v4 primary key (PostgreSQL ``uuid`` type).
TimestampMixin — ``created_at`` / ``updated_at`` with DB-side defaults.

Both mixins use SQLAlchemy 2.x ``Mapped`` / ``mapped_column`` declarative API.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Adds a UUID v4 primary key generated client-side."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns managed by the DB."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
