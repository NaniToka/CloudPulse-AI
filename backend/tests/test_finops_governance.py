"""
Pytest suite for FinOps Governance & Cost Control Center:
- Cost Policy CRUD, Enable/Disable, Evaluation
- Policy Violations Lifecycle
- Policy Exception Request & Approval Workflow
- Controlled Remediation (Request, Approve, Execute SIMULATED, Rollback)
- Deterministic Governance Score Calculation
- Audit Trail Logging
- API Endpoints (/finops/governance/overview, /score, /policies, /violations, /exceptions, /remediations, /audit)
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.services.finops_governance_engine import (
    calculate_finops_governance_score,
    evaluate_condition,
    simulate_remediation_execution,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"finopsgov-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "FinOps",
        "last_name": "Governor",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_evaluate_condition_logic():
    """Verify numeric operator comparison logic."""
    assert evaluate_condition(5000.0, ">", 4000.0) is True
    assert evaluate_condition(3000.0, ">", 4000.0) is False
    assert evaluate_condition(100.0, "<=", 100.0) is True
    assert evaluate_condition(10.0, "==", 10.0) is True


@pytest.mark.asyncio
async def test_governance_score_calculation():
    """Verify deterministic FinOps Governance Score computation."""
    res = calculate_finops_governance_score(
        policies=[1, 2, 3, 4],
        violations=[],
        potential_savings=5000.0,
        total_spend=50000.0,
    )
    assert "overall_score" in res
    assert res["overall_score"] >= 80
    assert res["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert len(res["components"]) == 4


@pytest.mark.asyncio
async def test_remediation_simulation_modes():
    """Verify remediation dry-run, simulated, and live payload generation."""
    dry_res = simulate_remediation_execution(
        action_type="stop_idle_compute",
        resource_name="dev-vm-1",
        provider="aws",
        estimated_savings=1200.0,
        execution_mode="DRY_RUN",
    )
    assert "[DRY_RUN]" in dry_res["result_message"]

    sim_res = simulate_remediation_execution(
        action_type="stop_idle_compute",
        resource_name="dev-vm-1",
        provider="aws",
        estimated_savings=1200.0,
        execution_mode="SIMULATED",
    )
    assert "SIMULATED:" in sim_res["result_message"]
    assert "original_config" in sim_res
    assert "rollback_config" in sim_res


@pytest.mark.asyncio
async def test_api_governance_overview_and_score(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/finops/governance/overview and /score."""
    score_resp = await client.get("/api/v1/finops/governance/score", headers=auth_headers)
    assert score_resp.status_code == 200, score_resp.text
    assert "overall_score" in score_resp.json()

    overview_resp = await client.get("/api/v1/finops/governance/overview", headers=auth_headers)
    assert overview_resp.status_code == 200, overview_resp.text
    data = overview_resp.json()
    assert "total_policies" in data
    assert "mode_indicator" in data
    assert "DEMO / LOCAL MODE" in data["mode_indicator"]


@pytest.mark.asyncio
async def test_api_policies_crud_and_status(client: AsyncClient, auth_headers: dict[str, str]):
    """Test Policy CRUD endpoints under /api/v1/finops/policies."""
    # List default seeded policies
    list_resp = await client.get("/api/v1/finops/policies", headers=auth_headers)
    assert list_resp.status_code == 200, list_resp.text
    policies = list_resp.json()["policies"]
    assert len(policies) >= 1

    # Create policy
    create_payload = {
        "name": "Kubernetes Prod Compute Budget Cap",
        "description": "Cap K8s cluster spend at $12,000/mo.",
        "category": "KUBERNETES",
        "provider": "kubernetes",
        "scope": "production",
        "metric": "monthly_spend",
        "operator": ">",
        "threshold_value": 12000.0,
        "severity": "HIGH",
        "enabled": True,
    }
    create_resp = await client.post("/api/v1/finops/policies", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    policy_id = created["id"]
    assert created["name"] == "Kubernetes Prod Compute Budget Cap"

    # Get single policy
    get_resp = await client.get(f"/api/v1/finops/policies/{policy_id}", headers=auth_headers)
    assert get_resp.status_code == 200, get_resp.text

    # Update policy
    update_resp = await client.put(
        f"/api/v1/finops/policies/{policy_id}",
        json={"threshold_value": 15000.0},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["threshold_value"] == 15000.0

    # Toggle policy status (Disable)
    toggle_resp = await client.patch(
        f"/api/v1/finops/policies/{policy_id}/status?enabled=false",
        headers=auth_headers,
    )
    assert toggle_resp.status_code == 200, toggle_resp.text
    assert toggle_resp.json()["enabled"] is False

    # Delete policy
    del_resp = await client.delete(f"/api/v1/finops/policies/{policy_id}", headers=auth_headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_api_policy_evaluation_and_violations(client: AsyncClient, auth_headers: dict[str, str]):
    """Test policy evaluation trigger and violation status updates."""
    # Create a policy with low threshold to guarantee violation trigger
    create_payload = {
        "name": "Strict Zero Spend Policy",
        "description": "Trigger violation for any spend",
        "category": "SPENDING",
        "provider": "all",
        "scope": "all",
        "metric": "monthly_spend",
        "operator": ">=",
        "threshold_value": 0.0,
        "severity": "CRITICAL",
        "enabled": True,
    }
    create_resp = await client.post("/api/v1/finops/policies", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    pol_id = create_resp.json()["id"]

    # Evaluate policy
    eval_resp = await client.post(f"/api/v1/finops/policies/{pol_id}/evaluate", headers=auth_headers)
    assert eval_resp.status_code == 200, eval_resp.text

    # List violations
    viol_resp = await client.get("/api/v1/finops/violations", headers=auth_headers)
    assert viol_resp.status_code == 200, viol_resp.text
    violations = viol_resp.json()["violations"]
    assert len(violations) >= 1

    viol_id = violations[0]["id"]
    # Update violation status
    status_resp = await client.patch(
        f"/api/v1/finops/violations/{viol_id}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=auth_headers,
    )
    assert status_resp.status_code == 200, status_resp.text
    assert status_resp.json()["status"] == "ACKNOWLEDGED"


@pytest.mark.asyncio
async def test_api_policy_exceptions_workflow(client: AsyncClient, auth_headers: dict[str, str]):
    """Test Exception Creation & Approval workflow."""
    pol_resp = await client.get("/api/v1/finops/policies", headers=auth_headers)
    pol_id = pol_resp.json()["policies"][0]["id"]

    # Create exception request
    exp_date = (datetime.now(UTC) + timedelta(days=30)).isoformat()
    exc_payload = {
        "policy_id": pol_id,
        "scope": "production",
        "reason": "Quarterly analytics workload expansion exception",
        "expiration_date": exp_date,
    }
    create_exc = await client.post("/api/v1/finops/exceptions", json=exc_payload, headers=auth_headers)
    assert create_exc.status_code == 201, create_exc.text
    created_exc = create_exc.json()
    exc_id = created_exc["id"]

    # Approve exception
    app_resp = await client.patch(
        f"/api/v1/finops/exceptions/{exc_id}",
        json={"status": "APPROVED", "approved_by": "lead-finops@example.com"},
        headers=auth_headers,
    )
    assert app_resp.status_code == 200, app_resp.text
    assert app_resp.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_api_remediation_workflow_and_rollback(client: AsyncClient, auth_headers: dict[str, str]):
    """Test Remediation workflow (Request -> Approve -> Execute SIMULATED -> Rollback)."""
    # 1. List remediations
    rem_resp = await client.get("/api/v1/finops/remediations", headers=auth_headers)
    assert rem_resp.status_code == 200, rem_resp.text
    remediations = rem_resp.json()["remediations"]
    assert len(remediations) >= 1

    rem_id = remediations[0]["id"]

    # 2. Approve remediation request
    approve_resp = await client.post(
        f"/api/v1/finops/remediations/{rem_id}/approve",
        json={"status": "APPROVED"},
        headers=auth_headers,
    )
    assert approve_resp.status_code == 200, approve_resp.text
    assert approve_resp.json()["approval_status"] == "APPROVED"

    # 3. Execute remediation in SIMULATED mode
    exec_resp = await client.post(
        f"/api/v1/finops/remediations/{rem_id}/execute",
        json={"execution_mode": "SIMULATED"},
        headers=auth_headers,
    )
    assert exec_resp.status_code == 200, exec_resp.text
    executed = exec_resp.json()
    assert executed["approval_status"] == "EXECUTED"
    assert "SIMULATED:" in executed["execution_result"]

    # 4. Rollback remediation
    rb_resp = await client.post(f"/api/v1/finops/remediations/{rem_id}/rollback", headers=auth_headers)
    assert rb_resp.status_code == 200, rb_resp.text
    rolled_back = rb_resp.json()
    assert rolled_back["approval_status"] == "ROLLED_BACK"
    assert "[SIMULATED ROLLBACK]" in rolled_back["execution_result"]


@pytest.mark.asyncio
async def test_api_audit_trail(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/finops/audit endpoint."""
    # Perform an action to create an audit log
    await client.post(
        "/api/v1/finops/policies",
        json={
            "name": "Audit Trail Test Policy",
            "category": "SPENDING",
            "provider": "aws",
            "scope": "all",
            "metric": "monthly_spend",
            "threshold_value": 5000.0,
        },
        headers=auth_headers,
    )

    resp = await client.get("/api/v1/finops/audit", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "audit_logs" in data
    assert len(data["audit_logs"]) >= 1
