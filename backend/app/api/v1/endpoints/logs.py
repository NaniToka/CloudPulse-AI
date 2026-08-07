"""
Log Analyzer endpoints.

Routes
------
POST   /api/v1/logs/upload        — Upload a log file, trigger AI analysis
GET    /api/v1/logs/history       — List all analyses for the current user
GET    /api/v1/logs/{id}          — Get one analysis by ID
DELETE /api/v1/logs/{id}          — Delete one analysis

Upload flow
-----------
1. Validate file (extension, size) — synchronous.
2. Parse log file into normalised entries — synchronous.
3. Insert DB row with status="analyzing" — respond immediately (201).
4. Fire-and-forget background task: call Gemini, update DB row.

The client polls GET /logs/{id} until status changes from "analyzing"
to "complete" or "error".

Authentication
--------------
All routes require a valid Bearer JWT (require_active_user dependency).
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_log_analysis
from app.models.user import User
from app.schemas.log_analysis import (
    AnalysisListItem,
    AnalysisResponse,
    HistoryResponse,
    LogStats,
    ParsedLogEntry,
    UploadResponse,
)
from app.services.log_analysis_service import analyse_logs
from app.services.log_parser import (
    LogValidationError,
    parse_log_file,
    validate_file,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Background task: run Gemini analysis, update DB row
# ---------------------------------------------------------------------------


async def _run_analysis(
    record_id: uuid.UUID,
    user_id: uuid.UUID,
    entries: list[dict],
    stats: dict,
    filename: str,
) -> None:
    """
    Background coroutine: call Gemini and persist results.

    Uses a fresh DB session because the request session is already closed
    by the time this background task runs.
    """
    from app.db.session import AsyncSessionLocal  # noqa: PLC0415

    async with AsyncSessionLocal() as db:
        try:
            await db.commit()  # ensure fresh transaction

            record = await crud_log_analysis.get(db, record_id=record_id, user_id=user_id)
            if not record:
                log.warning("log_analysis_record_missing", record_id=str(record_id))
                return

            try:
                analysis = await analyse_logs(
                    entries=entries,
                    stats=stats,
                    filename=filename,
                    user_id=str(user_id),
                )
                await crud_log_analysis.update_analysis_result(
                    db,
                    record=record,
                    status="complete",
                    **analysis,
                )
                log.info(
                    "log_analysis_saved",
                    record_id=str(record_id),
                    severity=analysis.get("severity"),
                )
            except (RuntimeError, ValueError) as exc:
                # Known errors: missing API key, rate limit
                log.warning("log_analysis_known_error", error=str(exc))
                await crud_log_analysis.update_analysis_result(
                    db,
                    record=record,
                    status="error",
                    ai_error=str(exc)[:1000],
                )
            except Exception as exc:
                log.exception("log_analysis_unexpected_error", error=str(exc))
                await crud_log_analysis.update_analysis_result(
                    db,
                    record=record,
                    status="error",
                    ai_error=f"Unexpected error: {type(exc).__name__}: {str(exc)[:800]}",
                )

            await db.commit()
        except Exception:
            log.exception("log_analysis_background_commit_failed")
            await db.rollback()


# ---------------------------------------------------------------------------
# POST /logs/upload
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a log file and trigger AI analysis",
)
async def upload_log(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Accepts a .log, .txt, or .json file up to 10 MB.

    Responds immediately with the new record (status = "analyzing").
    AI analysis runs in the background; poll GET /logs/{id} for results.
    """
    filename = file.filename or "unknown.log"
    content = await file.read()

    log.info(
        "log_upload_received",
        user_id=str(current_user.id),
        filename=filename,
        size=len(content),
    )

    # ── 1. Validate ────────────────────────────────────────────────────
    try:
        file_type = validate_file(filename, content)
    except LogValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ── 2. Parse ───────────────────────────────────────────────────────
    entries, stats = parse_log_file(content, file_type)

    # ── 3. Persist ─────────────────────────────────────────────────────
    record = await crud_log_analysis.create(
        db,
        user_id=current_user.id,
        filename=filename,
        file_size_bytes=len(content),
        file_type=file_type,
        total_lines=stats["total_lines"],
        error_count=stats["error_count"],
        warning_count=stats["warning_count"],
        critical_count=stats["critical_count"],
        info_count=stats["info_count"],
        parsed_entries=entries,
    )

    log.info(
        "log_upload_persisted",
        record_id=str(record.id),
        total_lines=stats["total_lines"],
    )

    # ── 4. Kick off background analysis ────────────────────────────────
    background_tasks.add_task(
        _run_analysis,
        record_id=record.id,
        user_id=current_user.id,
        entries=entries,
        stats=stats,
        filename=filename,
    )

    return UploadResponse(
        id=record.id,
        filename=record.filename,
        file_size_bytes=record.file_size_bytes,
        file_type=record.file_type,
        stats=LogStats(**stats),
        status=record.status,
        created_at=record.created_at,
    )


# ---------------------------------------------------------------------------
# GET /logs/history
# ---------------------------------------------------------------------------


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="List all log analyses for the current user",
)
async def list_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> HistoryResponse:
    records = await crud_log_analysis.list_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    total = await crud_log_analysis.count_by_user(db, user_id=current_user.id)
    return HistoryResponse(
        items=[AnalysisListItem.model_validate(r) for r in records],
        total=total,
    )


# ---------------------------------------------------------------------------
# GET /logs/{id}
# ---------------------------------------------------------------------------


@router.get(
    "/{record_id}",
    response_model=AnalysisResponse,
    summary="Get a single log analysis by ID",
)
async def get_analysis(
    record_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    record = await crud_log_analysis.get(db, record_id=record_id, user_id=current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log analysis not found.",
        )

    response = AnalysisResponse.model_validate(record)
    # Deserialise JSON → ParsedLogEntry objects
    response.parsed_entries = [ParsedLogEntry(**e) for e in (record.parsed_entries or [])]
    return response


# ---------------------------------------------------------------------------
# DELETE /logs/{id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a log analysis",
)
async def delete_analysis(
    record_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud_log_analysis.delete(db, record_id=record_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log analysis not found.",
        )
    log.info("log_analysis_deleted", record_id=str(record_id))
