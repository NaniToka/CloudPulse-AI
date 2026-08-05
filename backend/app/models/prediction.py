"""
Prediction model for AI Predictive Incident Detection Engine.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, JSON, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class Prediction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "predictions"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    service: Mapped[str] = mapped_column(String(255), nullable=False, default="api-gateway")
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="us-east-1")
    prediction_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)  # 0.0 to 1.0
    failure_probability: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)  # 0 to 100%
    expected_failure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, default="High")  # Critical, High, Medium, Low
    status: Mapped[str] = mapped_column(String(50), default="Active")  # Active, Mitigated, Dismissed, Triggered
    affected_services: Mapped[list] = mapped_column(JSON, default=list)
    likely_root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.92)  # 0.0 to 1.0
    recommended_preventive_actions: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    triggering_metrics: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)

    # Gemini AI Detailed Explanation Fields
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    ai_metrics_of_concern: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    ai_historical_pattern_comparison: Mapped[str] = mapped_column(Text, nullable=True)
    ai_possible_impact: Mapped[str] = mapped_column(Text, nullable=True)
    ai_immediate_preventive_actions: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    ai_long_term_recommendations: Mapped[list] = mapped_column(JSON, nullable=True, default=list)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
