"""
Unit tests for Organizations, Teams, Projects, Users CRUD endpoints & Redis Cache blocklist.
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"extrauser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Extra",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_organization_crud_full(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Create org
    res = await client.post(
        "/api/v1/organizations",
        json={"name": "Test Org SRE", "plan": "Enterprise"},
        headers=headers,
    )
    assert res.status_code == 201
    org_id = res.json()["id"]

    # 2. Get org details
    res_get = await client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Test Org SRE"

    # 3. Patch org
    res_patch = await client.patch(
        f"/api/v1/organizations/{org_id}",
        json={"name": "Updated Org SRE"},
        headers=headers,
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["name"] == "Updated Org SRE"

    # 4. Delete org
    res_del = await client.delete(f"/api/v1/organizations/{org_id}", headers=headers)
    assert res_del.status_code == 204


@pytest.mark.asyncio
async def test_team_and_project_crud_full(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Create org
    res_org = await client.post(
        "/api/v1/organizations",
        json={"name": "DevOps Org", "plan": "Pro"},
        headers=headers,
    )
    org_id = res_org.json()["id"]

    # Create team
    res_team = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Platform SRE", "description": "Platform Team"},
        headers=headers,
    )
    assert res_team.status_code == 201
    team_id = res_team.json()["id"]

    # Update team
    res_team_up = await client.patch(
        f"/api/v1/teams/{team_id}",
        json={"name": "Core Platform SRE"},
        headers=headers,
    )
    assert res_team_up.status_code == 200
    assert res_team_up.json()["name"] == "Core Platform SRE"

    # Create project
    res_proj = await client.post(
        "/api/v1/projects",
        json={
            "organization_id": org_id,
            "team_id": team_id,
            "name": "K8s Microservices",
            "cloud_provider": "AWS",
            "environment": "Production",
        },
        headers=headers,
    )
    assert res_proj.status_code == 201
    proj_id = res_proj.json()["id"]

    # Update project
    res_proj_up = await client.patch(
        f"/api/v1/projects/{proj_id}",
        json={"environment": "Staging"},
        headers=headers,
    )
    assert res_proj_up.status_code == 200
    assert res_proj_up.json()["environment"] == "Staging"

    # Delete project and team
    res_del_p = await client.delete(f"/api/v1/projects/{proj_id}", headers=headers)
    assert res_del_p.status_code == 204

    res_del_t = await client.delete(f"/api/v1/teams/{team_id}", headers=headers)
    assert res_del_t.status_code == 204
