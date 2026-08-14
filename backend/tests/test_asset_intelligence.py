"""
Pytest unit tests for Enterprise Cloud Asset Intelligence Center.
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.cloud_resource import CloudResource
from app.models.cloud_account import CloudAccount
from app.services.asset_intelligence_engine import (
    calculate_asset_overview,
    calculate_provider_distribution,
    get_asset_detail_by_id,
    get_asset_topology,
    get_local_demo_assets,
    get_orphaned_resources,
)


@pytest.mark.asyncio
async def test_asset_intelligence_engine_calculations():
    assets = get_local_demo_assets()
    assert len(assets) > 0

    overview = calculate_asset_overview(assets)
    assert overview.total_resources == len(assets)
    assert overview.aws_count >= 1
    assert overview.total_monthly_cost > 0.0
    assert overview.mode_indicator == "Demo / Local Asset Data"

    providers = calculate_provider_distribution(assets)
    assert len(providers.providers) > 0
    assert any(p.provider == "AWS" for p in providers.providers)

    topology = get_asset_topology(assets)
    assert len(topology.nodes) == len(assets)
    assert len(topology.edges) > 0

    orphaned = get_orphaned_resources(assets)
    assert orphaned.total_orphaned >= 1
    assert orphaned.total_potential_savings > 0.0

    detail = get_asset_detail_by_id(assets, assets[0]["id"])
    assert detail is not None
    assert detail.resource.name == assets[0]["name"]


def unique_payload() -> dict:
    return {
        "email": f"assetuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Asset",
        "last_name": "Admin",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_api_asset_intelligence_endpoints(client: AsyncClient):
    headers = await get_auth_headers(client)

    # GET /assets/overview
    resp = await client.get("/api/v1/assets/overview", headers=headers)
    assert resp.status_code == 200
    ov = resp.json()
    assert ov["total_resources"] >= 1
    assert "total_monthly_cost" in ov

    # GET /assets/resources
    resp = await client.get("/api/v1/assets/resources?provider=AWS", headers=headers)
    assert resp.status_code == 200
    res_list = resp.json()
    assert isinstance(res_list, list)
    assert len(res_list) > 0
    first_id = res_list[0]["id"]

    # GET /assets/resources/{id}
    resp = await client.get(f"/api/v1/assets/resources/{first_id}", headers=headers)
    assert resp.status_code == 200
    detail = resp.json()
    assert "resource" in detail

    # GET /assets/providers
    resp = await client.get("/api/v1/assets/providers", headers=headers)
    assert resp.status_code == 200
    assert "providers" in resp.json()

    # GET /assets/services
    resp = await client.get("/api/v1/assets/services", headers=headers)
    assert resp.status_code == 200

    # GET /assets/regions
    resp = await client.get("/api/v1/assets/regions", headers=headers)
    assert resp.status_code == 200

    # GET /assets/types
    resp = await client.get("/api/v1/assets/types", headers=headers)
    assert resp.status_code == 200

    # GET /assets/search
    resp = await client.get("/api/v1/assets/search?q=payment", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # GET /assets/topology
    resp = await client.get("/api/v1/assets/topology", headers=headers)
    assert resp.status_code == 200

    # GET /assets/orphaned
    resp = await client.get("/api/v1/assets/orphaned", headers=headers)
    assert resp.status_code == 200

    # POST /assets/discover
    resp = await client.post("/api/v1/assets/discover", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"

    # POST /assets/refresh
    resp = await client.post("/api/v1/assets/refresh", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
