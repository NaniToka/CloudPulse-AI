"""
Log analysis service — calls Gemini with a structured SRE prompt and
returns a strongly-typed analysis result.

The analysis result is a dict with these keys:
  executive_summary   str
  root_cause          str
  severity            str   (critical | high | medium | low)
  recommended_fixes   str   (Markdown bullet list)
  preventive_measures str   (Markdown bullet list)
  confidence_score    float (0.0 – 1.0)

The function raises:
  RuntimeError   if GEMINI_API_KEY is not configured
  ValueError     if rate-limited (re-uses ai_service rate_limiter)
  Exception      from Gemini SDK, propagated to the endpoint for clean 502
"""

from __future__ import annotations

import re
from typing import Any

import structlog

from app.core.config import settings
from app.services.ai_service import rate_limiter  # reuse existing limiter
from app.services.log_parser import format_entries_for_prompt

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are an expert Site Reliability Engineering (SRE) analyst.

You will receive a parsed server log file.  Your task is to analyse it and
return a structured JSON object — nothing else, no markdown fences, no
commentary outside the JSON.

The JSON object must have exactly these keys:

{
  "executive_summary":   "<2–4 sentence high-level summary for a non-technical audience>",
  "root_cause":          "<concise technical root-cause explanation>",
  "severity":            "<one of: critical | high | medium | low>",
  "recommended_fixes":   "<numbered list of concrete remediation steps>",
  "preventive_measures": "<numbered list of preventive actions>",
  "confidence_score":    <float between 0.0 and 1.0>
}

Rules:
- severity = critical  if there are P0-level errors that could cause data loss or full outage
- severity = high      if the errors could degrade service for a significant portion of users
- severity = medium    if the errors are isolated or non-critical
- severity = low       if there are only warnings or informational anomalies
- confidence_score reflects how confident you are given the available evidence
- Never fabricate specific metric values you were not given
- Always recommend testing fixes in a staging environment first
- Keep all field values plain text or simple numbered lists — no markdown headers
"""

# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

_JSON_RE = re.compile(r"\{[\s\S]+\}", re.MULTILINE)


def _extract_json(text: str) -> dict[str, Any]:
    """
    Extract and parse the first JSON object from the model response.
    Handles models that sometimes wrap JSON in markdown fences.
    """
    import json

    # Remove markdown fences if present
    cleaned = re.sub(r"```(?:json)?", "", text).strip()

    match = _JSON_RE.search(cleaned)
    if not match:
        raise ValueError(f"Model returned no JSON object: {text[:200]!r}")

    return json.loads(match.group(0))


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalise_severity(raw: str) -> str:
    raw = raw.lower().strip()
    if raw in ("critical", "high", "medium", "low"):
        return raw
    if raw in ("error", "fatal"):
        return "critical"
    if raw in ("warning", "warn"):
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyse_logs(
    entries: list[dict[str, Any]],
    stats: dict[str, int],
    filename: str,
    user_id: str,
) -> dict[str, Any]:
    """
    Send parsed log entries to Gemini and return a structured analysis dict.

    Parameters
    ----------
    entries  : parsed log entries (from log_parser.parse_log_file)
    stats    : aggregate statistics dict
    filename : original uploaded filename (for context)
    user_id  : used by the rate limiter

    Returns
    -------
    dict with keys: executive_summary, root_cause, severity,
                    recommended_fixes, preventive_measures, confidence_score
    """
    if not rate_limiter.is_allowed(user_id):
        raise ValueError(
            "Rate limit exceeded. Please wait before analysing another log."
        )

    import google.generativeai as genai  # lazy import — no startup failure

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ("your_key_here", ""):
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Set it in backend/.env to enable AI log analysis."
        )

    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config={
            "temperature": 0.2,          # low temp for deterministic JSON
            "max_output_tokens": 2048,
            "top_p": 0.9,
        },
        system_instruction=_SYSTEM_PROMPT,
    )

    log_text = format_entries_for_prompt(entries)

    user_prompt = (
        f"Filename: {filename}\n"
        f"Total lines: {stats['total_lines']}\n"
        f"ERROR: {stats['error_count']}, "
        f"WARNING: {stats['warning_count']}, "
        f"CRITICAL: {stats['critical_count']}, "
        f"INFO: {stats['info_count']}\n\n"
        f"=== LOG ENTRIES ===\n{log_text}"
    )

    log.info(
        "log_analysis_request",
        user_id=user_id,
        filename=filename,
        total_lines=stats["total_lines"],
        prompt_chars=len(user_prompt),
    )

    response = await model.generate_content_async(user_prompt)
    raw_text: str = response.text

    result = _extract_json(raw_text)

    # Normalise and validate each field
    analysis = {
        "executive_summary": str(result.get("executive_summary", "")).strip()[:4000],
        "root_cause": str(result.get("root_cause", "")).strip()[:4000],
        "severity": _normalise_severity(str(result.get("severity", "low"))),
        "recommended_fixes": str(result.get("recommended_fixes", "")).strip()[:4000],
        "preventive_measures": str(result.get("preventive_measures", "")).strip()[:4000],
        "confidence_score": _clamp(result.get("confidence_score", 0.5)),
    }

    log.info(
        "log_analysis_complete",
        user_id=user_id,
        filename=filename,
        severity=analysis["severity"],
        confidence=analysis["confidence_score"],
    )
    return analysis
