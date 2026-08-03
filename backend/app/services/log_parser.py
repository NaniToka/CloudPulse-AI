"""
Log parser service.

Responsibilities
----------------
- Validate uploaded file: extension, MIME-like heuristic, size.
- Parse .log / .txt / .json files into a normalised list of ParsedLogEntry
  dicts, extracting level, timestamp, service, and message fields.
- Return aggregate statistics (error/warning/critical/info counts).

Design decisions
----------------
- Pure functions — no I/O, no DB; easy to unit-test.
- The parser is deliberately lenient: any line that does not match a known
  pattern is tagged UNKNOWN rather than dropped.
- JSON log files are expected to be a JSON array of objects OR one JSON
  object per line (JSON-lines / NDJSON format).
- Cap at MAX_ENTRIES for storage and LLM prompt size.
"""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_BYTES: int = 10 * 1024 * 1024    # 10 MB
MAX_ENTRIES: int = 500                     # rows stored in DB / sent to Gemini
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".log", ".txt", ".json"})

# Common log level keywords (upper-cased comparison)
_LEVEL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("CRITICAL", re.compile(r"\b(critical|crit|fatal)\b", re.I)),
    ("ERROR",    re.compile(r"\b(error|err|exception|traceback)\b", re.I)),
    ("WARNING",  re.compile(r"\b(warn(?:ing)?)\b", re.I)),
    ("INFO",     re.compile(r"\b(info(?:rmation)?)\b", re.I)),
    ("DEBUG",    re.compile(r"\b(debug|trace|verbose)\b", re.I)),
]

# Timestamp patterns (ISO-8601, common log formats)
_TS_RE = re.compile(
    r"""
    (?:
        \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?
        |
        \d{2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}
        |
        \w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}
    )
    """,
    re.VERBOSE,
)

# Structured log line: "[TIMESTAMP] [LEVEL] [SERVICE] message"
_STRUCTURED_RE = re.compile(
    r"""
    ^
    (?:\[?(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\]\s]*)\]?\s+)?
    (?:\[?(?P<level>CRITICAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE|FATAL)\]?\s+)?
    (?:\[(?P<service>[A-Za-z0-9._-]{2,40})\]\s+|(?:(?P<service_nobracket>[A-Za-z0-9._-]{2,40})\s+[-:]\s+))?
    (?P<message>.+)
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class LogValidationError(ValueError):
    """Raised when the uploaded file fails validation."""


def validate_file(filename: str, content: bytes) -> str:
    """
    Validate the uploaded log file.

    Returns the normalised extension ("log" | "txt" | "json").
    Raises LogValidationError on any failure.
    """
    lower = filename.lower()
    ext = ""
    for allowed in ALLOWED_EXTENSIONS:
        if lower.endswith(allowed):
            ext = allowed.lstrip(".")
            break

    if not ext:
        raise LogValidationError(
            f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}."
        )

    if len(content) == 0:
        raise LogValidationError("File is empty.")

    if len(content) > MAX_FILE_BYTES:
        mb = MAX_FILE_BYTES // (1024 * 1024)
        raise LogValidationError(f"File exceeds the {mb} MB size limit.")

    return ext


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _detect_level_from_text(text: str) -> str:
    """Heuristically detect log level from arbitrary text."""
    for level, pattern in _LEVEL_PATTERNS:
        if pattern.search(text):
            return level
    return "UNKNOWN"


def _parse_text_line(line: str, line_number: int) -> dict[str, Any]:
    """Parse a single plain-text / .log line."""
    stripped = line.rstrip("\r\n")
    if not stripped.strip():
        return {}   # blank line — skip

    ts_match = _TS_RE.search(stripped)
    timestamp = ts_match.group(0) if ts_match else None

    struct_match = _STRUCTURED_RE.match(stripped)
    if struct_match:
        level = (struct_match.group("level") or "").upper()
        if level in ("WARN",):
            level = "WARNING"
        service = struct_match.group("service") or struct_match.group("service_nobracket")
        message = struct_match.group("message").strip()
    else:
        level = ""
        service = None
        message = stripped

    if not level:
        level = _detect_level_from_text(stripped)

    return {
        "line_number": line_number,
        "timestamp": timestamp,
        "level": level or "UNKNOWN",
        "service": service,
        "message": message,
        "raw": stripped,
    }


def _parse_json_entry(obj: Any, line_number: int) -> dict[str, Any]:
    """Parse a single JSON log object (dict)."""
    if not isinstance(obj, dict):
        raw = json.dumps(obj)
        return {
            "line_number": line_number,
            "timestamp": None,
            "level": _detect_level_from_text(raw),
            "service": None,
            "message": raw[:500],
            "raw": raw[:1000],
        }

    # Try common field names
    level_raw = (
        obj.get("level") or obj.get("severity") or obj.get("log_level") or ""
    )
    level = str(level_raw).upper()
    if level in ("WARN",):
        level = "WARNING"
    if level not in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"):
        level = _detect_level_from_text(json.dumps(obj))

    timestamp = (
        obj.get("timestamp")
        or obj.get("time")
        or obj.get("@timestamp")
        or obj.get("ts")
    )

    service = (
        obj.get("service")
        or obj.get("logger")
        or obj.get("source")
        or obj.get("component")
    )

    message = (
        obj.get("message")
        or obj.get("msg")
        or obj.get("text")
        or json.dumps(obj)
    )

    return {
        "line_number": line_number,
        "timestamp": str(timestamp) if timestamp else None,
        "level": level or "UNKNOWN",
        "service": str(service)[:100] if service else None,
        "message": str(message)[:2000],
        "raw": json.dumps(obj)[:2000],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_log_file(
    content: bytes,
    file_type: str,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Parse log file content into normalised entries + aggregate statistics.

    Returns
    -------
    entries : list[dict]   — up to MAX_ENTRIES parsed log entries
    stats   : dict[str, int] — total_lines, error_count, warning_count,
                               critical_count, info_count
    """
    text = content.decode("utf-8", errors="replace")
    entries: list[dict[str, Any]] = []
    stats = {
        "total_lines": 0,
        "error_count": 0,
        "warning_count": 0,
        "critical_count": 0,
        "info_count": 0,
    }

    if file_type == "json":
        entries, stats = _parse_json(text)
    else:
        entries, stats = _parse_text(text)

    log.info(
        "log_parsed",
        file_type=file_type,
        total_lines=stats["total_lines"],
        errors=stats["error_count"],
        warnings=stats["warning_count"],
    )
    return entries[:MAX_ENTRIES], stats


def _parse_text(text: str) -> tuple[list[dict], dict[str, int]]:
    lines = text.splitlines()
    entries: list[dict] = []
    stats = {
        "total_lines": len(lines),
        "error_count": 0,
        "warning_count": 0,
        "critical_count": 0,
        "info_count": 0,
    }
    for i, line in enumerate(lines, start=1):
        entry = _parse_text_line(line, i)
        if not entry:
            continue
        _update_stats(stats, entry["level"])
        entries.append(entry)
    return entries, stats


def _parse_json(text: str) -> tuple[list[dict], dict[str, int]]:
    entries: list[dict] = []
    stats = {"total_lines": 0, "error_count": 0, "warning_count": 0,
             "critical_count": 0, "info_count": 0}

    # Try JSON array first
    stripped = text.strip()
    if stripped.startswith("["):
        try:
            objects = json.loads(stripped)
            if isinstance(objects, list):
                stats["total_lines"] = len(objects)
                for i, obj in enumerate(objects, start=1):
                    entry = _parse_json_entry(obj, i)
                    _update_stats(stats, entry["level"])
                    entries.append(entry)
                return entries, stats
        except json.JSONDecodeError:
            pass  # fall through to NDJSON

    # NDJSON / one object per line
    lines = [l for l in text.splitlines() if l.strip()]
    stats["total_lines"] = len(lines)
    for i, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            obj = {"message": line, "level": "UNKNOWN"}
        entry = _parse_json_entry(obj, i)
        _update_stats(stats, entry["level"])
        entries.append(entry)
    return entries, stats


def _update_stats(stats: dict[str, int], level: str) -> None:
    level = level.upper()
    if level == "ERROR":
        stats["error_count"] += 1
    elif level == "WARNING":
        stats["warning_count"] += 1
    elif level == "CRITICAL":
        stats["critical_count"] += 1
    elif level == "INFO":
        stats["info_count"] += 1


# ---------------------------------------------------------------------------
# Prompt formatting helper (used by analysis service)
# ---------------------------------------------------------------------------

def format_entries_for_prompt(
    entries: list[dict[str, Any]],
    max_chars: int = 12_000,
) -> str:
    """
    Format parsed log entries into a compact text block for the Gemini prompt.

    Only includes ERROR, CRITICAL, and WARNING lines (plus the first 20 INFO
    lines for context).  Truncates if the total would exceed max_chars.
    """
    priority: list[dict] = []
    info_added = 0

    for e in entries:
        level = e.get("level", "UNKNOWN")
        if level in ("ERROR", "CRITICAL", "WARNING"):
            priority.append(e)
        elif level == "INFO" and info_added < 20:
            priority.append(e)
            info_added += 1

    lines: list[str] = []
    total = 0
    for e in priority:
        ts = f"[{e['timestamp']}] " if e.get("timestamp") else ""
        svc = f"[{e['service']}] " if e.get("service") else ""
        line = f"L{e['line_number']:04d}  {ts}{e['level']:8s}  {svc}{e['message']}"
        if total + len(line) > max_chars:
            lines.append("... [truncated]")
            break
        lines.append(line)
        total += len(line)

    return "\n".join(lines) if lines else "(no entries parsed)"
