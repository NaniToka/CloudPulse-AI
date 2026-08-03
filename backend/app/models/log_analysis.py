"""
LogAnalysis ORM model.

Stores the results of an AI-powered log file analysis.
Each row represents one uploaded file and its analysis output.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class LogAnalysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "log_analyses"

    # ── Upload metadata ───────────────────────────────────────────────
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # log | txt | json

    # ── Parsed log statistics ─────────────────────────────────────────
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    info_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Raw parsed log content (capped; not the full file) ────────────
    # Stores up to 500 parsed log entries as a JSON array for the viewer
    parsed_entries: Mapped[list] = mapped_column(
        JSON, default=list, nullable=False
    )

    # ── AI analysis output ────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending | analyzing | complete | error

    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # critical | high | medium | low
    recommended_fixes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preventive_measures: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_error: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # ── Owner ─────────────────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LogAnalysis id={self.id} file={self.filename!r} status={self.status}>"
