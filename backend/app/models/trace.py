"""
Trace, Span, and ServiceDependency models for Distributed Tracing Platform.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Trace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "traces"

    trace_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # e.g., GET /api/v1/users/checkout
    root_service: Mapped[str] = mapped_column(String(255), nullable=False, default="api-gateway")
    http_method: Mapped[str] = mapped_column(String(10), nullable=False, default="GET")
    http_status: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=145.2)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ok")  # ok, error
    span_count: Mapped[int] = mapped_column(Integer, nullable=False, default=7)

    # Gemini AI Analysis JSON storage
    ai_analysis_json: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships
    spans: Mapped[list["Span"]] = relationship(
        "Span", back_populates="trace", cascade="all, delete-orphan"
    )


class Span(UUIDMixin, Base):
    __tablename__ = "spans"

    trace_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("traces.trace_id", ondelete="CASCADE"), nullable=False, index=True
    )
    span_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    parent_span_id: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    operation_name: Mapped[str] = mapped_column(String(500), nullable=False)
    span_kind: Mapped[str] = mapped_column(
        String(50), nullable=False, default="SERVER"
    )  # SERVER, CLIENT, INTERNAL
    status_code: Mapped[str] = mapped_column(String(50), nullable=False, default="OK")  # OK, ERROR
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=24.5)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attributes_json: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    events_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)

    # Relationship
    trace: Mapped["Trace"] = relationship("Trace", back_populates="spans")


class ServiceDependency(UUIDMixin, Base):
    __tablename__ = "service_dependencies"

    source_service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1250)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    avg_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=42.5)
