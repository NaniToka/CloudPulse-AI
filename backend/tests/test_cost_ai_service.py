"""
Unit tests for Cost AI Service (Gemini JSON extraction & fallback response).
"""

from app.services.cost_ai_service import _build_fallback_cost_analysis, _extract_json


def test_extract_json_finops_response():
    raw = """
    Here is your cloud cost analysis:
    ```json
    {
      "cost_summary": "High spending on idle dev VM instances.",
      "highest_cost_services": ["GKE", "Compute Engine"],
      "idle_resources": ["dev-vm-1"],
      "wasted_resources": ["unattached-disk-2"],
      "optimization_suggestions": ["Delete dev-vm-1"],
      "reserved_instance_recommendations": ["3-yr CUD on GKE"],
      "auto_scaling_recommendations": ["Set target CPU to 75%"],
      "estimated_monthly_savings": 5400.0,
      "recommendations": []
    }
    ```
    """
    extracted = _extract_json(raw)
    assert extracted["estimated_monthly_savings"] == 5400.0
    assert "GKE" in extracted["highest_cost_services"]


def test_build_fallback_cost_analysis():
    overview = {
        "monthly_cost": 50000.0,
        "potential_savings": 12000.0,
        "efficiency_score": 76,
    }
    fallback = _build_fallback_cost_analysis(overview)
    assert fallback["estimated_monthly_savings"] == 12000.0
    assert fallback["efficiency_score"] == 76
    assert len(fallback["highest_cost_services"]) > 0
