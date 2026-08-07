"""
API Unit tests for Multi-Cloud Observability endpoints (AWS, Azure, GCP).
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"clouduser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Cloud",
        "last_name": "Architect",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_cloud_accounts_api(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List accounts (triggers default seed)
    res_list = await client.get("/api/v1/cloud/accounts", headers=headers)
    assert res_list.status_code == 200, res_list.text
    accounts = res_list.json()
    assert len(accounts) > 0

    # 2. Connect new AWS account
    acc_payload = {
        "name": "AWS Secondary Staging",
        "provider": "AWS",
        "account_id": "9876-5432-1098",
        "credentials_type": "role_arn",
        "credentials_meta": {"role_arn": "arn:aws:iam::987654321098:role/StagingRole"},
        "default_region": "us-west-2",
        "environment": "staging",
    }
    res_conn = await client.post("/api/v1/cloud/accounts", json=acc_payload, headers=headers)
    assert res_conn.status_code == 201, res_conn.text
    new_acc = res_conn.json()
    assert new_acc["name"] == "AWS Secondary Staging"


@pytest.mark.asyncio
async def test_cloud_resources_and_observability_api(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List resources
    res_r = await client.get("/api/v1/cloud/resources", headers=headers)
    assert res_r.status_code == 200, res_r.text
    resources = res_r.json()
    assert len(resources) > 0

    # 2. Get cost breakdown
    res_cost = await client.get("/api/v1/cloud/cost", headers=headers)
    assert res_cost.status_code == 200, res_cost.text
    cost_data = res_cost.json()
    assert "total_monthly_spend" in cost_data
    assert "provider_breakdown" in cost_data

    # 3. Get security summary
    res_sec = await client.get("/api/v1/cloud/security", headers=headers)
    assert res_sec.status_code == 200, res_sec.text
    sec_data = res_sec.json()
    assert "overall_compliance_score" in sec_data

    # 4. Get health summary & Gemini AI recommendations
    res_health = await client.get("/api/v1/cloud/health", headers=headers)
    assert res_health.status_code == 200, res_health.text
    health_data = res_health.json()
    assert "health_score_percent" in health_data
    assert len(health_data["ai_insights"]) > 0

    # 5. Trigger sync
    res_sync = await client.post("/api/v1/cloud/sync", headers=headers)
    assert res_sync.status_code == 200, res_sync.text
    assert res_sync.json()["status"] == "success"
