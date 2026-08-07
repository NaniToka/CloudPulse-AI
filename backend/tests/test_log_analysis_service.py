"""
Unit tests for log analysis service (Gemini response extraction & prompt logic).
"""

import pytest

from app.services.log_analysis_service import (
    _clamp,
    _extract_json,
    _normalise_severity,
)


def test_extract_json_valid():
    raw_response = """
    Here is the analysis:
    ```json
    {
        "executive_summary": "Database service encountered deadlocks.",
        "root_cause": "Unindexed queries caused row lock contention.",
        "severity": "critical",
        "recommended_fixes": "1. Add index on user_id\\n2. Optimize transaction boundary",
        "preventive_measures": "1. Enable slow query log",
        "confidence_score": 0.95
    }
    ```
    """
    extracted = _extract_json(raw_response)
    assert extracted["severity"] == "critical"
    assert extracted["confidence_score"] == 0.95
    assert "deadlocks" in extracted["executive_summary"]


def test_extract_json_missing():
    raw_response = "No JSON available in this response."
    with pytest.raises(ValueError, match="Model returned no JSON object"):
        _extract_json(raw_response)


def test_normalise_severity():
    assert _normalise_severity("critical") == "critical"
    assert _normalise_severity("FATAL") == "critical"
    assert _normalise_severity("warn") == "medium"
    assert _normalise_severity("unknown_level") == "low"


def test_clamp():
    assert _clamp(1.5) == 1.0
    assert _clamp(-0.2) == 0.0
    assert _clamp(0.85) == 0.85
