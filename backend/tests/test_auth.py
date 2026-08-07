"""
Authentication endpoint tests.

Each test uses a uniquely generated email (via the ``email_factory`` fixture)
to stay fully isolated even when the session-scoped engine re-uses the same
in-memory DB between tests.
"""

import uuid

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def unique_payload(**overrides) -> dict:
    """Return a register payload with a guaranteed-unique email."""
    base = {
        "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
        "password": "Secure123",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "organization_name": "Test Corp",
    }
    return {**base, **overrides}


async def register_and_get_tokens(client: AsyncClient, **overrides) -> dict:
    """Register a user and return the full response JSON."""
    payload = unique_payload(**overrides)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json(), payload


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_returns_tokens(client: AsyncClient):
    data, _ = await register_and_get_tokens(client)

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["expires_in"], int)
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_creates_org(client: AsyncClient):
    """Registering with an org name should succeed."""
    payload = unique_payload(organization_name="Acme Corp")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_register_without_org(client: AsyncClient):
    """organization_name is optional."""
    payload = unique_payload()
    del payload["organization_name"]
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = unique_payload()
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["error"].lower()


@pytest.mark.asyncio
async def test_register_short_password_returns_422(client: AsyncClient):
    payload = unique_payload(password="short")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_uppercase_returns_422(client: AsyncClient):
    payload = unique_payload(password="alllowercase1")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_digit_returns_422(client: AsyncClient):
    payload = unique_payload(password="NoDigitsHere")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_blank_first_name_returns_422(client: AsyncClient):
    payload = unique_payload(first_name="   ")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client: AsyncClient):
    payload = unique_payload(email="not-an-email")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    _, payload = await register_and_get_tokens(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient):
    _, payload = await register_and_get_tokens(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": "WrongPass99"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "AnyPass1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email_format_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bad-email", "password": "AnyPass1"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_me_returns_user(client: AsyncClient):
    data, payload = await register_and_get_tokens(client)
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == payload["email"].lower()
    assert me["first_name"] == payload["first_name"]
    assert "hashed_password" not in me


@pytest.mark.asyncio
async def test_get_me_no_token_returns_403(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    # HTTPBearer returns 403 when no Authorization header is present
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token_returns_401(client: AsyncClient):
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer totally.invalid.token"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_refresh_token_rejected(client: AsyncClient):
    """Passing a refresh token where an access token is expected should fail."""
    data, _ = await register_and_get_tokens(client)
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['refresh_token']}"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client: AsyncClient):
    data, _ = await register_and_get_tokens(client)
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert resp.status_code == 200
    refreshed = resp.json()
    assert "access_token" in refreshed
    assert refreshed["token_type"] == "bearer"
    assert isinstance(refreshed["expires_in"], int)
    assert refreshed["expires_in"] > 0


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_401(client: AsyncClient):
    """Passing an access token to /refresh should fail."""
    data, _ = await register_and_get_tokens(client)
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["access_token"]},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_garbage_returns_401(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not.a.jwt"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_returns_204(client: AsyncClient):
    data, _ = await register_and_get_tokens(client)
    resp = await client.post(
        "/api/v1/logout",  # wrong path — should 404
    )
    assert resp.status_code == 404  # confirm route doesn't exist at root

    resp = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_logout_without_token_returns_403(client: AsyncClient):
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Users endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_users_me_returns_profile(client: AsyncClient):
    data, payload = await register_and_get_tokens(client)
    resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["email"] == payload["email"].lower()
    # org name should be present since we provided one
    assert profile["organization_name"] == payload.get("organization_name")


@pytest.mark.asyncio
async def test_users_me_patch_updates_name(client: AsyncClient):
    data, _ = await register_and_get_tokens(client)
    resp = await client.patch(
        "/api/v1/users/me",
        json={"first_name": "Grace", "last_name": "Hopper"},
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Grace"
    assert resp.json()["last_name"] == "Hopper"


# ---------------------------------------------------------------------------
# Health check (sanity)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
