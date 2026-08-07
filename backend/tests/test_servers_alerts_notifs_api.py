"""
API unit tests for Servers, Alerts, and Notifications endpoints.
"""

import uuid
import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"infrauser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Infra",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_servers_api_crud(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List (triggers default seeding)
    res_list = await client.get("/api/v1/servers", headers=headers)
    assert res_list.status_code == 200, res_list.text
    servers = res_list.json()
    assert len(servers) > 0

    # 2. Register server
    srv_payload = {
        "name": "k8s-node-alpha",
        "hostname": "k8s-node-alpha.internal",
        "provider": "AWS",
        "environment": "production",
        "server_type": "container",
    }
    res_create = await client.post("/api/v1/servers", json=srv_payload, headers=headers)
    assert res_create.status_code == 201, res_create.text
    server = res_create.json()
    assert server["name"] == "k8s-node-alpha"

    # 3. Get server detail
    res_get = await client.get(f"/api/v1/servers/{server['id']}", headers=headers)
    assert res_get.status_code == 200, res_get.text

    # 4. Patch server
    res_patch = await client.patch(
        f"/api/v1/servers/{server['id']}",
        json={"status": "degraded", "cpu_percent": 94.5},
        headers=headers,
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "degraded"

    # 5. Delete server
    res_del = await client.delete(f"/api/v1/servers/{server['id']}", headers=headers)
    assert res_del.status_code == 204


@pytest.mark.asyncio
async def test_alerts_api_crud(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List alerts
    res_list = await client.get("/api/v1/alerts", headers=headers)
    assert res_list.status_code == 200, res_list.text
    alerts = res_list.json()
    assert len(alerts) > 0

    # 2. Create alert
    alert_payload = {
        "title": "Disk usage > 90% on storage-node-01",
        "message": "Storage saturation",
        "severity": "critical",
        "metric_name": "disk_percent",
        "metric_value": 94.2,
        "threshold": 90.0,
    }
    res_create = await client.post("/api/v1/alerts", json=alert_payload, headers=headers)
    assert res_create.status_code == 201, res_create.text
    alert_id = res_create.json()["id"]

    # 3. Acknowledge alert
    res_ack = await client.patch(f"/api/v1/alerts/{alert_id}/acknowledge", headers=headers)
    assert res_ack.status_code == 200
    assert res_ack.json()["status"] == "acknowledged"

    # 4. Resolve alert
    res_res = await client.patch(f"/api/v1/alerts/{alert_id}/resolve", headers=headers)
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "resolved"

    # 5. Bulk acknowledge
    res_bulk = await client.post("/api/v1/alerts/acknowledge-all", headers=headers)
    assert res_bulk.status_code == 200


@pytest.mark.asyncio
async def test_notifications_api_crud(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. List notifications
    res_list = await client.get("/api/v1/notifications", headers=headers)
    assert res_list.status_code == 200, res_list.text
    notifs = res_list.json()
    assert len(notifs) > 0
    first_id = notifs[0]["id"]

    # 2. Mark single read
    res_read = await client.patch(f"/api/v1/notifications/{first_id}/read", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["is_read"] is True

    # 3. Mark all read
    res_all = await client.post("/api/v1/notifications/read-all", headers=headers)
    assert res_all.status_code == 200
