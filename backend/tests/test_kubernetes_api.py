"""
API Unit tests for Kubernetes & Container Intelligence endpoints.
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"k8suser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "K8s",
        "last_name": "Admin",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_kubernetes_api_endpoints(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List Clusters (triggers default seeding)
    res_clusters = await client.get("/api/v1/kubernetes/clusters", headers=headers)
    assert res_clusters.status_code == 200, res_clusters.text
    clusters = res_clusters.json()
    assert len(clusters) > 0

    # 2. List Nodes
    res_nodes = await client.get("/api/v1/kubernetes/nodes", headers=headers)
    assert res_nodes.status_code == 200, res_nodes.text
    nodes = res_nodes.json()
    assert len(nodes) > 0

    # 3. List Pods
    res_pods = await client.get("/api/v1/kubernetes/pods", headers=headers)
    assert res_pods.status_code == 200, res_pods.text
    pods = res_pods.json()
    assert len(pods) > 0
    sample_pod_name = pods[0]["name"]

    # 4. List Deployments
    res_deps = await client.get("/api/v1/kubernetes/deployments", headers=headers)
    assert res_deps.status_code == 200, res_deps.text

    # 5. List Events
    res_events = await client.get("/api/v1/kubernetes/events", headers=headers)
    assert res_events.status_code == 200, res_events.text

    # 6. Get Pod Logs
    res_logs = await client.get(f"/api/v1/kubernetes/logs/{sample_pod_name}", headers=headers)
    assert res_logs.status_code == 200, res_logs.text
    assert "logs" in res_logs.json()

    # 7. Analyze Cluster with Gemini AI
    res_analyze = await client.post("/api/v1/kubernetes/analyze", headers=headers)
    assert res_analyze.status_code == 200, res_analyze.text
    assert "cluster_health_score" in res_analyze.json()
