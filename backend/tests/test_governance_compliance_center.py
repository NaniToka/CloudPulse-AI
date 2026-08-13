"""
Pytest Suite for Enterprise Cloud Governance & Compliance Center:
- Policy Evaluation Engine & Resource Rules
- Compliance Score Calculation (passing/applicable * 100)
- Compliance Framework Control Mappings (CIS, SOC 2, ISO 27001, NIST, PCI DSS)
- Overall Governance Posture Scoring & Rating
- Domain Governance Integrations (Cost, Security, SRE, K8s)
- Remediation Recommendation Generation
- Governance Trend Calculations (7d, 30d, 90d)
- REST API Endpoints (/governance/overview, /governance/policies, /governance/frameworks, /governance/evaluations, /governance/violations, /governance/recommendations, /governance/audit, /governance/trends, /governance/evaluate, /governance/analyze)
- Violation Status Transitions (ACKNOWLEDGED, WAIVED, RESOLVED) & Audit Trail
"""

import uuid

import pytest
from httpx import AsyncClient

from app.services.governance_engine import (
    calculate_compliance_score,
    calculate_governance_posture,
    calculate_governance_trends,
    evaluate_domain_governance,
    evaluate_governance_policy,
    generate_governance_remediations,
    get_compliance_framework_mappings,
    get_local_governance_fixture_resources,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"govuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Governance",
        "last_name": "Admin",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_policy_evaluation_engine():
    """Verify policy evaluation against local fixture resources."""
    resources = get_local_governance_fixture_resources()
    assert len(resources) >= 4

    policy = {
        "name": "Public Storage Access Disabled",
        "rule_identifier": "GOV-SEC-001",
        "category": "Security",
        "severity": "CRITICAL",
        "provider": "Multi-Cloud",
    }
    evals = evaluate_governance_policy(policy, resources)
    assert len(evals) >= 1
    failing = [e for e in evals if e["status"] == "FAIL"]
    assert len(failing) >= 1
    assert "public" in failing[0]["evidence"].lower()


@pytest.mark.asyncio
async def test_compliance_scoring_engine():
    """Verify compliance score calculation and severity distribution."""
    sample_evals = [
        {"status": "PASS", "severity": "HIGH"},
        {"status": "PASS", "severity": "MEDIUM"},
        {"status": "FAIL", "severity": "CRITICAL"},
        {"status": "FAIL", "severity": "HIGH"},
        {"status": "WARNING", "severity": "LOW"},
    ]
    res = calculate_compliance_score(sample_evals)
    assert res["compliance_score"] == 40.0
    assert res["passing_controls"] == 2
    assert res["failing_controls"] == 2
    assert res["critical_violations"] == 1


@pytest.mark.asyncio
async def test_compliance_framework_control_mappings():
    """Verify framework mapping to CIS, SOC 2, ISO 27001, NIST, PCI DSS."""
    sample_evals = [{"status": "FAIL", "severity": "CRITICAL"}]
    fw_list = get_compliance_framework_mappings(sample_evals)
    assert len(fw_list) == 5
    names = {f["framework"] for f in fw_list}
    assert "CIS Controls" in names
    assert "SOC 2 Type II" in names
    assert "ISO/IEC 27001" in names
    assert "NIST SP 800-53" in names
    assert "PCI DSS" in names
    assert fw_list[0]["disclaimer"] == "Internal Control Mapping — Not a Certification"


@pytest.mark.asyncio
async def test_overall_governance_posture():
    """Verify posture calculation and rating classification."""
    posture = calculate_governance_posture(
        compliance_score=85.0,
        critical_violations=1,
        security_violations_count=2,
        cost_violations_count=1,
        sre_violations_count=0,
        k8s_violations_count=1,
    )
    assert posture["score"] >= 0.0 and posture["score"] <= 100.0
    assert posture["rating"] in ("EXCELLENT", "GOOD", "AT_RISK", "CRITICAL")
    assert "Weighted formula" in posture["scoring_methodology"]


@pytest.mark.asyncio
async def test_domain_governance_integration():
    """Verify domain breakdown for Cost, Security, SRE, and Kubernetes governance."""
    resources = get_local_governance_fixture_resources()
    domain_gov = evaluate_domain_governance(resources)
    assert "cost_governance" in domain_gov
    assert "security_governance" in domain_gov
    assert "sre_governance" in domain_gov
    assert "kubernetes_governance" in domain_gov
    assert domain_gov["security_governance"]["public_resources_count"] >= 1


@pytest.mark.asyncio
async def test_remediation_engine_and_trends():
    """Verify remediation generation and trend calculations."""
    violations = [
        {
            "id": str(uuid.uuid4()),
            "resource_name": "s3-public-bucket",
            "severity": "CRITICAL",
            "category": "Security",
            "evidence": "Public access enabled",
            "recommended_action": "Disable public access",
        }
    ]
    rems = generate_governance_remediations(violations)
    assert len(rems) == 1
    assert rems[0]["workflow_automation_supported"] is True

    trends = calculate_governance_trends(history_days=30)
    assert len(trends["compliance_trend"]) >= 3
    assert trends["horizon_days"] == 30


# ── REST API Integration Tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_get_governance_overview(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/governance/overview."""
    resp = await client.get("/api/v1/governance/overview", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "governance_score" in data
    assert "compliance_score" in data
    assert "Local Governance Data" in data["data_source"]


@pytest.mark.asyncio
async def test_api_governance_policies_crud(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET, POST, and PUT /api/v1/governance/policies."""
    get_resp = await client.get("/api/v1/governance/policies", headers=auth_headers)
    assert get_resp.status_code == 200, get_resp.text
    assert len(get_resp.json()["policies"]) >= 1

    create_payload = {
        "name": "Custom Unencrypted Disk Prevention",
        "description": "Prevent unencrypted EBS block storage creation",
        "category": "Security",
        "severity": "HIGH",
        "provider": "AWS",
        "resource_type": "ec2_ebs",
        "rule_identifier": f"GOV-CUSTOM-{uuid.uuid4().hex[:6].upper()}",
        "enabled": True,
    }
    create_resp = await client.post("/api/v1/governance/policies", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["name"] == "Custom Unencrypted Disk Prevention"

    policy_id = created["id"]
    update_resp = await client.put(
        f"/api/v1/governance/policies/{policy_id}",
        json={"severity": "CRITICAL", "enabled": False},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_api_get_frameworks_evaluations_violations(client: AsyncClient, auth_headers: dict[str, str]):
    """Test frameworks, evaluations, and violations endpoints."""
    fw_resp = await client.get("/api/v1/governance/frameworks", headers=auth_headers)
    assert fw_resp.status_code == 200, fw_resp.text
    assert len(fw_resp.json()["frameworks"]) == 5

    eval_resp = await client.get("/api/v1/governance/evaluations", headers=auth_headers)
    assert eval_resp.status_code == 200, eval_resp.text
    assert len(eval_resp.json()["evaluations"]) >= 1

    viol_resp = await client.get("/api/v1/governance/violations", headers=auth_headers)
    assert viol_resp.status_code == 200, viol_resp.text
    assert "violations" in viol_resp.json()


@pytest.mark.asyncio
async def test_api_violation_status_transition_and_audit(client: AsyncClient, auth_headers: dict[str, str]):
    """Test violation status transition and audit trail recording."""
    # First trigger evaluation sweep to populate violations
    eval_resp = await client.post("/api/v1/governance/evaluate", headers=auth_headers)
    assert eval_resp.status_code == 200, eval_resp.text

    viol_resp = await client.get("/api/v1/governance/violations", headers=auth_headers)
    assert viol_resp.status_code == 200, viol_resp.text
    violations = viol_resp.json()["violations"]
    assert len(violations) >= 1

    viol_id = violations[0]["id"]
    status_resp = await client.patch(
        f"/api/v1/governance/violations/{viol_id}/status",
        json={"status": "ACKNOWLEDGED", "reason": "Acknowledged by SecOps team during sprint review."},
        headers=auth_headers,
    )
    assert status_resp.status_code == 200, status_resp.text
    assert status_resp.json()["status"] == "ACKNOWLEDGED"

    audit_resp = await client.get("/api/v1/governance/audit", headers=auth_headers)
    assert audit_resp.status_code == 200, audit_resp.text
    assert "audit_events" in audit_resp.json()


@pytest.mark.asyncio
async def test_api_recommendations_trends_and_analyze(client: AsyncClient, auth_headers: dict[str, str]):
    """Test recommendations, trends, and AI analysis endpoints."""
    recs_resp = await client.get("/api/v1/governance/recommendations", headers=auth_headers)
    assert recs_resp.status_code == 200, recs_resp.text
    assert "remediations" in recs_resp.json()

    trends_resp = await client.get("/api/v1/governance/trends?days=30", headers=auth_headers)
    assert trends_resp.status_code == 200, trends_resp.text
    assert "compliance_trend" in trends_resp.json()

    analyze_resp = await client.post("/api/v1/governance/analyze", headers=auth_headers)
    assert analyze_resp.status_code == 200, analyze_resp.text
    data = analyze_resp.json()
    assert "executive_summary" in data
    assert "analysis_engine" in data
