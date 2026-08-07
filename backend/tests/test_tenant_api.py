"""
API tests for Multi-Tenant SaaS Architecture (Organizations, Teams, Projects, Members, RBAC).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"tenantuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Tenant",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_organization_crud(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Create Org
    org_payload = {"name": "Test Acme Enterprise", "plan": "Enterprise"}
    create_resp = await client.post("/api/v1/organizations", json=org_payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    org = create_resp.json()

    assert "id" in org
    assert org["name"] == "Test Acme Enterprise"
    assert "slug" in org

    # List Orgs
    list_resp = await client.get("/api/v1/organizations", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    orgs = list_resp.json()
    assert len(orgs) > 0

    # Get Org Audit Logs
    audit_resp = await client.get(f"/api/v1/organizations/{org['id']}/audit-logs", headers=headers)
    assert audit_resp.status_code == 200, audit_resp.text


@pytest.mark.asyncio
async def test_teams_and_projects(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Get user org
    list_resp = await client.get("/api/v1/organizations", headers=headers)
    org_id = list_resp.json()[0]["id"]

    # Create Team
    team_payload = {
        "organization_id": org_id,
        "name": "Security Ops Team",
        "description": "CSPM response team",
    }
    t_resp = await client.post("/api/v1/teams", json=team_payload, headers=headers)
    assert t_resp.status_code == 201, t_resp.text
    team = t_resp.json()
    assert team["name"] == "Security Ops Team"

    # Create Project
    proj_payload = {
        "organization_id": org_id,
        "team_id": team["id"],
        "name": "Staging Kubernetes Cluster",
        "cloud_provider": "GCP",
        "environment": "Staging",
        "region": "us-central1",
    }
    p_resp = await client.post("/api/v1/projects", json=proj_payload, headers=headers)
    assert p_resp.status_code == 201, p_resp.text
    proj = p_resp.json()
    assert proj["cloud_provider"] == "GCP"


@pytest.mark.asyncio
async def test_member_invitation_and_permissions(client: AsyncClient):
    headers = await get_auth_headers(client)

    list_resp = await client.get("/api/v1/organizations", headers=headers)
    org_id = list_resp.json()[0]["id"]

    # Invite Member
    invite_payload = {
        "organization_id": org_id,
        "email": f"invitee-{uuid.uuid4().hex[:6]}@example.com",
        "role": "Admin",
    }
    inv_resp = await client.post("/api/v1/members/invite", json=invite_payload, headers=headers)
    assert inv_resp.status_code == 201, inv_resp.text
    inv = inv_resp.json()
    assert inv["role"] == "Admin"

    # List Permissions Matrix
    perm_resp = await client.get("/api/v1/members/permissions", headers=headers)
    assert perm_resp.status_code == 200, perm_resp.text
    matrix = perm_resp.json()
    assert "Owner" in matrix
    assert "Engineer" in matrix
