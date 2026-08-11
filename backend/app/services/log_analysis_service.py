"""
Log Analysis Service — Combines deterministic statistical RCA with Google Gemini AI synthesis.
"""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.core.config import settings
from app.services.ai_service import rate_limiter
from app.services.log_parser import format_entries_for_prompt
from app.services.root_cause_engine import analyze_log_entries

log = structlog.get_logger(__name__)

_SYSTEM_PROMPT = """You are an expert Site Reliability Engineering (SRE) analyst.

You will receive a parsed server log excerpt and its computed error statistics. Your task is to analyze it and return a structured JSON object.

The JSON object must have exactly these keys:

{
  "executive_summary": "<2–4 sentence high-level summary for a non-technical audience>",
  "root_cause": "<concise technical root-cause explanation grounded in the log evidence>",
  "severity": "<one of: critical | high | medium | low>",
  "recommended_fixes": "<numbered list of concrete remediation steps>",
  "preventive_measures": "<numbered list of preventive actions>",
  "confidence_score": <float between 0.0 and 1.0>
}

Rules:
- severity = critical if there are fatal crashes, data loss risks, or full outage indicators.
- severity = high if errors cause degraded latency or widespread client failure.
- severity = medium if errors are isolated or transient.
- severity = low if only warnings or normal operational anomalies exist.
- Never hallucinate infrastructure components not present in the logs.
- Keep field values plain text or simple numbered lines.
"""

_JSON_RE = re.compile(r"\{[\s\S]+\}", re.MULTILINE)


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    match = _JSON_RE.search(cleaned)
    if not match:
        raise ValueError(f"Model returned no JSON object: {text[:200]!r}")
    return json.loads(match.group(0))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalise_severity(raw: str) -> str:
    raw = raw.lower().strip()
    if raw in ("critical", "high", "medium", "low"):
        return raw
    if "crit" in raw or "fatal" in raw:
        return "critical"
    if "err" in raw or "high" in raw:
        return "high"
    if "warn" in raw or "med" in raw:
        return "medium"
    return "low"


async def analyse_logs(
    parsed_entries: list[dict[str, Any]],
    filename: str = "uploaded.log",
) -> dict[str, Any]:
    """
    Analyzes parsed log entries using deterministic root-cause heuristics
    augmented by Google Gemini AI (with fallback to local SRE engine).
    """
    # 1. Deterministic Root-Cause Analysis
    engine_stats = analyze_log_entries(parsed_entries)
    deterministic_result = {
        "executive_summary": (
            f"Automated SRE analysis of {filename} ({engine_stats['total_lines']} lines) completed. "
            f"Detected {engine_stats['critical_count']} critical and {engine_stats['error_count']} error events. "
            f"Primary assessment indicates {engine_stats['severity']} operational impact."
        ),
        "root_cause": engine_stats["heuristic_hypothesis"],
        "severity": engine_stats["severity"].lower(),
        "recommended_fixes": "\n".join(f"{i+1}. {fix}" for i, fix in enumerate(engine_stats["recommended_fixes"])),
        "preventive_measures": "\n".join(f"{i+1}. {prev}" for i, prev in enumerate(engine_stats["preventive_measures"])),
        "confidence_score": engine_stats["confidence_score"],
        "engine_used": "local",
    }

    # 2. Check if Google Gemini AI is configured
    has_gemini = bool(
        settings.GEMINI_API_KEY
        and settings.GEMINI_API_KEY.strip()
        and settings.GEMINI_API_KEY.strip() not in ("your_key_here", "your_gemini_api_key_here", "")
    )

    if not has_gemini:
        log.info("gemini_key_not_configured_using_local_rca", filename=filename)
        return deterministic_result

    # 3. Call Gemini AI with structured prompt
    try:
        from google import genai
        from google.genai import types

        await rate_limiter.acquire()

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        log_sample = format_entries_for_prompt(parsed_entries)

        prompt = (
            f"Log File: {filename}\n"
            f"Total Lines: {len(parsed_entries)}\n"
            f"Pre-computed Errors: {engine_stats['error_count']}, Warnings: {engine_stats['warning_count']}\n"
            f"Sample Log Excerpts:\n{log_sample}\n\n"
            "Analyze these logs according to the system prompt."
        )

        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.3,
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            ),
        )

        raw_text = response.text or ""
        parsed_json = _extract_json(raw_text)

        fixes = parsed_json.get("recommended_fixes")
        fixes_str = "\n".join(fixes) if isinstance(fixes, list) else str(fixes or deterministic_result["recommended_fixes"])

        prevs = parsed_json.get("preventive_measures")
        prevs_str = "\n".join(prevs) if isinstance(prevs, list) else str(prevs or deterministic_result["preventive_measures"])

        return {
            "executive_summary": str(parsed_json.get("executive_summary") or deterministic_result["executive_summary"]),
            "root_cause": str(parsed_json.get("root_cause") or deterministic_result["root_cause"]),
            "severity": _normalise_severity(str(parsed_json.get("severity") or deterministic_result["severity"])),
            "recommended_fixes": fixes_str,
            "preventive_measures": prevs_str,
            "confidence_score": _clamp(float(parsed_json.get("confidence_score") or deterministic_result["confidence_score"])),
            "engine_used": "gemini",
        }

    except Exception as exc:
        log.warning("gemini_log_analysis_failed_falling_back", error=str(exc), filename=filename)
        return deterministic_result
