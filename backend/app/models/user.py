"""
User ORM model.

Maps to the ``users`` PostgreSQL table.  All sensitive fields (password hash)
are never exposed directly; Pydantic schemas control serialisation.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession
    from app.models.notification import Notification
    from app.models.organization import Organization


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Core identity
    # ------------------------------------------------------------------
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ------------------------------------------------------------------
    # Account status & security flags
    # ------------------------------------------------------------------
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ------------------------------------------------------------------
    # Foreign keys
    # ------------------------------------------------------------------
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships  (lazy="raise" catches accidental sync access in async)
    # ------------------------------------------------------------------
    organization: Mapped[Organization | None] = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id],
        lazy="raise",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        lazy="raise",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="raise",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        parts = filter(None, [self.first_name, self.last_name])
        return " ".join(parts)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"
