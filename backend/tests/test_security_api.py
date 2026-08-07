"""
API tests for AI Security & Cloud Compliance Center (/api/v1/security).
"""

import uuid

import pytest
from httpx import AsyncClient


def unique_payload() -> dict:
    return {
        "email": f"secuser-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123",
        "first_name": "Security",
        "last_name": "Tester",
    }


async def get_auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = unique_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_trigger_security_scan(client: AsyncClient):
    headers = await get_auth_headers(client)

    payload = {"provider": "AWS", "scan_name": "Test Cloud Scan"}

    response = await client.post("/api/v1/security/scan", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    data = response.json()

    assert "total_findings" in data
    assert data["total_findings"] > 0
    assert "overall_security_score" in data


@pytest.mark.asyncio
async def test_list_findings_and_risk_score(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Findings
    findings_resp = await client.get("/api/v1/security/findings", headers=headers)
    assert findings_resp.status_code == 200, findings_resp.text
    fdata = findings_resp.json()
    assert "items" in fdata
    assert fdata["total"] > 0

    # Risk Score
    risk_resp = await client.get("/api/v1/security/risk-score", headers=headers)
    assert risk_resp.status_code == 200, risk_resp.text
    rdata = risk_resp.json()
    assert "overall_security_score" in rdata
    assert "overall_risk_score" in rdata


@pytest.mark.asyncio
async def test_compliance_and_report(client: AsyncClient):
    headers = await get_auth_headers(client)

    # Compliance Scorecards
    comp_resp = await client.get("/api/v1/security/compliance", headers=headers)
    assert comp_resp.status_code == 200, comp_resp.text
    cdata = comp_resp.json()
    assert len(cdata) > 0
    assert cdata[0]["framework"] is not None

    # Executive Report
    rep_resp = await client.get("/api/v1/security/report", headers=headers)
    assert rep_resp.status_code == 200, rep_resp.text
    rdata = rep_resp.json()
    assert "overall_security_score" in rdata
    assert "top_recommendations" in rdata
