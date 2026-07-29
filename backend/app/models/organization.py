"""Organization model."""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="starter")
    team_size: Mapped[str] = mapped_column(String(50), nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="organization")
    incidents: Mapped[list["Incident"]] = relationship("Incident", back_populates="organization")
