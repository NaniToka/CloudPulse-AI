"""
Prediction Service orchestrating Predictive AIOps, Analytics, and Incident integration.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_prediction import crud_anomaly_event, crud_prediction
from app.models.incident import Incident, IncidentTimelineEvent
from app.models.prediction import AnomalyEvent, Prediction
from app.schemas.prediction import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    CapacityRiskRequest,
    CapacityRiskResponse,
    ForecastRequest,
    MetricForecastResponse,
    PredictionAnalyticsResponse,
    PredictionStatsResponse,
    ServiceRiskItem,
)
from app.services.anomaly_engine import anomaly_engine
from app.services.capacity_risk_engine import capacity_risk_engine
from app.services.forecasting_engine import forecasting_engine
from app.services.predictive_aiops_engine import predictive_aiops_engine
from app.services.websocket_manager import incident_ws_manager

log = structlog.get_logger(__name__)


class PredictionService:
    """Service layer for predictive operations, anomaly scans, forecasts, and incident bridge."""

    def __init__(self, crud_repo=crud_prediction) -> None:
        self.crud = crud_repo

    async def list_predictions(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        service: str | None = None,
        resource: str | None = None,
        metric: str | None = None,
        environment: str | None = None,
        region: str | None = None,
        risk: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Prediction], int, int]:
        return await self.crud.get_filtered(
            db,
            organization_id=organization_id,
            service=service,
            resource=resource,
            metric=metric,
            environment=environment,
            region=region,
            risk=risk,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            size=size,
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        prediction_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> Prediction | None:
        pred = await self.crud.get(db, prediction_id)
        if pred and organization_id and pred.organization_id and pred.organization_id != organization_id:
            return None
        return pred

    async def get_active(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> list[Prediction]:
        return await self.crud.get_active(db, organization_id=organization_id)

    async def get_stats(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> PredictionStatsResponse:
        return await self.crud.get_stats(db, organization_id=organization_id)

    async def get_analytics(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> PredictionAnalyticsResponse:
        return await self.crud.get_analytics(db, organization_id=organization_id)

    async def get_risk_heatmap(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> list[ServiceRiskItem]:
        return await self.crud.get_risk_heatmap(db, organization_id=organization_id)

    async def get_anomalies(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        service: str | None = None,
        severity: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AnomalyEvent], int]:
        return await self.crud.get_anomalies(
            db,
            organization_id=organization_id,
            service=service,
            severity=severity,
            page=page,
            size=size,
        )

    async def detect_anomalies(
        self,
        req: AnomalyDetectionRequest,
    ) -> AnomalyDetectionResponse:
        """Run deterministic anomaly detection on metric payload."""
        hist = req.historical_values or [50.0, 52.0, 51.0, 53.0, 50.0, 52.0, 51.0, 88.0]
        curr = req.current_value if req.current_value is not None else hist[-1]
        res = anomaly_engine.detect_anomaly(
            current_value=curr,
            historical_values=hist,
            metric_name=req.metric_name,
            custom_critical_threshold=req.custom_critical_threshold,
        )
        return AnomalyDetectionResponse(
            metric_name=res.metric_name,
            value=res.value,
            baseline_value=res.baseline_value,
            anomaly_score=res.anomaly_score,
            severity=res.severity,
            is_anomaly=res.is_anomaly,
            direction=res.direction,
            method_used=res.method_used,
            z_score=res.z_score,
            deviation_percent=res.deviation_percent,
            explanation=res.explanation,
        )

    async def generate_forecast(
        self,
        req: ForecastRequest,
    ) -> MetricForecastResponse:
        """Generate multi-horizon forecast for metric payload."""
        hist = req.historical_values or [
            50.0, 52.0, 54.0, 57.0, 61.0, 65.0, 69.0, 74.0, 79.0, 84.5
        ]
        res = forecasting_engine.generate_forecast(
            values=hist,
            metric_name=req.metric_name,
            service=req.service,
            horizons=req.horizons,
            step_minutes=req.step_minutes,
        )
        return MetricForecastResponse(
            metric_name=res.metric_name,
            service=res.service,
            current_value=res.current_value,
            forecast_points=[
                {
                    "horizon": p.horizon,
                    "timestamp": p.timestamp,
                    "predicted_value": p.predicted_value,
                    "lower_bound": p.lower_bound,
                    "upper_bound": p.upper_bound,
                    "confidence": p.confidence,
                }
                for p in res.forecast_points
            ],
            historical_points=res.historical_points,
            model_used=res.model_used,
            data_sufficiency=res.data_sufficiency,
            generated_at=res.generated_at,
        )

    async def evaluate_capacity(
        self,
        req: CapacityRiskRequest,
    ) -> CapacityRiskResponse:
        """Evaluate resource capacity exhaustion risk."""
        hist = req.historical_values or [50.0, 54.0, 58.0, 63.0, 68.0, 74.0, 80.0, 86.5]
        res = capacity_risk_engine.evaluate_capacity_risk(
            values=hist,
            resource_name=req.resource_name,
            custom_threshold=req.custom_threshold,
        )
        return CapacityRiskResponse(
            resource_name=res.resource_name,
            current_value=res.current_value,
            capacity_limit=res.capacity_limit,
            exhaustion_threshold=res.exhaustion_threshold,
            risk_score=res.risk_score,
            risk_level=res.risk_level,
            is_exhaustion_imminent=res.is_exhaustion_imminent,
            estimated_time_to_threshold_minutes=res.estimated_time_to_threshold_minutes,
            rate_of_growth_per_minute=res.rate_of_growth_per_minute,
            data_status=res.data_status,
            summary=res.summary,
            recommended_mitigation=res.recommended_mitigation,
        )

    async def trigger_analysis(
        self,
        db: AsyncSession,
        target_services: list[str] | None = None,
        lookback_hours: int = 24,
        telemetry_map: dict[str, list[float]] | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> Prediction:
        """Runs full Predictive AIOps Analysis against telemetry data and stores new prediction."""
        primary_service = (
            target_services[0] if target_services and len(target_services) > 0 else "api-gateway"
        )
        region = "us-east-1"

        prediction = await predictive_aiops_engine.generate_prediction(
            db=db,
            service_name=primary_service,
            region=region,
            environment="production",
            telemetry_map=telemetry_map,
            organization_id=organization_id,
        )

        # Broadcast via WebSocket
        try:
            await incident_ws_manager.broadcast(
                {
                    "type": "PREDICTIVE_FAILURE_DETECTED",
                    "prediction_id": str(prediction.id),
                    "service": prediction.service,
                    "failure_probability": prediction.failure_probability,
                    "risk_level": prediction.risk_level,
                    "title": prediction.title,
                }
            )
        except Exception as ws_err:
            log.warning("websocket_broadcast_failed", error=str(ws_err))

        return prediction

    async def update_status(
        self,
        db: AsyncSession,
        prediction_id: uuid.UUID,
        new_status: str,
        organization_id: uuid.UUID | None = None,
    ) -> Prediction | None:
        """Update lifecycle status of a prediction."""
        pred = await self.get_by_id(db, prediction_id, organization_id)
        if not pred:
            return None

        pred.status = new_status.capitalize()
        await db.commit()
        await db.refresh(pred)
        return pred

    async def create_incident_from_prediction(
        self,
        db: AsyncSession,
        prediction_id: uuid.UUID,
        custom_severity: str | None = None,
        custom_title: str | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> Incident | None:
        """Escalate an active prediction directly into an Incident Command Center Incident."""
        pred = await self.get_by_id(db, prediction_id, organization_id)
        if not pred:
            return None

        now = datetime.now(UTC)
        severity_map = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
        }
        mapped_sev = custom_severity or severity_map.get(pred.risk_level.lower(), "HIGH")

        inc_title = custom_title or f"[PREDICTIVE RISK] {pred.title}"
        incident = Incident(
            id=uuid.uuid4(),
            organization_id=organization_id or pred.organization_id,
            title=inc_title,
            description=(
                f"Proactively declared from Predictive AIOps Engine.\n\n"
                f"Service: {pred.service}\n"
                f"Failure Probability: {pred.failure_probability}%\n"
                f"Likely Root Cause: {pred.likely_root_cause}\n\n"
                f"AI Explanation: {pred.ai_explanation}"
            ),
            severity=mapped_sev,
            status="INVESTIGATING",
            affected_service=pred.service,
            environment=pred.environment or "production",
            affected_region=pred.region or "us-east-1",
            source="AIOps_Prediction",
            root_cause=pred.likely_root_cause,
            recommended_actions=pred.recommended_preventive_actions,
            created_at=now,
            updated_at=now,
        )
        db.add(incident)

        timeline = IncidentTimelineEvent(
            id=uuid.uuid4(),
            incident_id=incident.id,
            timestamp=now,
            event_type="STATE_CHANGE",
            title="Incident Declared from Predictive Anomaly Risk",
            description=f"Auto-generated from high-confidence prediction {pred.id} ({pred.failure_probability}% failure probability).",
            created_at=now,
        )
        db.add(timeline)

        # Mark prediction as Triggered / Monitoring
        pred.status = "Triggered"

        await db.commit()
        await db.refresh(incident)

        return incident


prediction_service = PredictionService()
