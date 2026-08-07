"""
Alert Monitoring Service with auto-seeding.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.crud.crud_alert import crud_alert
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate

log = structlog.get_logger(__name__)

DEFAULT_ALERTS = [
    {
        "title": "CPU > 90% on api-prod-01",
        "message": "CPU utilization reached 91.8% in us-central1 cluster.",
        "severity": "critical",
        "status": "active",
        "metric_name": "cpu_percent",
        "metric_value": 91.8,
        "threshold": 90.0,
    },
    {
        "title": "Memory usage > 85% on web-prod-02",
        "message": "Container memory heap saturation at 88.4%.",
        "severity": "high",
        "status": "active",
        "metric_name": "memory_percent",
        "metric_value": 88.4,
        "threshold": 85.0,
    },
    {
        "title": "worker-prod-02 is unreachable",
        "message": "Heartbeat failure detected from worker-prod-02 in eastus.",
        "severity": "high",
        "status": "active",
        "metric_name": "uptime_seconds",
        "metric_value": 0.0,
        "threshold": 1.0,
    },
    {
        "title": "Disk usage > 75% on db-primary",
        "message": "PostgreSQL database volume usage at 75.5%.",
        "severity": "medium",
        "status": "acknowledged",
        "metric_name": "disk_percent",
        "metric_value": 75.5,
        "threshold": 75.0,
    },
    {
        "title": "Response time > 2s on /checkout",
        "message": "P99 latency latency spike on payment API.",
        "severity": "medium",
        "status": "acknowledged",
        "metric_name": "latency_ms",
        "metric_value": 2450.0,
        "threshold": 2000.0,
    },
    {
        "title": "TLS Certificate expiring in 14 days",
        "message": "Domain cert *.cloudpulse.io expires soon.",
        "severity": "low",
        "status": "acknowledged",
        "metric_name": "cert_days",
        "metric_value": 14.0,
        "threshold": 30.0,
    },
]


class AlertService:
    """Service handling active and historical monitoring alerts."""

    def __init__(self, crud_repo=crud_alert) -> None:
        self.crud = crud_repo

    async def get_alerts(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Alert]:
        alerts = await self.crud.get_multi_filtered(
            db, status=status, severity=severity, search=search
        )
        if not alerts:
            alerts = await self.seed_default_alerts(db)
        return alerts

    async def seed_default_alerts(self, db: AsyncSession) -> List[Alert]:
        created = []
        now = datetime.now(timezone.utc)
        for data in DEFAULT_ALERTS:
            alert = Alert(
                id=uuid.uuid4(),
                title=data["title"],
                message=data["message"],
                severity=data["severity"],
                status=data["status"],
                metric_name=data["metric_name"],
                metric_value=data["metric_value"],
                threshold=data["threshold"],
                created_at=now,
                updated_at=now,
            )
            db.add(alert)
            created.append(alert)
        await db.commit()
        for a in created:
            await db.refresh(a)
        return created

    async def create_alert(self, db: AsyncSession, payload: AlertCreate) -> Alert:
        now = datetime.now(timezone.utc)
        alert = Alert(
            id=uuid.uuid4(),
            title=payload.title,
            message=payload.message,
            severity=payload.severity,
            status="active",
            metric_name=payload.metric_name,
            metric_value=payload.metric_value,
            threshold=payload.threshold,
            created_at=now,
            updated_at=now,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def update_alert_status(self, db: AsyncSession, alert_id: uuid.UUID, new_status: str) -> Optional[Alert]:
        alert = await self.crud.get(db, id=alert_id)
        if not alert:
            return None
        alert.status = new_status
        alert.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def bulk_acknowledge(self, db: AsyncSession) -> int:
        return await self.crud.bulk_acknowledge(db)


alert_service = AlertService()
