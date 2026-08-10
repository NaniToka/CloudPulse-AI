"""
CRUD operations for LogAnalysis.

All DB access is async (AsyncSession).
Queries are always scoped to user_id to prevent cross-user data access.
"""

from __future__ import annotations

import uuid
from typing import Any

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
) -> LogAnalysis | None:
    """Fetch a single record owned by user_id."""
    result = await db.execute(
        select(LogAnalysis).where(
            LogAnalysis.id == record_id,
            LogAnalysis.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def seed_default_logs_if_empty(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Seed baseline realistic log analyses if the user has no records."""
    from sqlalchemy import func as _func

    count_res = await db.execute(
        select(_func.count()).select_from(LogAnalysis).where(LogAnalysis.user_id == user_id)
    )
    if count_res.scalar_one() > 0:
        return

    sample_logs = [
        {
            "filename": "api-gateway-prod-oom.log",
            "file_size_bytes": 14250,
            "file_type": "json",
            "status": "complete",
            "total_lines": 42,
            "error_count": 18,
            "warning_count": 8,
            "critical_count": 6,
            "info_count": 10,
            "severity": "CRITICAL",
            "executive_summary": "Sustained high heap memory allocation in api-gateway caused prolonged JVM GC pauses and container OOM-Kills, generating HTTP 504 timeouts on ingress traffic.",
            "root_cause": "Session token cache retained unbounded JSON payloads under 5,000 req/sec burst without TTL eviction policy.",
            "recommended_fixes": "1. Increase pod memory limit from 2Gi to 4Gi via kubectl patch deployment.\n2. Configure Redis TTL expiration for session cache entries (3600s).\n3. Enable G1GC low-latency garbage collector with -XX:MaxGCPauseMillis=200.",
            "preventive_measures": "1. Add Prometheus memory saturation alert at 80% utilization.\n2. Implement Kubernetes Horizontal Pod Autoscaler based on memory metric.\n3. Conduct load testing on session serialization handler.",
            "confidence_score": 0.96,
            "parsed_entries": [
                {"line_number": 1, "timestamp": "2026-08-10T15:20:01.102Z", "level": "INFO", "service": "api-gateway", "message": "Inbound request spike detected from ingress controller (rate=4820 rps)."},
                {"line_number": 2, "timestamp": "2026-08-10T15:20:04.234Z", "level": "WARN", "service": "api-gateway", "message": "JVM Heap memory threshold exceeded 85% (1740MB / 2048MB)."},
                {"line_number": 3, "timestamp": "2026-08-10T15:20:08.841Z", "level": "ERROR", "service": "api-gateway", "message": "java.lang.OutOfMemoryError: Java heap space during SessionContext deserialization."},
                {"line_number": 4, "timestamp": "2026-08-10T15:20:09.110Z", "level": "CRITICAL", "service": "api-gateway", "message": "Health check probe failed: /healthz timeout after 5000ms. Kubelet issuing SIGKILL."},
                {"line_number": 5, "timestamp": "2026-08-10T15:20:12.440Z", "level": "ERROR", "service": "api-gateway", "message": "Upstream connection dropped: 504 Gateway Timeout returned to 412 clients."}
            ]
        },
        {
            "filename": "auth-service-db-exhaustion.log",
            "file_size_bytes": 9820,
            "file_type": "standard",
            "status": "complete",
            "total_lines": 28,
            "error_count": 12,
            "warning_count": 6,
            "critical_count": 2,
            "info_count": 8,
            "severity": "HIGH",
            "executive_summary": "PostgreSQL connection pool on auth-service reached maximum capacity (100/100 connections), resulting in client authentication handshake timeouts.",
            "root_cause": "Long-running JWT validation queries blocked pooled connections due to missing index on users.organization_id.",
            "recommended_fixes": "1. Deploy PgBouncer connection pooler in transaction mode.\n2. Increase HikariCP maxLifetime and connectionTimeout to 30000ms.\n3. Add CREATE INDEX CONCURRENTLY idx_users_org_id ON users(organization_id).",
            "preventive_measures": "1. Implement circuit breaker for DB pool exhaustion.\n2. Set statement_timeout = '5s' on application database role.",
            "confidence_score": 0.94,
            "parsed_entries": [
                {"line_number": 1, "timestamp": "2026-08-10T15:10:00.012Z", "level": "INFO", "service": "auth-service", "message": "Token verification service initialized with 100 connection pool limit."},
                {"line_number": 2, "timestamp": "2026-08-10T15:11:15.542Z", "level": "WARN", "service": "auth-service", "message": "Connection pool utilization high: 92/100 active connections in use."},
                {"line_number": 3, "timestamp": "2026-08-10T15:12:02.190Z", "level": "ERROR", "service": "auth-service", "message": "TimeoutException: Connection acquisition timed out after 30000ms waiting for available pool connection."},
                {"line_number": 4, "timestamp": "2026-08-10T15:12:05.882Z", "level": "CRITICAL", "service": "auth-service", "message": "Authentication pipeline degraded: 48 authorization requests rejected."}
            ]
        }
    ]

    for item in sample_logs:
        rec = LogAnalysis(
            user_id=user_id,
            filename=item["filename"],
            file_size_bytes=item["file_size_bytes"],
            file_type=item["file_type"],
            status=item["status"],
            total_lines=item["total_lines"],
            error_count=item["error_count"],
            warning_count=item["warning_count"],
            critical_count=item["critical_count"],
            info_count=item["info_count"],
            severity=item["severity"],
            executive_summary=item["executive_summary"],
            root_cause=item["root_cause"],
            recommended_fixes=item["recommended_fixes"],
            preventive_measures=item["preventive_measures"],
            confidence_score=item["confidence_score"],
            parsed_entries=item["parsed_entries"],
        )
        db.add(rec)

    await db.commit()


async def list_by_user(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[LogAnalysis]:
    """List all analyses for a user, newest first."""
    await seed_default_logs_if_empty(db, user_id)
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
    await seed_default_logs_if_empty(db, user_id)
    from sqlalchemy import func
    from sqlalchemy import select as _select

    result = await db.execute(
        _select(func.count()).select_from(LogAnalysis).where(LogAnalysis.user_id == user_id)
    )
    return result.scalar_one()


async def update_analysis_result(
    db: AsyncSession,
    *,
    record: LogAnalysis,
    status: str,
    executive_summary: str | None = None,
    root_cause: str | None = None,
    severity: str | None = None,
    recommended_fixes: str | None = None,
    preventive_measures: str | None = None,
    confidence_score: float | None = None,
    ai_error: str | None = None,
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
) -> LogAnalysis | None:
    """Delete a record owned by user_id. Returns deleted record or None."""
    record = await get(db, record_id=record_id, user_id=user_id)
    if record:
        await db.delete(record)
        await db.flush()
    return record
