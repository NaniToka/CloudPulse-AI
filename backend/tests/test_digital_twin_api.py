"""
API Unit tests for Digital Twin Infrastructure Platform endpoints.
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"twinuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Twin",
        "last_name": "Architect",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_digital_twin_full_lifecycle_api(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Get Digital Twin (triggers default seeding)
    res_twin = await client.get("/api/v1/twin", headers=headers)
    assert res_twin.status_code == 200, res_twin.text
    twin = res_twin.json()
    assert "health_score" in twin
    assert len(twin["virtual_resources"]) > 0

    # 2. List Twin Resources
    res_res = await client.get("/api/v1/twin/resources", headers=headers)
    assert res_res.status_code == 200, res_res.text
    resources = res_res.json()
    assert len(resources) > 0

    # 3. List Simulation Scenarios
    res_scenarios = await client.get("/api/v1/twin/simulations", headers=headers)
    assert res_scenarios.status_code == 200, res_scenarios.text
    scenarios = res_scenarios.json()
    assert len(scenarios) > 0
    sample_scenario = scenarios[0]

    # 4. Run Simulation & calculate blast radius
    res_run = await client.post(
        f"/api/v1/twin/simulations/{sample_scenario['id']}/run", headers=headers
    )
    assert res_run.status_code == 200, res_run.text
    execution = res_run.json()
    assert execution["status"] == "completed"
    assert "blast_radius" in execution
    assert execution["risk_score"] > 0

    # 5. List Simulation History
    res_hist = await client.get("/api/v1/twin/simulations/history", headers=headers)
    assert res_hist.status_code == 200, res_hist.text
    assert len(res_hist.json()) > 0

    # 6. Get Blast Radius detail
    res_blast = await client.get(
        f"/api/v1/twin/blast-radius/{sample_scenario['id']}", headers=headers
    )
    assert res_blast.status_code == 200, res_blast.text
    blast_data = res_blast.json()
    assert "financial_impact_usd" in blast_data

    # 7. Ask What-If Question to Gemini AI
    what_if_payload = {"query": "What happens if Redis primary cache fails?"}
    res_what_if = await client.post("/api/v1/twin/what-if", json=what_if_payload, headers=headers)
    assert res_what_if.status_code == 200, res_what_if.text
    what_if_res = res_what_if.json()
    assert "impact_summary" in what_if_res
    assert len(what_if_res["mitigations"]) > 0
