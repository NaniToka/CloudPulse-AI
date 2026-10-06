import uuid
import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.init_db import _seed_admin_user_and_org

@pytest.mark.asyncio
async def test_auth_smoke(client: AsyncClient, db_session: AsyncSession) -> None:
    await _seed_admin_user_and_org(db_session)

    # 1. Register with a unique email returns 201 with tokens
    unique_email = f"test-{uuid.uuid4()}@cloudpulse.io"
    register_payload = {
        "email": unique_email,
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "organization_name": "Test Org"
    }
    resp = await client.post("/api/v1/auth/register", json=register_payload)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    
    # 2. Login with the demo user returns 200
    demo_payload = {
        "email": "admin@cloudpulse.io",
        "password": "Password123!"
    }
    resp = await client.post("/api/v1/auth/login", json=demo_payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data

    # 3. Login with a wrong password returns 401
    wrong_payload = {
        "email": "admin@cloudpulse.io",
        "password": "WrongPassword!"
    }
    resp = await client.post("/api/v1/auth/login", json=wrong_payload)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    # 4. OPTIONS /api/v1/auth/login with Origin returns 200/204 with access-control-allow-origin
    headers = {
        "Origin": "https://cloudpulse-frontend-55i6.onrender.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    resp = await client.options("/api/v1/auth/login", headers=headers)
    assert resp.status_code in (200, 204), f"Expected 200 or 204, got {resp.status_code}"
    assert resp.headers.get("access-control-allow-origin") == "https://cloudpulse-frontend-55i6.onrender.com"
