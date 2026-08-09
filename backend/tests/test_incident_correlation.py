"""
Unit & Integration tests for Incident Correlation Engine.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.incident_correlation_engine import incident_correlation_engine


@pytest.mark.asyncio
async def test_correlate_single_alert(db_session: AsyncSession):
    raw_alerts = [
        {
            "service": "api-gateway",
            "metric_name": "http_latency_p99",
            "title": "API Gateway p99 latency exceeded 2000ms",
            "severity": "HIGH",
            "resource": "pod-gateway-1",
            "metric_value": 2450.0,
            "threshold": 500.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    ]

    incidents = await incident_correlation_engine.correlate_alerts(db_session, raw_alerts)
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.affected_service == "api-gateway"
    assert inc.severity in ["HIGH", "CRITICAL"]
    assert inc.confidence_score >= 0.8
    assert len(inc.timeline_events) >= 1


@pytest.mark.asyncio
async def test_correlate_multi_service_cascading_failure(db_session: AsyncSession):
    now = datetime.now(UTC)
    raw_alerts = [
        {
            "service": "database-cluster",
            "metric_name": "db_connections_active",
            "title": "PostgreSQL connection pool exhausted (200/200)",
            "severity": "CRITICAL",
            "resource": "postgres-primary",
            "metric_value": 200.0,
            "threshold": 160.0,
            "timestamp": now.isoformat(),
        },
        {
            "service": "payment-service",
            "metric_name": "http_504_timeouts",
            "title": "Payment API downstream timeout on DB call",
            "severity": "HIGH",
            "resource": "payment-pod-1",
            "timestamp": (now + timedelta(seconds=30)).isoformat(),
        },
        {
            "service": "checkout-svc",
            "metric_name": "http_500_errors",
            "title": "Checkout failure due to payment timeout",
            "severity": "HIGH",
            "resource": "checkout-pod-2",
            "timestamp": (now + timedelta(seconds=60)).isoformat(),
        },
    ]

    incidents = await incident_correlation_engine.correlate_alerts(db_session, raw_alerts)
    # Should correlate all 3 into a single incident with database-cluster as root origin
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.affected_service == "database-cluster"
    assert "payment-service" in inc.affected_services
    assert "checkout-svc" in inc.affected_services
    assert inc.severity == "CRITICAL"
    assert inc.confidence_score >= 0.9
    assert inc.impact_score >= 70.0


@pytest.mark.asyncio
async def test_alert_deduplication_storm(db_session: AsyncSession):
    now = datetime.now(UTC)
    # 5 identical alerts within 1 minute
    raw_alerts = [
        {
            "service": "auth-service",
            "metric_name": "cpu_utilization",
            "title": "CPU utilization at 98%",
            "severity": "HIGH",
            "resource": "auth-pod-1",
            "timestamp": (now + timedelta(seconds=i * 10)).isoformat(),
        }
        for i in range(5)
    ]

    incidents = await incident_correlation_engine.correlate_alerts(db_session, raw_alerts)
    # Should deduplicate and create only 1 incident
    assert len(incidents) == 1
    assert incidents[0].affected_service == "auth-service"
