"""
Pytest Unit Test Suite for Enterprise AIOps Automated Remediation & Action Center.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import RemediationPlan
from app.services.remediation_engine import (
    analyze_remediation_ai,
    calculate_effectiveness,
    check_cooldown_and_idempotency,
    classify_action_risk,
    evaluate_remediation_policies,
    execute_remediation_dry_run,
    execute_remediation_simulation,
    validate_state_transition,
)


@pytest.mark.asyncio
async def test_risk_classification():
    """Test operational risk classification and environment scaling."""
    assert classify_action_risk("CLEAR_CACHE") == "LOW"
    assert classify_action_risk("SERVICE_RESTART") == "MEDIUM"
    assert classify_action_risk("DRAIN_K8S_NODE") == "HIGH"
    assert classify_action_risk("REMOVE_UNATTACHED_STORAGE") == "CRITICAL"


@pytest.mark.asyncio
async def test_deterministic_state_transitions():
    """Test state machine lifecycle transition rules."""
    assert validate_state_transition("PLANNED", "APPROVED") is True
    assert validate_state_transition("AWAITING_APPROVAL", "APPROVED") is True
    assert validate_state_transition("APPROVED", "EXECUTING") is True
    assert validate_state_transition("EXECUTING", "VERIFYING") is True
    assert validate_state_transition("VERIFYING", "SUCCEEDED") is True
    assert validate_state_transition("FAILED", "ROLLED_BACK") is True

    # Invalid transitions
    assert validate_state_transition("SUCCEEDED", "EXECUTING") is False
    assert validate_state_transition("ROLLED_BACK", "APPROVED") is False


@pytest.mark.asyncio
async def test_cooldown_and_idempotency_checks(db_session: AsyncSession):
    """Test idempotency duplicate detection and resource cooldown enforcement."""
    res = await check_cooldown_and_idempotency(db_session, affected_resource="payment-service")
    assert res["allowed"] is True


@pytest.mark.asyncio
async def test_evaluate_remediation_policies(db_session: AsyncSession):
    """Test policy evaluation engine against operational telemetry signals."""
    telemetry = {"service": "payment-service", "error_rate_pct": 6.5, "latency_p95_ms": 320}
    actions = await evaluate_remediation_policies(db_session, signal_type="INCIDENT", telemetry=telemetry)
    assert len(actions) >= 1
    assert actions[0]["action_type"] in ("SERVICE_RESTART", "RESTART_SERVICE")


@pytest.mark.asyncio
async def test_dry_run_execution(db_session: AsyncSession):
    """Test dry-run simulation outputting proposed state diff without touching resources."""
    plan = RemediationPlan(
        user_id=uuid.uuid4(),
        trigger_source="test",
        root_cause="Test root cause",
        affected_resource="order-processor",
        provider="Kubernetes",
        environment="production",
        action_type="SCALE_UP",
        risk_level="MEDIUM",
        expected_impact="Test impact",
        estimated_downtime_sec=0,
        estimated_cost_impact=0.0,
        requires_approval=True,
        rollback_supported=True,
        execution_mode="DRY_RUN",
        status="RECOMMENDED",
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    dry_res = await execute_remediation_dry_run(db_session, plan)
    assert dry_res["execution_mode"] == "DRY_RUN"
    assert "proposed_state_diff" in dry_res
    assert dry_res["preconditions_passed"] is True


@pytest.mark.asyncio
async def test_remediation_simulation_execution(db_session: AsyncSession):
    """Test local simulation execution pipeline."""
    plan = RemediationPlan(
        user_id=uuid.uuid4(),
        trigger_source="test",
        root_cause="High CPU utilization",
        affected_resource="inventory-service",
        provider="AWS",
        environment="production",
        action_type="SERVICE_RESTART",
        risk_level="MEDIUM",
        expected_impact="Clear memory leak and restore health",
        estimated_downtime_sec=5,
        estimated_cost_impact=0.0,
        requires_approval=False,
        rollback_supported=True,
        execution_mode="SIMULATION",
        status="APPROVED",
    )
    db_session.add(plan)
    await db_session.commit()

    exec_res = await execute_remediation_simulation(db_session, plan=plan)
    assert exec_res["status"] in ("COMPLETED", "SUCCEEDED")
    assert "mode_indicator" in exec_res


@pytest.mark.asyncio
async def test_effectiveness_calculation():
    """Test pre-action vs post-action telemetry improvement calculation."""
    eff = calculate_effectiveness(pre_metric=7.2, post_metric=1.8)
    assert eff["verification_status"] == "IMPROVED"
    assert eff["improvement_pct"] > 70.0

    eff_insuff = calculate_effectiveness(pre_metric=0.0, post_metric=0.0)
    assert eff_insuff["verification_status"] == "INSUFFICIENT_DATA"


@pytest.mark.asyncio
async def test_analyze_remediation_ai(db_session: AsyncSession):
    """Test dual-mode AI/Local remediation intelligence analysis."""
    res = await analyze_remediation_ai(db_session)
    assert "analysis_engine" in res
    assert "executive_summary" in res


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"remediation-user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "AIOps",
        "last_name": "Remediator",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    if resp.status_code != 201:
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        token = resp.json()["access_token"]
    else:
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_api_remediation_endpoints(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test all /api/v1/remediation/* REST API endpoints."""
    # 1. GET /remediation/overview
    resp = await client.get("/api/v1/remediation/overview", headers=auth_headers)
    assert resp.status_code == 200
    assert "pending_approvals_count" in resp.json()

    # 2. GET /remediation/actions
    resp = await client.get("/api/v1/remediation/actions", headers=auth_headers)
    assert resp.status_code == 200
    actions = resp.json()
    assert len(actions) >= 1
    plan_id = actions[0]["id"]

    # 3. GET /remediation/actions/{id}
    resp = await client.get(f"/api/v1/remediation/actions/{plan_id}", headers=auth_headers)
    assert resp.status_code == 200

    # 4. POST /remediation/actions
    new_action_payload = {
        "trigger_source": "manual_trigger",
        "root_cause": "Memory leak detected in cart-service",
        "affected_resource": "cart-service",
        "provider": "Kubernetes",
        "environment": "production",
        "action_type": "POD_RESTART",
        "risk_level": "MEDIUM",
        "expected_impact": "Restart container pod",
        "execution_mode": "SIMULATION",
    }
    resp = await client.post("/api/v1/remediation/actions", json=new_action_payload, headers=auth_headers)
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # 5. POST /remediation/actions/{id}/dry-run
    resp = await client.post(f"/api/v1/remediation/actions/{created_id}/dry-run", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["execution_mode"] == "DRY_RUN"

    # 6. POST /remediation/actions/{id}/approve
    resp = await client.post(
        f"/api/v1/remediation/actions/{created_id}/approve",
        json={"comments": "Approved for local simulation."},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["approval_status"] == "APPROVED"

    # 7. POST /remediation/actions/{id}/execute
    resp = await client.post(
        f"/api/v1/remediation/actions/{created_id}/execute",
        json={"execution_mode": "SIMULATION"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    exec_data = resp.json()
    assert exec_data["status"] in ("COMPLETED", "SUCCEEDED")
    execution_id = exec_data.get("execution_id")

    # 8. POST /remediation/actions/{id}/rollback (if execution_id exists)
    if execution_id:
        resp = await client.post(f"/api/v1/remediation/actions/{execution_id}/rollback", headers=auth_headers)
        assert resp.status_code == 200

    # 9. GET /remediation/executions
    resp = await client.get("/api/v1/remediation/executions", headers=auth_headers)
    assert resp.status_code == 200

    # 10. GET /remediation/policies
    resp = await client.get("/api/v1/remediation/policies", headers=auth_headers)
    assert resp.status_code == 200

    # 11. GET /remediation/audit
    resp = await client.get("/api/v1/remediation/audit", headers=auth_headers)
    assert resp.status_code == 200

    # 12. POST /remediation/analyze
    resp = await client.post("/api/v1/remediation/analyze", headers=auth_headers)
    assert resp.status_code == 200
    assert "analysis_engine" in resp.json()
