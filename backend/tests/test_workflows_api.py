"""
API Unit tests for Enterprise Workflow Automation endpoints.
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"workflowuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Automation",
        "last_name": "Lead",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_workflows_full_lifecycle_api(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List Templates
    res_tpl = await client.get("/api/v1/workflows/templates", headers=headers)
    assert res_tpl.status_code == 200, res_tpl.text
    templates = res_tpl.json()
    assert len(templates) > 0

    # 2. List Workflows (triggers default seeding)
    res_list = await client.get("/api/v1/workflows", headers=headers)
    assert res_list.status_code == 200, res_list.text
    workflows = res_list.json()
    assert len(workflows) > 0
    sample_wf = workflows[0]

    # 3. Create Custom Workflow
    new_wf_payload = {
        "name": "Custom K8s Scale Down & Slack",
        "description": "Auto scale down deployment during off-peak hours.",
        "status": "active",
        "trigger_type": "cron",
        "nodes": [
            {"id": "n1", "type": "trigger", "label": "Cron Schedule (0 20 * * *)"},
            {"id": "n2", "type": "action", "label": "Scale K8s Deployment to 2 Replicas"},
            {"id": "n3", "type": "approval", "label": "DevOps Approval Gate"},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
        "tags": ["cron", "k8s", "cost-saving"],
    }
    res_create = await client.post("/api/v1/workflows", json=new_wf_payload, headers=headers)
    assert res_create.status_code == 201, res_create.text
    created_wf = res_create.json()
    assert created_wf["name"] == "Custom K8s Scale Down & Slack"
    created_id = created_wf["id"]

    # 4. Get by ID
    res_get = await client.get(f"/api/v1/workflows/{created_id}", headers=headers)
    assert res_get.status_code == 200, res_get.text

    # 5. Execute Workflow (hits approval gate)
    res_exec = await client.post(f"/api/v1/workflows/{created_id}/execute", headers=headers)
    assert res_exec.status_code == 200, res_exec.text
    execution = res_exec.json()
    assert execution["status"] == "awaiting_approval"

    # 6. Approve Workflow Gate
    approval_payload = {
        "approval_id": execution["id"],
        "decision": "approved",
        "reason": "Verified off-peak traffic by SRE Lead",
    }
    res_appr = await client.post(f"/api/v1/workflows/{created_id}/approve", json=approval_payload, headers=headers)
    assert res_appr.status_code == 200, res_appr.text
    appr_result = res_appr.json()
    assert appr_result["status"] == "completed"

    # 7. List History
    res_hist = await client.get("/api/v1/workflows/history", headers=headers)
    assert res_hist.status_code == 200, res_hist.text

    # 8. Generate Workflow with Gemini AI
    ai_prompt_payload = {
        "prompt": "When high CPU alert fires on production VM, restart container, run Gemini diagnosis, and notify Slack."
    }
    res_ai = await client.post("/api/v1/workflows/generate-ai", json=ai_prompt_payload, headers=headers)
    assert res_ai.status_code == 200, res_ai.text
    ai_wf = res_ai.json()
    assert "nodes" in ai_wf
    assert len(ai_wf["nodes"]) > 0
