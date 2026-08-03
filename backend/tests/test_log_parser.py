"""
Unit tests for the log parser service.
"""

import pytest
from app.services.log_parser import (
    LogValidationError,
    format_entries_for_prompt,
    parse_log_file,
    validate_file,
)


def test_validate_file_valid():
    assert validate_file("server.log", b"some log line") == "log"
    assert validate_file("app.txt", b"some text line") == "txt"
    assert validate_file("data.json", b"{}") == "json"


def test_validate_file_invalid_extension():
    with pytest.raises(LogValidationError, match="Unsupported file type"):
        validate_file("file.pdf", b"content")


def test_validate_file_empty():
    with pytest.raises(LogValidationError, match="File is empty"):
        validate_file("empty.log", b"")


def test_validate_file_exceeds_size():
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    with pytest.raises(LogValidationError, match="File exceeds the 10 MB size limit"):
        validate_file("big.log", big_content)


def test_parse_text_log():
    raw_log = (
        "2026-08-03T10:00:00Z [INFO] [auth-service] User logged in\n"
        "2026-08-03T10:01:00Z [WARNING] [db-service] Slow query executed\n"
        "2026-08-03T10:02:00Z [ERROR] [api-gateway] 500 Internal Server Error\n"
        "2026-08-03T10:03:00Z [CRITICAL] [kernel] Out of memory killed process\n"
    )
    entries, stats = parse_log_file(raw_log.encode("utf-8"), "log")

    assert len(entries) == 4
    assert stats["total_lines"] == 4
    assert stats["info_count"] == 1
    assert stats["warning_count"] == 1
    assert stats["error_count"] == 1
    assert stats["critical_count"] == 1

    assert entries[2]["level"] == "ERROR"
    assert entries[2]["service"] == "api-gateway"
    assert entries[2]["message"] == "500 Internal Server Error"


def test_parse_json_log_array():
    raw_json = """[
        {"timestamp": "2026-08-03T10:00:00Z", "level": "INFO", "service": "auth", "message": "Login success"},
        {"timestamp": "2026-08-03T10:05:00Z", "level": "ERROR", "service": "payment", "message": "Gateway timeout"}
    ]"""
    entries, stats = parse_log_file(raw_json.encode("utf-8"), "json")

    assert len(entries) == 2
    assert stats["total_lines"] == 2
    assert stats["info_count"] == 1
    assert stats["error_count"] == 1
    assert entries[1]["level"] == "ERROR"
    assert entries[1]["service"] == "payment"


def test_parse_ndjson_log():
    raw_ndjson = (
        '{"timestamp": "2026-08-03T10:00:00Z", "level": "INFO", "msg": "Started"}\n'
        '{"timestamp": "2026-08-03T10:01:00Z", "level": "WARN", "msg": "High CPU"}\n'
    )
    entries, stats = parse_log_file(raw_ndjson.encode("utf-8"), "json")

    assert len(entries) == 2
    assert stats["total_lines"] == 2
    assert stats["warning_count"] == 1


def test_format_entries_for_prompt():
    entries = [
        {"line_number": 1, "timestamp": "10:00", "level": "INFO", "service": "app", "message": "Normal operation"},
        {"line_number": 2, "timestamp": "10:01", "level": "ERROR", "service": "db", "message": "Connection refused"},
    ]
    prompt_text = format_entries_for_prompt(entries)
    assert "ERROR" in prompt_text
    assert "Connection refused" in prompt_text
