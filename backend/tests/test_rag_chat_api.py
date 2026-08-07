"""
API tests for RAG AI Infrastructure Chat Platform (/api/v1/chat).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"raguser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "RAG",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_rag_chat_query(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {
        "question": "Why is CPU high on api-gateway?",
        "conversation_id": "conv-test-101",
    }

    response = await client.post("/api/v1/chat/query", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "answer" in data
    assert "evidence_sources" in data
    assert "confidence_score" in data
    assert "recommended_actions" in data
    assert len(data["evidence_sources"]) > 0


@pytest.mark.asyncio
async def test_rag_chat_history_and_clear(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Get History
    hist_resp = await client.get(
        "/api/v1/chat/history?conversation_id=conv-test-101", headers=headers
    )
    assert hist_resp.status_code == 200, hist_resp.text
    data = hist_resp.json()
    assert "messages" in data

    # Clear History
    del_resp = await client.delete(
        "/api/v1/chat/history?conversation_id=conv-test-101", headers=headers
    )
    assert del_resp.status_code == 200, del_resp.text
    assert del_resp.json()["status"] == "success"
