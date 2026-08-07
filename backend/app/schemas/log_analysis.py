"""
Pydantic schemas for the Log Analyzer module.

UploadResponse      — returned immediately after file upload + parse
AnalysisResponse    — full record including AI analysis results
AnalysisListItem    — compact row for the history list
HistoryResponse     — paginated history wrapper
ParsedLogEntry      — one log line as parsed by the log parser service
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Shared sub-schemas
# ---------------------------------------------------------------------------


class ParsedLogEntry(BaseModel):
    """One log line as returned in parsed_entries."""

    line_number: int
    timestamp: str | None = None
    level: str  # ERROR | WARN | WARNING | CRITICAL | INFO | DEBUG | UNKNOWN
    service: str | None = None
    message: str
    raw: str  # original unparsed line


class LogStats(BaseModel):
    """Aggregate counts from the parsed file."""

    total_lines: int
    error_count: int
    warning_count: int
    critical_count: int
    info_count: int


# ---------------------------------------------------------------------------
# Upload response (returned synchronously — AI analysis is async)
# ---------------------------------------------------------------------------


class UploadResponse(BaseModel):
    """Returned immediately after POST /logs/upload."""

    id: uuid.UUID
    filename: str
    file_size_bytes: int
    file_type: str
    stats: LogStats
    status: str  # "analyzing" — AI is running in the background
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Full analysis record
# ---------------------------------------------------------------------------


class AnalysisResponse(BaseModel):
    """Full record returned from GET /logs/{id}."""

    id: uuid.UUID
    filename: str
    file_size_bytes: int
    file_type: str
    status: str  # pending | analyzing | complete | error

    # Stats
    total_lines: int
    error_count: int
    warning_count: int
    critical_count: int
    info_count: int

    # Log entries (capped at 500 for the viewer)
    parsed_entries: list[ParsedLogEntry] = []

    # AI output — null until status == "complete"
    executive_summary: str | None = None
    root_cause: str | None = None
    severity: str | None = None
    recommended_fixes: str | None = None
    preventive_measures: str | None = None
    confidence_score: float | None = None
    ai_error: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# History list item (compact)
# ---------------------------------------------------------------------------


class AnalysisListItem(BaseModel):
    """Compact row for the history list — no parsed_entries to keep it light."""

    id: uuid.UUID
    filename: str
    file_size_bytes: int
    file_type: str
    status: str
    total_lines: int
    error_count: int
    warning_count: int
    critical_count: int
    info_count: int
    severity: str | None = None
    confidence_score: float | None = None
    executive_summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    items: list[AnalysisListItem]
    total: int
