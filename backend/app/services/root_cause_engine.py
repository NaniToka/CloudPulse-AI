"""
Deterministic Root Cause & Error Pattern Analysis Engine.

Performs statistical, lexical, and structural analysis on parsed log entries
BEFORE invoking external LLM / AI providers.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

# Regular expressions for error classification
_EXCEPTION_RE = re.compile(
    r"\b([A-Za-z0-9_]+(?:Exception|Error|Failure|Timeout|Fault))\b",
    re.IGNORECASE,
)
_HTTP_STATUS_RE = re.compile(r"\b(status(?:_code)?|HTTP)?\s*[:=]?\s*([1-5]\d{2})\b", re.IGNORECASE)
_ENDPOINT_RE = re.compile(r"\b(GET|POST|PUT|DELETE|PATCH|OPTIONS)\s+([/\w\-\.\:]+)\b")
_TIMEOUT_RE = re.compile(r"\b(timeout|timed\s*out|deadline\s*exceeded|connection\s*reset)\b", re.IGNORECASE)
_OOM_RE = re.compile(r"\b(out\s*of\s*memory|heap\s*space|oom|killed|memory\s*limit)\b", re.IGNORECASE)
_DB_RE = re.compile(r"\b(connection\s*pool|postgres|psql|mysql|deadlock|lock\s*wait|database)\b", re.IGNORECASE)


def analyze_log_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Computes rigorous deterministic diagnostics and metrics across parsed log entries.
    """
    total_lines = len(entries)
    if total_lines == 0:
        return {
            "total_lines": 0,
            "error_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "info_count": 0,
            "error_rate": 0.0,
            "severity": "LOW",
            "confidence_score": 0.90,
            "top_error_types": [],
            "affected_services": [],
            "affected_endpoints": [],
            "http_status_breakdown": {"4xx": 0, "5xx": 0, "other": 0},
            "timeout_count": 0,
            "evidence_snippets": [],
            "heuristic_hypothesis": "Log file is empty; no anomalies detected.",
            "recommended_fixes": ["Verify that log shipping agent is actively capturing standard output."],
            "preventive_measures": ["Implement heartbeat telemetry for application logger."],
        }

    level_counts = Counter()
    service_counts = Counter()
    exception_counts = Counter()
    endpoint_counts = Counter()
    status_4xx = 0
    status_5xx = 0
    timeout_count = 0
    oom_count = 0
    db_count = 0

    first_ts = None
    last_ts = None
    evidence_snippets = []

    for idx, e in enumerate(entries):
        level = (e.get("level") or "INFO").upper()
        if level in ("CRIT", "FATAL"):
            level = "CRITICAL"
        elif level in ("WARN", "WARNING"):
            level = "WARN"
        elif level in ("ERR", "EXCEPTION"):
            level = "ERROR"

        level_counts[level] += 1

        service = e.get("service")
        if service and service.lower() != "unknown":
            service_counts[service] += 1

        ts = e.get("timestamp")
        if ts:
            if not first_ts:
                first_ts = ts
            last_ts = ts

        msg = (e.get("message") or "") + " " + (e.get("raw") or "")

        # Exceptions
        found_exceptions = _EXCEPTION_RE.findall(msg)
        for exc in found_exceptions:
            exception_counts[exc] += 1

        # HTTP Statuses
        for _, code_str in _HTTP_STATUS_RE.findall(msg):
            code = int(code_str)
            if 400 <= code < 500:
                status_4xx += 1
            elif 500 <= code < 600:
                status_5xx += 1

        # Endpoints
        for method, path in _ENDPOINT_RE.findall(msg):
            endpoint_counts[f"{method} {path}"] += 1

        # Timeouts & OOM & DB
        if _TIMEOUT_RE.search(msg):
            timeout_count += 1
        if _OOM_RE.search(msg):
            oom_count += 1
        if _DB_RE.search(msg):
            db_count += 1

        # Collect high-value evidence lines (Errors / Criticals)
        if level in ("ERROR", "CRITICAL") and len(evidence_snippets) < 10:
            evidence_snippets.append(f"Line {e.get('line_number', idx + 1)} [{level}]: {e.get('message', '').strip()}")

    err_count = level_counts.get("ERROR", 0)
    crit_count = level_counts.get("CRITICAL", 0)
    warn_count = level_counts.get("WARN", 0) + level_counts.get("WARNING", 0)
    info_count = level_counts.get("INFO", 0) + level_counts.get("DEBUG", 0)

    error_rate = round((err_count + crit_count) / max(total_lines, 1), 4)

    # Determine Severity
    if crit_count > 0 or status_5xx > 10 or oom_count > 0:
        severity = "CRITICAL"
    elif err_count > 5 or status_5xx > 0 or timeout_count > 3:
        severity = "HIGH"
    elif err_count > 0 or warn_count > 5 or status_4xx > 10:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # Formulate Heuristic Root Cause Hypothesis
    top_service = service_counts.most_common(1)[0][0] if service_counts else "core-service"
    top_exc = exception_counts.most_common(1)[0][0] if exception_counts else None

    if oom_count > 0:
        hypothesis = (
            f"Heap memory exhaustion in '{top_service}'. Container exceeded memory allocation limits, "
            f"causing high garbage collection pause times and OOM-Kills."
        )
        remediations = [
            f"Increase container memory limits for {top_service} in deployment manifest.",
            "Profile memory allocation to eliminate unbounded cache growth or retain leaks.",
            "Tune JVM / runtime garbage collection parameters (-XX:+UseG1GC).",
        ]
        preventions = [
            "Configure Kubernetes Horizontal Pod Autoscaler with memory saturation triggers.",
            "Set up alerts for memory utilization exceeding 80%.",
        ]
    elif db_count > 0 and timeout_count > 0:
        hypothesis = (
            f"Database connection pool exhaustion and query timeouts on '{top_service}'. "
            f"Active connections saturated the pool under concurrent load."
        )
        remediations = [
            "Increase max pool size on the database connection pooler (e.g. PgBouncer / HikariCP).",
            "Audit long-running transactions and add missing database query indexes.",
            "Implement a circuit breaker to prevent cascading connection starvation.",
        ]
        preventions = [
            "Deploy connection pooling proxies between services and database.",
            "Establish strict statement timeouts on database roles.",
        ]
    elif timeout_count > 0:
        hypothesis = (
            f"Upstream communication failure or timeout surge in '{top_service}'. "
            f"Dependent downstream APIs failed to respond within configured SLA thresholds."
        )
        remediations = [
            f"Verify upstream dependency network routing and health for {top_service}.",
            "Increase client timeout and configure exponential backoff retries with jitter.",
            "Deploy fallback responses for degraded third-party API dependencies.",
        ]
        preventions = [
            "Implement distributed tracing with OpenTelemetry to track inter-service latency.",
            "Establish synthetic canary probes on upstream service endpoints.",
        ]
    elif top_exc:
        hypothesis = (
            f"Uncaught application exception '{top_exc}' encountered repeatedly in '{top_service}'."
        )
        remediations = [
            f"Inspect stack traces associated with {top_exc} and apply code-level exception handling.",
            "Deploy hotfix patch with null checks and defensive input validation.",
        ]
        preventions = [
            "Add regression test cases covering the input data causing this exception.",
            "Enable Sentry / CloudPulse APM error tracking for real-time triage.",
        ]
    elif err_count > 0:
        hypothesis = (
            f"Elevated error rate ({err_count} errors, {error_rate * 100:.1f}%) observed in '{top_service}'."
        )
        remediations = [
            "Review error log snippets and check for recent code deployments or config drifts.",
            "Roll back recent releases if errors correlate with last deployment timestamp.",
        ]
        preventions = [
            "Implement automated canary deployment verification.",
        ]
    else:
        hypothesis = "All log events reflect healthy operational status with zero critical failure signatures."
        remediations = ["No immediate corrective remediation needed."]
        preventions = ["Maintain standard monitoring and log retention policies."]

    confidence_score = min(0.98, max(0.85, round(0.85 + (0.02 * min(len(evidence_snippets), 6)), 2)))

    return {
        "total_lines": total_lines,
        "error_count": err_count,
        "warning_count": warn_count,
        "critical_count": crit_count,
        "info_count": info_count,
        "error_rate": error_rate,
        "severity": severity,
        "confidence_score": confidence_score,
        "top_error_types": [{"name": k, "count": v} for k, v in exception_counts.most_common(5)],
        "affected_services": [k for k, _ in service_counts.most_common(5)],
        "affected_endpoints": [k for k, _ in endpoint_counts.most_common(5)],
        "http_status_breakdown": {"4xx": status_4xx, "5xx": status_5xx, "other": total_lines - (status_4xx + status_5xx)},
        "timeout_count": timeout_count,
        "first_occurrence": first_ts,
        "latest_occurrence": last_ts,
        "evidence_snippets": evidence_snippets,
        "heuristic_hypothesis": hypothesis,
        "recommended_fixes": remediations,
        "preventive_measures": preventions,
    }
