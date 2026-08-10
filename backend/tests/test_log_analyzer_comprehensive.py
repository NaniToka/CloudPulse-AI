"""
Comprehensive test suite for the Log Analyzer backend subsystem.
Covers upload, security validation, parsing, deterministic RCA, PDF report generation,
and CRUD history operations.
"""

from __future__ import annotations

import io
import json
import uuid

import pytest
from httpx import AsyncClient

from app.services.log_parser import parse_log_file
from app.services.pdf_report_service import generate_log_analysis_pdf
from app.services.root_cause_engine import analyze_log_entries


def unique_payload() -> dict:
    return {
        "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Log",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_valid_log_upload(client: AsyncClient):
    """1. Test valid .log file upload and background task dispatch."""
    headers = await get_auth_headers(client)
    log_content = (
        b"2026-08-10 14:00:01 [INFO] [api-gateway] Started service\n"
        b"2026-08-10 14:00:05 [ERROR] [api-gateway] OutOfMemoryError: Java heap space\n"
        b"2026-08-10 14:00:10 [CRITICAL] [api-gateway] Pod killed by OOM killer\n"
    )
    files = {"file": ("test_server.log", log_content, "text/plain")}
    resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)

    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"] == "test_server.log"
    assert data["file_type"] == "log"
    assert data["stats"]["total_lines"] == 3
    assert data["stats"]["error_count"] == 1
    assert data["stats"]["critical_count"] == 1


@pytest.mark.asyncio
async def test_valid_json_log_upload(client: AsyncClient):
    """2. Test valid JSON array log file upload."""
    headers = await get_auth_headers(client)
    json_logs = [
        {"timestamp": "2026-08-10T14:00:00Z", "level": "INFO", "service": "auth-service", "message": "Initialized"},
        {"timestamp": "2026-08-10T14:00:05Z", "level": "ERROR", "service": "auth-service", "message": "PSQLException: Connection pool full"},
    ]
    files = {"file": ("auth.json", json.dumps(json_logs).encode("utf-8"), "application/json")}
    resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)

    assert resp.status_code == 201
    data = resp.json()
    assert data["file_type"] == "json"
    assert data["stats"]["total_lines"] == 2
    assert data["stats"]["error_count"] == 1


@pytest.mark.asyncio
async def test_invalid_extension_rejected(client: AsyncClient):
    """3. Test unsupported file extension is rejected with 422."""
    headers = await get_auth_headers(client)
    files = {"file": ("malicious.exe", b"binary content", "application/octet-stream")}
    resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)
    assert resp.status_code == 422
    assert "Unsupported file type" in (resp.json().get("detail") or resp.json().get("error") or "")


@pytest.mark.asyncio
async def test_file_too_large_rejected(client: AsyncClient):
    """4. Test file larger than 10MB is rejected with 413 or 422."""
    headers = await get_auth_headers(client)
    big_content = b"A" * (11 * 1024 * 1024)  # 11 MB
    files = {"file": ("huge.log", big_content, "text/plain")}
    resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)
    assert resp.status_code in (413, 422)
    detail_msg = resp.json().get("detail") or resp.json().get("error") or ""
    assert "exceeds maximum allowed size" in detail_msg.lower() or "too large" in detail_msg.lower() or "10mb" in detail_msg.lower()


@pytest.mark.asyncio
async def test_empty_file_rejected(client: AsyncClient):
    """5. Test empty file is rejected with 400 or 422."""
    headers = await get_auth_headers(client)
    files = {"file": ("empty.log", b"", "text/plain")}
    resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)
    assert resp.status_code in (400, 422)
    detail_msg = resp.json().get("detail") or resp.json().get("error") or ""
    assert "empty" in detail_msg.lower()


def test_log_parser_and_error_counting():
    """6 & 7. Unit test parsing and deterministic error counting."""
    raw_content = (
        b"2026-08-10 10:00:00 [INFO] [order-service] Processing order #1092\n"
        b"2026-08-10 10:00:05 [WARN] [order-service] Slow database query (latency=1400ms)\n"
        b"2026-08-10 10:00:10 [ERROR] [order-service] TimeoutException: Downstream inventory API unreachable\n"
        b"2026-08-10 10:00:15 [CRITICAL] [order-service] Transaction rollback failed: Deadlock detected\n"
    )
    entries, stats = parse_log_file(raw_content, "log")
    assert stats["total_lines"] == 4
    assert stats["error_count"] == 1
    assert stats["critical_count"] == 1
    assert stats["warning_count"] == 1
    assert stats["info_count"] == 1


def test_root_cause_engine_hypothesis():
    """8 & 9. Unit test deterministic root cause hypothesis synthesis."""
    entries = [
        {"line_number": 1, "level": "INFO", "service": "api-gateway", "message": "Inbound request", "raw": ""},
        {"line_number": 2, "level": "ERROR", "service": "api-gateway", "message": "java.lang.OutOfMemoryError: Java heap space", "raw": ""},
        {"line_number": 3, "level": "CRITICAL", "service": "api-gateway", "message": "Container killed by OOM killer", "raw": ""},
    ]
    rca = analyze_log_entries(entries)
    assert rca["severity"] == "CRITICAL"
    assert "Heap memory exhaustion" in rca["heuristic_hypothesis"]
    assert len(rca["recommended_fixes"]) > 0
    assert len(rca["preventive_measures"]) > 0


def test_pdf_report_generation():
    """10. Test ReportLab PDF report generation returns valid PDF binary."""
    sample_data = {
        "filename": "api-gateway-prod.log",
        "created_at": "2026-08-10 14:00:00 UTC",
        "severity": "CRITICAL",
        "confidence_score": 0.96,
        "total_lines": 140,
        "error_count": 18,
        "warning_count": 4,
        "critical_count": 2,
        "executive_summary": "Sustained high heap memory caused OOM kills on api-gateway.",
        "root_cause": "Session token cache retained unbounded JSON payloads.",
        "recommended_fixes": "1. Increase pod memory limits.\n2. Configure TTL cache expiration.",
        "preventive_measures": "1. Add Prometheus memory saturation alerts.",
        "parsed_entries": [
            {"line_number": 1, "level": "INFO", "service": "api-gateway", "message": "Started"},
            {"line_number": 2, "level": "ERROR", "service": "api-gateway", "message": "OutOfMemoryError"},
        ],
    }
    pdf_bytes = generate_log_analysis_pdf(sample_data)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_log_history_and_detail_flow(client: AsyncClient):
    """11, 12, 13 & 14. Test history retrieval, detail retrieval, PDF download, and deletion."""
    headers = await get_auth_headers(client)

    # 1. Fetch History
    hist_resp = await client.get("/api/v1/logs/history", headers=headers)
    assert hist_resp.status_code == 200
    items = hist_resp.json().get("items", [])
    assert len(items) > 0
    target_id = items[0]["id"]

    # 2. Get Detail
    detail_resp = await client.get(f"/api/v1/logs/{target_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == target_id
    assert len(detail_resp.json()["parsed_entries"]) > 0

    # 3. Download PDF
    pdf_resp = await client.get(f"/api/v1/logs/{target_id}/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["Content-Type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-")

    # 4. Delete Record
    del_resp = await client.delete(f"/api/v1/logs/{target_id}", headers=headers)
    assert del_resp.status_code == 204

    # 5. Verify 404 after deletion
    after_del = await client.get(f"/api/v1/logs/{target_id}", headers=headers)
    assert after_del.status_code == 404
