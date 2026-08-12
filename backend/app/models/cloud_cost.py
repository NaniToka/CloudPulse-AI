"""
CloudCost, OptimizationRecommendation, and CostBudget ORM models.

Stores individual cloud resource costs, AI-generated cost optimization recommendations,
and FinOps budget tracking parameters.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class CloudCost(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "cloud_costs"

    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), default="gcp", nullable=False)
    region: Mapped[str] = mapped_column(
        String(100), default="us-central1", nullable=False, index=True
    )
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    daily_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    usage_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    usage_unit: Mapped[str] = mapped_column(String(50), default="hrs", nullable=False)
    environment: Mapped[str] = mapped_column(String(50), default="production", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # active | idle | overprovisioned
    tags: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CloudCost resource={self.resource_name!r} cost=${self.cost:.2f}>"


class OptimizationRecommendation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "optimization_recommendations"

    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cloud_costs.id", ondelete="SET NULL"),
        nullable=True,
    )
    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # idle_resource | wasted_resource | rightsizing | reserved_instance | auto_scaling
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    current_cost: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_savings: Mapped[float] = mapped_column(Float, nullable=False)
    effort_level: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )  # low | medium | high
    risk_level: Mapped[str] = mapped_column(
        String(20), default="low", nullable=False
    )  # low | medium | high
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )  # active | dismissed | applied
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OptimizationRecommendation title={self.title!r} savings=${self.estimated_savings:.2f}>"


class CostBudget(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "cost_budgets"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="all", nullable=False)
    service: Mapped[str] = mapped_column(String(100), default="all", nullable=False)
    environment: Mapped[str] = mapped_column(String(50), default="all", nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    period: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly | quarterly | annual
    threshold_percentages: Mapped[dict] = mapped_column(JSON, default=lambda: [50, 75, 90, 100], nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CostBudget name={self.name!r} amount=${self.amount:.2f}>"
