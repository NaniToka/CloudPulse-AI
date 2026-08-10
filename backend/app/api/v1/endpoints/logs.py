"""
Log Analyzer endpoints.

Routes
------
POST   /api/v1/logs/upload        — Upload a log file, trigger AI root-cause analysis
GET    /api/v1/logs/history       — List all analyses for the current user
GET    /api/v1/logs/{id}          — Get full analysis by ID
DELETE /api/v1/logs/{id}          — Delete one analysis record
GET    /api/v1/logs/{id}/pdf      — Download analysis as an official PDF report
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, UploadFile, status
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
from app.services.log_parser import parse_log_file
from app.services.pdf_report_service import generate_log_analysis_pdf
from app.utils.log_security import decode_log_bytes, validate_log_upload

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Background task: run Gemini analysis, update DB row
# ---------------------------------------------------------------------------


async def _run_analysis(
    record_id: uuid.UUID,
    user_id: uuid.UUID,
    entries: list[dict],
    filename: str,
) -> None:
    """
    Background coroutine: executes RCA synthesis and updates database.
    """
    from app.db.session import AsyncSessionLocal  # noqa: PLC0415

    async with AsyncSessionLocal() as db:
        try:
            record = await crud_log_analysis.get(db, record_id=record_id, user_id=user_id)
            if not record:
                log.warning("log_analysis_record_missing", record_id=str(record_id))
                return

            try:
                analysis = await analyse_logs(
                    parsed_entries=entries,
                    filename=filename,
                )
                await crud_log_analysis.update_analysis_result(
                    db,
                    record=record,
                    status="complete",
                    executive_summary=analysis.get("executive_summary"),
                    root_cause=analysis.get("root_cause"),
                    severity=analysis.get("severity"),
                    recommended_fixes=analysis.get("recommended_fixes"),
                    preventive_measures=analysis.get("preventive_measures"),
                    confidence_score=analysis.get("confidence_score"),
                )
                log.info(
                    "log_analysis_completed_successfully",
                    record_id=str(record_id),
                    severity=analysis.get("severity"),
                    engine=analysis.get("engine_used"),
                )
            except Exception as exc:
                log.exception("log_analysis_pipeline_error", error=str(exc))
                await crud_log_analysis.update_analysis_result(
                    db,
                    record=record,
                    status="error",
                    ai_error=f"Analysis pipeline error: {str(exc)[:800]}",
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
    summary="Upload a server log file and trigger AI analysis",
)
async def upload_log(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Accepts a .log, .txt, or .json file up to 10 MB.
    Validates extension, MIME type, parses entries, persists record,
    and initiates automated AI root-cause analysis in the background.
    """
    raw_filename = file.filename or "server.log"
    content_bytes = await file.read()
    file_size = len(content_bytes)

    # 1. Security & MIME validation
    clean_filename, file_type = validate_log_upload(
        filename=raw_filename,
        content_type=file.content_type,
        file_size=file_size,
    )

    log.info(
        "log_upload_validated",
        user_id=str(current_user.id),
        filename=clean_filename,
        size_bytes=file_size,
    )

    # 2. Decode and parse log file
    decoded_text = decode_log_bytes(content_bytes)
    entries, stats = parse_log_file(decoded_text.encode("utf-8"), file_type)

    # 3. Persist record in database
    record = await crud_log_analysis.create(
        db,
        user_id=current_user.id,
        filename=clean_filename,
        file_size_bytes=file_size,
        file_type=file_type,
        total_lines=stats["total_lines"],
        error_count=stats["error_count"],
        warning_count=stats["warning_count"],
        critical_count=stats["critical_count"],
        info_count=stats["info_count"],
        parsed_entries=entries,
    )

    # 4. Kick off background analysis
    background_tasks.add_task(
        _run_analysis,
        record_id=record.id,
        user_id=current_user.id,
        entries=entries,
        filename=clean_filename,
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
            detail="Log analysis record not found.",
        )

    response = AnalysisResponse.model_validate(record)
    parsed = []
    for e in (record.parsed_entries or []):
        if isinstance(e, dict):
            entry_data = dict(e)
            if "raw" not in entry_data or entry_data["raw"] is None:
                entry_data["raw"] = entry_data.get("message", "")
            parsed.append(ParsedLogEntry(**entry_data))
    response.parsed_entries = parsed
    return response


# ---------------------------------------------------------------------------
# GET /logs/{id}/pdf
# ---------------------------------------------------------------------------


@router.get(
    "/{record_id}/pdf",
    summary="Download log analysis report as a formatted PDF",
)
async def download_analysis_pdf(
    record_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    record = await crud_log_analysis.get(db, record_id=record_id, user_id=current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log analysis record not found.",
        )

    data = {
        "filename": record.filename,
        "created_at": record.created_at,
        "severity": record.severity,
        "confidence_score": record.confidence_score,
        "total_lines": record.total_lines,
        "error_count": record.error_count,
        "warning_count": record.warning_count,
        "critical_count": record.critical_count,
        "executive_summary": record.executive_summary,
        "root_cause": record.root_cause,
        "recommended_fixes": record.recommended_fixes,
        "preventive_measures": record.preventive_measures,
        "parsed_entries": record.parsed_entries,
    }

    try:
        pdf_bytes = generate_log_analysis_pdf(data)
    except Exception as exc:
        log.exception("pdf_generation_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF report.",
        ) from exc

    safe_name = record.filename.replace(" ", "_").replace("/", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="CloudPulse_Log_Analysis_{safe_name}.pdf"',
            "Cache-Control": "no-cache",
        },
    )


# ---------------------------------------------------------------------------
# DELETE /logs/{id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a log analysis record",
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
            detail="Log analysis record not found.",
        )
    log.info("log_analysis_deleted", record_id=str(record_id))
