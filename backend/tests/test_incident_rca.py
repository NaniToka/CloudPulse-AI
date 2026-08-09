"""
Unit & Integration tests for Root Cause Analysis (RCA) Service.
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.services.root_cause_analysis_service import root_cause_analysis_service


@pytest.mark.asyncio
async def test_rca_database_saturation_origin(db_session: AsyncSession):
    now = datetime.now(UTC)
    incident = Incident(
        id=uuid.uuid4(),
        title="Cascading Checkout & Payment Failure",
        description="Checkout service failing with HTTP 504 timeouts.",
        severity="CRITICAL",
        priority="Critical",
        status="INVESTIGATING",
        affected_service="database-cluster",
        affected_services=["database-cluster", "payment-service", "checkout-svc"],
        affected_resources=["postgres-primary-db"],
        started_at=now,
        detected_at=now,
    )
    db_session.add(incident)
    await db_session.commit()

    rca_result = await root_cause_analysis_service.analyze_incident(db_session, incident)
    assert rca_result is not None
    assert "root_cause" in rca_result
    assert "postgres" in rca_result["root_cause"].lower() or "database" in rca_result["root_cause"].lower()
    assert rca_result["confidence"] >= 0.85
    assert len(rca_result["evidence"]) >= 1
    assert len(rca_result["recommended_actions"]) >= 1

    # Verify recommended actions contain workflow_id and parameters
    action = rca_result["recommended_actions"][0]
    assert "id" in action
    assert "action_type" in action
    assert action.get("automated") is True


@pytest.mark.asyncio
async def test_rca_blast_radius_calculation(db_session: AsyncSession):
    now = datetime.now(UTC)
    incident = Incident(
        id=uuid.uuid4(),
        title="Redis Memory Exhaustion Incident",
        severity="HIGH",
        priority="High",
        status="INVESTIGATING",
        affected_service="redis-cluster-cache",
        affected_services=["redis-cluster-cache", "auth-service", "user-service"],
        affected_resources=["redis-node-1"],
        started_at=now,
    )
    db_session.add(incident)
    await db_session.commit()

    blast = await root_cause_analysis_service.calculate_blast_radius(db_session, incident)
    assert blast["root_component"] == "redis-cluster-cache"
    assert len(blast["affected_services"]) == 3
    assert blast["dependency_depth"] >= 1
    assert "financial_risk_estimate" in blast
    assert "topology_graph" in blast
    assert len(blast["topology_graph"]["nodes"]) >= 3
