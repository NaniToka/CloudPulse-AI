"""
Pytest Unit Tests for Enterprise Cloud Topology & Blast-Radius Intelligence Center.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service_dependency import ServiceDependency, ServiceNode
from app.services.cloud_topology_engine import cloud_topology_engine
from app.schemas.topology import FailureSimulationRequest


def unique_payload() -> dict:
    return {
        "email": f"topouser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Topology",
        "last_name": "Admin",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_topology_engine_calculations(db_session: AsyncSession):
    overview = await cloud_topology_engine.get_overview(db_session)
    assert overview.total_nodes > 0
    assert overview.total_edges > 0
    assert overview.total_providers >= 3

    graph = await cloud_topology_engine.get_graph(db_session)
    assert len(graph.nodes) == overview.total_nodes
    assert len(graph.edges) == overview.total_edges

    blast = await cloud_topology_engine.calculate_blast_radius(db_session, "node-order-service")
    assert blast.affected_node_count >= 1
    assert blast.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW")

    sim = await cloud_topology_engine.simulate_failure(
        db_session, FailureSimulationRequest(node_id="node-rds-postgres", failure_type="TOTAL_OUTAGE")
    )
    assert sim.is_simulation is True
    assert sim.target_node_name == "orders-rds-postgres-main"
    assert len(sim.mitigation_steps) > 0

    spofs = await cloud_topology_engine.detect_spofs(db_session)
    assert spofs.total_spofs >= 1

    paths = await cloud_topology_engine.get_dependency_paths(db_session)
    assert len(paths.paths) >= 1


@pytest.mark.asyncio
async def test_topology_api_endpoints(client: AsyncClient, db_session: AsyncSession):
    headers = await get_auth_headers(client)

    # 1. GET /overview
    resp = await client.get("/api/v1/topology/overview", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_nodes"] > 0

    # 2. GET /graph
    resp = await client.get("/api/v1/topology/graph?provider=AWS", headers=headers)
    assert resp.status_code == 200
    assert "nodes" in resp.json()

    # 3. GET /nodes
    resp = await client.get("/api/v1/topology/nodes", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    # 4. GET /edges
    resp = await client.get("/api/v1/topology/edges", headers=headers)
    assert resp.status_code == 200

    # 5. GET /services/{id}
    resp = await client.get("/api/v1/topology/services/node-order-service", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "order-service"

    # 6. GET /resources/{id}
    resp = await client.get("/api/v1/topology/resources/node-rds-postgres", headers=headers)
    assert resp.status_code == 200

    # 7. GET /dependencies/{id}
    resp = await client.get("/api/v1/topology/dependencies/edge-4", headers=headers)
    assert resp.status_code == 200

    # 8. GET /upstream/{id}
    resp = await client.get("/api/v1/topology/upstream/node-rds-postgres", headers=headers)
    assert resp.status_code == 200

    # 9. GET /downstream/{id}
    resp = await client.get("/api/v1/topology/downstream/node-api-gateway", headers=headers)
    assert resp.status_code == 200

    # 10. GET /blast-radius/{id}
    resp = await client.get("/api/v1/topology/blast-radius/node-order-service", headers=headers)
    assert resp.status_code == 200
    assert "severity" in resp.json()

    # 11. GET /spof
    resp = await client.get("/api/v1/topology/spof", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_spofs"] >= 1

    # 12. GET /paths
    resp = await client.get("/api/v1/topology/paths", headers=headers)
    assert resp.status_code == 200

    # 13. POST /simulate-failure
    sim_payload = {"node_id": "node-order-service", "failure_type": "TOTAL_OUTAGE"}
    resp = await client.post("/api/v1/topology/simulate-failure", json=sim_payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_simulation"] is True

    # 14. GET /incidents/{id}
    resp = await client.get("/api/v1/topology/incidents/inc-101", headers=headers)
    assert resp.status_code == 200
