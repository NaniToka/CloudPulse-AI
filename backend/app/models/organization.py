"""
Organization ORM model.

One organization owns many users, resources, and incidents.
The slug is a URL-safe unique identifier derived from the name.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
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

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", lazy="raise"
    )
    resources: Mapped[list["Resource"]] = relationship(
        "Resource", back_populates="organization", lazy="raise"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        "Incident", back_populates="organization", lazy="raise"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organization id={self.id} slug={self.slug!r}>"
