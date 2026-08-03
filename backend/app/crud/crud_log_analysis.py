"""
CRUD operations for LogAnalysis.

All DB access is async (AsyncSession).
Queries are always scoped to user_id to prevent cross-user data access.
"""

from __future__ import annotations

import uuid
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log_analysis import LogAnalysis


async def create(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    filename: str,
    file_size_bytes: int,
    file_type: str,
    total_lines: int,
    error_count: int,
    warning_count: int,
    critical_count: int,
    info_count: int,
    parsed_entries: list[dict[str, Any]],
) -> LogAnalysis:
    """Create a new LogAnalysis row with parsed log data; status = 'analyzing'."""
    record = LogAnalysis(
        user_id=user_id,
        filename=filename,
        file_size_bytes=file_size_bytes,
        file_type=file_type,
        status="analyzing",
        total_lines=total_lines,
        error_count=error_count,
        warning_count=warning_count,
        critical_count=critical_count,
        info_count=info_count,
        parsed_entries=parsed_entries,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get(
    db: AsyncSession,
    *,
    record_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[LogAnalysis]:
    """Fetch a single record owned by user_id."""
    result = await db.execute(
        select(LogAnalysis).where(
            LogAnalysis.id == record_id,
            LogAnalysis.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def list_by_user(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[LogAnalysis]:
    """List all analyses for a user, newest first."""
    result = await db.execute(
        select(LogAnalysis)
        .where(LogAnalysis.user_id == user_id)
        .order_by(LogAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_by_user(db: AsyncSession, *, user_id: uuid.UUID) -> int:
    """Count total analyses for a user."""
    from sqlalchemy import func, select as _select
    result = await db.execute(
        _select(func.count()).select_from(LogAnalysis).where(
            LogAnalysis.user_id == user_id
        )
    )
    return result.scalar_one()


async def update_analysis_result(
    db: AsyncSession,
    *,
    record: LogAnalysis,
    status: str,
    executive_summary: Optional[str] = None,
    root_cause: Optional[str] = None,
    severity: Optional[str] = None,
    recommended_fixes: Optional[str] = None,
    preventive_measures: Optional[str] = None,
    confidence_score: Optional[float] = None,
    ai_error: Optional[str] = None,
) -> LogAnalysis:
    """Patch the AI analysis fields once Gemini has responded."""
    record.status = status
    if executive_summary is not None:
        record.executive_summary = executive_summary
    if root_cause is not None:
        record.root_cause = root_cause
    if severity is not None:
        record.severity = severity
    if recommended_fixes is not None:
        record.recommended_fixes = recommended_fixes
    if preventive_measures is not None:
        record.preventive_measures = preventive_measures
    if confidence_score is not None:
        record.confidence_score = confidence_score
    if ai_error is not None:
        record.ai_error = ai_error

    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def delete(
    db: AsyncSession,
    *,
    record_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[LogAnalysis]:
    """Delete a record owned by user_id. Returns deleted record or None."""
    record = await get(db, record_id=record_id, user_id=user_id)
    if record:
        await db.delete(record)
        await db.flush()
    return record
