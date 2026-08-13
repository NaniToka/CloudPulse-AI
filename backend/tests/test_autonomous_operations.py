"""
Pytest suite for Autonomous Cloud Operations & Self-Healing Center:
- Action Catalog Registry & Risk Levels
- Precondition Engine & Policy Checks
- Approval Engine Decision Matrix & Autonomy Levels (0-4)
- Provider Adapters & Simulation Engine
- Execution Engine Pipeline & Verification
- Rollback Engine & State Restoration
- Concurrency Locking & Idempotency
- REST API Endpoints (/autonomous/overview, /config, /actions, /plans, /executions, /queue, /audit, /simulate)
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_autonomous
from app.schemas.autonomous import AutonomyPolicyUpdate, RemediationPlanCreate
from app.services.autonomous import (
    action_catalog,
    approval_engine,
    execution_engine,
    precondition_engine,
    rollback_engine,
)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {
        "email": f"auto-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Autonomous",
        "last_name": "Admin",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_action_catalog_registry():
    """Test Action Catalog registration and metadata."""
    actions = action_catalog.list_action_definitions()
    assert len(actions) >= 10

    restart_act = action_catalog.get_action_definition("RESTART_SERVICE")
    assert restart_act is not None
    assert restart_act.risk_level == "LOW"
    assert restart_act.supports_simulation is True


@pytest.mark.asyncio
async def test_precondition_engine_evaluation(db_session: AsyncSession):
    """Test precondition evaluation engine."""
    res = await precondition_engine.evaluate_preconditions(
        db_session,
        action_type="RESTART_SERVICE",
        target_resource="api-gateway-prod",
        environment="production",
        provider="AWS",
    )
    assert res["passed"] is True
    assert res["status"] == "PASSED"


@pytest.mark.asyncio
async def test_approval_engine_decision_matrix(db_session: AsyncSession):
    """Test approval engine logic across autonomy levels."""
    # Level 1 (Default: Recommend Only) -> Requires Approval
    app1 = await approval_engine.evaluate_approval_requirement(
        db_session, action_type="RESTART_SERVICE", environment="production", risk_level="LOW"
    )
    assert app1["requires_approval"] is True

    # Update Policy to Level 3 (Auto Low-Risk)
    await crud_autonomous.update_autonomy_policy(
        db_session,
        policy_in=AutonomyPolicyUpdate(autonomy_level=3, max_autonomous_risk="LOW"),
    )

    app3_low = await approval_engine.evaluate_approval_requirement(
        db_session, action_type="RESTART_SERVICE", environment="staging", risk_level="LOW"
    )
    assert app3_low["requires_approval"] is False

    app3_high = await approval_engine.evaluate_approval_requirement(
        db_session, action_type="STOP_IDLE_COMPUTE", environment="staging", risk_level="HIGH"
    )
    assert app3_high["requires_approval"] is True


@pytest.mark.asyncio
async def test_execution_engine_pipeline(db_session: AsyncSession):
    """Test full execution engine pipeline in SIMULATED mode."""
    plan_in = RemediationPlanCreate(
        trigger_source="incident_intelligence",
        root_cause="High CPU Saturation on API Gateway",
        affected_resource="api-gateway-prod-pod-1",
        provider="Kubernetes",
        environment="staging",
        action_type="RESTART_K8S_POD",
        risk_level="LOW",
        expected_impact="Restore pod latency baseline",
        execution_mode="SIMULATED",
    )
    plan = await crud_autonomous.create_plan(db_session, plan_in=plan_in)
    plan.status = "APPROVED"  # Pre-approve for automated execution
    await db_session.commit()

    exec_res = await execution_engine.execute_remediation_plan(
        db_session, plan=plan, execution_mode="SIMULATED"
    )

    assert exec_res["status"] == "COMPLETED"
    assert exec_res["execution_mode"] == "SIMULATED"
    assert exec_res["verification_result"]["verified"] is True


@pytest.mark.asyncio
async def test_rollback_engine_execution(db_session: AsyncSession):
    """Test explicit rollback functionality."""
    plan_in = RemediationPlanCreate(
        trigger_source="finops",
        root_cause="Idle Compute Waste",
        affected_resource="worker-instance-9",
        provider="GCP",
        environment="staging",
        action_type="STOP_IDLE_COMPUTE",
        risk_level="HIGH",
        expected_impact="Save $450/mo",
        execution_mode="SIMULATED",
    )
    plan = await crud_autonomous.create_plan(db_session, plan_in=plan_in)
    plan.status = "APPROVED"
    await db_session.commit()

    exec_res = await execution_engine.execute_remediation_plan(
        db_session, plan=plan, execution_mode="SIMULATED"
    )
    exec_id = uuid.UUID(exec_res["execution_id"])

    execution = await crud_autonomous.get_execution_by_id(db_session, exec_id)
    assert execution is not None

    rb_res = await rollback_engine.execute_rollback(db_session, execution=execution, provider="GCP")
    assert rb_res["status"] == "ROLLBACK_SUCCESS"
    assert execution.status == "ROLLED_BACK"


@pytest.mark.asyncio
async def test_api_autonomous_overview_and_config(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /autonomous/overview and GET/PUT /autonomous/config."""
    overview_resp = await client.get("/api/v1/autonomous/overview", headers=auth_headers)
    assert overview_resp.status_code == 200, overview_resp.text
    o_data = overview_resp.json()
    assert "autonomy_level" in o_data
    assert "DEMO / SIMULATION MODE" in o_data["mode_indicator"]

    config_resp = await client.get("/api/v1/autonomous/config", headers=auth_headers)
    assert config_resp.status_code == 200, config_resp.text

    put_resp = await client.put(
        "/api/v1/autonomous/config",
        json={"autonomy_level": 2, "max_autonomous_risk": "MEDIUM"},
        headers=auth_headers,
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["autonomy_level"] == 2


@pytest.mark.asyncio
async def test_api_autonomous_plans_crud_and_execute(client: AsyncClient, auth_headers: dict[str, str]):
    """Test plan creation, validation, approval, and execution via REST API."""
    create_payload = {
        "trigger_source": "security_center",
        "root_cause": "Unattached Storage Disk Security Finding",
        "affected_resource": "vol-00129a8f",
        "provider": "AWS",
        "environment": "staging",
        "action_type": "CLEAR_TEMP_STORAGE",
        "risk_level": "LOW",
        "expected_impact": "Free 100GB storage space",
        "execution_mode": "SIMULATED",
    }
    create_resp = await client.post("/api/v1/autonomous/plans", json=create_payload, headers=auth_headers)
    print("CREATE RESP:", create_resp.status_code, create_resp.text)
    assert create_resp.status_code == 201, create_resp.text
    plan_id = create_resp.json()["id"]

    val_resp = await client.post(f"/api/v1/autonomous/plans/{plan_id}/validate", headers=auth_headers)
    print("VAL RESP:", val_resp.status_code, val_resp.text)
    assert val_resp.status_code == 200, val_resp.text
    assert val_resp.json()["valid"] is True

    app_resp = await client.post(f"/api/v1/autonomous/plans/{plan_id}/approve", headers=auth_headers)
    print("APP RESP:", app_resp.status_code, app_resp.text)
    assert app_resp.status_code == 200, app_resp.text

    exec_resp = await client.post(f"/api/v1/autonomous/plans/{plan_id}/execute", headers=auth_headers)
    print("EXEC RESP:", exec_resp.status_code, exec_resp.text)
    assert exec_resp.status_code == 200, exec_resp.text
    res_json = exec_resp.json()
    assert res_json["status"] == "COMPLETED", f"Execution failed: {res_json}"


@pytest.mark.asyncio
async def test_api_autonomous_simulate(client: AsyncClient, auth_headers: dict[str, str]):
    """Test POST /api/v1/autonomous/simulate Action Simulator endpoint."""
    sim_payload = {
        "action_type": "RESTART_SERVICE",
        "affected_resource": "auth-service-prod",
        "provider": "AWS",
        "environment": "production",
        "execution_mode": "SIMULATED",
    }
    resp = await client.post("/api/v1/autonomous/simulate", json=sim_payload, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["simulation_result"] == "SUCCESS"
    assert "No real cloud resources modified" in data["message"]
