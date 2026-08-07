"""
Monitoring Alerts REST API Endpoints.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.alert_service import AlertService, alert_service

router = APIRouter()


@router.get("", response_model=list[AlertResponse], summary="List Monitoring Alerts")
async def list_alerts(
    status_filter: str | None = Query(
        None, alias="status", description="Filter by status (active, acknowledged, resolved)"
    ),
    severity: str | None = Query(
        None, description="Filter by severity (critical, high, medium, low)"
    ),
    search: str | None = Query(None, description="Search alert title or message"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: AlertService = Depends(lambda: alert_service),
):
    """Retrieve monitoring alerts."""
    alerts = await service.get_alerts(db, status=status_filter, severity=severity, search=search)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post(
    "", response_model=AlertResponse, status_code=status.HTTP_201_CREATED, summary="Create Alert"
)
async def create_alert(
    payload: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: AlertService = Depends(lambda: alert_service),
):
    """Manually trigger or register a monitoring alert."""
    alert = await service.create_alert(db, payload)
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse, summary="Acknowledge Alert")
async def acknowledge_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: AlertService = Depends(lambda: alert_service),
):
    """Mark an alert as acknowledged."""
    alert = await service.update_alert_status(db, alert_id, "acknowledged")
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}/resolve", response_model=AlertResponse, summary="Resolve Alert")
async def resolve_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: AlertService = Depends(lambda: alert_service),
):
    """Mark an alert as resolved."""
    alert = await service.update_alert_status(db, alert_id, "resolved")
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/acknowledge-all", summary="Acknowledge All Active Alerts")
async def acknowledge_all_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: AlertService = Depends(lambda: alert_service),
):
    """Acknowledge all currently active alerts."""
    count = await service.bulk_acknowledge(db)
    return {"status": "success", "acknowledged_count": count}
