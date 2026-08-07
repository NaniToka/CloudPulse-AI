"""
API tests for the Log Analyzer endpoints (/api/v1/logs).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Log",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_log_success(client: AsyncClient):
    headers = await get_auth_headers(client)

    log_content = (
        b"2026-08-03T10:00:00Z [INFO] [app] App started\n"
        b"2026-08-03T10:01:00Z [ERROR] [auth] Invalid credentials\n"
    )

    files = {"file": ("test.log", log_content, "text/plain")}

    response = await client.post(
        "/api/v1/logs/upload",
        files=files,
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.log"
    assert data["file_type"] == "log"
    assert data["status"] == "analyzing"
    assert data["stats"]["total_lines"] == 2
    assert data["stats"]["error_count"] == 1
    assert data["stats"]["info_count"] == 1


@pytest.mark.asyncio
async def test_upload_log_invalid_extension(client: AsyncClient):
    headers = await get_auth_headers(client)
    files = {"file": ("document.pdf", b"fake pdf", "application/pdf")}

    response = await client.post(
        "/api/v1/logs/upload",
        files=files,
        headers=headers,
    )

    assert response.status_code == 422
    assert "Unsupported file type" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_log_history_and_detail(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Upload a file
    log_content = b"2026-08-03 [WARNING] High memory usage\n"
    files = {"file": ("sys.log", log_content, "text/plain")}
    upload_resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201
    log_id = upload_resp.json()["id"]

    # 2. Get history
    history_resp = await client.get("/api/v1/logs/history", headers=headers)
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert history_data["total"] >= 1
    items = history_data["items"]
    assert any(item["id"] == log_id for item in items)

    # 3. Get single record detail
    detail_resp = await client.get(f"/api/v1/logs/{log_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == log_id
    assert detail_data["filename"] == "sys.log"
    assert len(detail_data["parsed_entries"]) == 1
    assert detail_data["parsed_entries"][0]["level"] == "WARNING"


@pytest.mark.asyncio
async def test_delete_log_analysis(client: AsyncClient):
    headers = await get_auth_headers(client)

    log_content = b"2026-08-03 [INFO] System ok\n"
    files = {"file": ("to_delete.log", log_content, "text/plain")}
    upload_resp = await client.post("/api/v1/logs/upload", files=files, headers=headers)
    log_id = upload_resp.json()["id"]

    # Delete
    del_resp = await client.delete(f"/api/v1/logs/{log_id}", headers=headers)
    assert del_resp.status_code == 204

    # Detail after delete should 404
    get_resp = await client.get(f"/api/v1/logs/{log_id}", headers=headers)
    assert get_resp.status_code == 404
