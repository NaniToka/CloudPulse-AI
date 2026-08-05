"""
Organization ORM model.

One organization owns many users, resources, and incidents.
The slug is a URL-safe unique identifier derived from the name.
"""

from typing import TYPE_CHECKING, Optional

import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.incident import Incident
    from app.models.resource import Resource
    from app.models.user import User


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="starter")
    team_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")  # Active, Suspended
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL", use_alter=True, name="fk_organization_owner"), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", foreign_keys="[User.organization_id]", lazy="raise"
    )
    resources: Mapped[list["Resource"]] = relationship(
        "Resource", back_populates="organization", lazy="raise"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        "Incident", back_populates="organization", lazy="raise"
    )
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    members: Mapped[list["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invitations: Mapped[list["Invitation"]] = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organization id={self.id} slug={self.slug!r}>"
