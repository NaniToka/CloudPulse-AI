"""
Unit & Integration tests for Incident Timeline events.
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"inctime-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Timeline",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_incident_timeline_chronology_and_notes(client: AsyncClient):
    headers = await get_auth_headers(client)

    # 1. Create incident
    create_payload = {
        "title": "Timeline Test Incident",
        "severity": "MEDIUM",
        "status": "INVESTIGATING",
        "affected_service": "auth-service",
        "auto_analyze": True,
    }
    create_resp = await client.post("/api/v1/incidents", json=create_payload, headers=headers)
    incident_id = create_resp.json()["id"]

    # 2. Add an engineer note to timeline
    note_payload = {
        "title": "Engineer Triage Note",
        "description": "Observed connection spikes on auth pod 3. Initiating trace dump.",
        "event_type": "engineer_note",
        "source": "IncidentCommandCenter",
    }
    post_timeline_resp = await client.post(
        f"/api/v1/incidents/{incident_id}/timeline", json=note_payload, headers=headers
    )
    assert post_timeline_resp.status_code == 201, post_timeline_resp.text
    new_evt = post_timeline_resp.json()
    assert new_evt["title"] == "Engineer Triage Note"
    assert new_evt["event_type"] == "engineer_note"

    # 3. Query entire timeline
    get_timeline_resp = await client.get(
        f"/api/v1/incidents/{incident_id}/timeline", headers=headers
    )
    assert get_timeline_resp.status_code == 200, get_timeline_resp.text
    events = get_timeline_resp.json()
    assert len(events) >= 2

    # Verify chronological ordering
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)
