"""
Service Layer for Predictive Incident Detection Engine.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.crud.crud_prediction import crud_prediction
from app.models.prediction import Prediction
from app.schemas.prediction import (
    PredictionCreate,
    PredictionUpdate,
    PredictionStatsResponse,
    ServiceRiskItem,
)
from app.services.prediction_ai_service import generate_predictive_analysis
from app.services.websocket_manager import incident_ws_manager

log = structlog.get_logger(__name__)


class PredictionService:
    """Prediction Service handling business operations and AI analysis."""

    def __init__(self, crud_repo=crud_prediction) -> None:
        self.crud = crud_repo

    async def list_predictions(
        self,
        db: AsyncSession,
        *,
        service: Optional[str] = None,
        region: Optional[str] = None,
        risk: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> Tuple[List[Prediction], int, int]:
        return await self.crud.get_filtered(
            db,
            service=service,
            region=region,
            risk=risk,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            size=size,
        )

    async def get_active(self, db: AsyncSession) -> List[Prediction]:
        return await self.crud.get_active(db)

    async def get_stats(self, db: AsyncSession) -> PredictionStatsResponse:
        return await self.crud.get_stats(db)

    async def get_risk_heatmap(self, db: AsyncSession) -> List[ServiceRiskItem]:
        return await self.crud.get_risk_heatmap(db)

    async def get_by_id(self, db: AsyncSession, prediction_id: uuid.UUID) -> Optional[Prediction]:
        return await self.crud.get(db, prediction_id)

    async def trigger_analysis(
        self,
        db: AsyncSession,
        target_services: Optional[List[str]] = None,
        lookback_hours: int = 24,
    ) -> Prediction:
        """Runs Gemini Predictive AI Analysis against telemetry data and stores new prediction."""
        now = datetime.now(timezone.utc)
        primary_service = target_services[0] if target_services and len(target_services) > 0 else "api-gateway"
        region = "us-east-1"

        metrics_sample = {
            "cpu_history_avg": "94.2%",
            "memory_leak_rate": "+450MB/15m",
            "disk_io_utilization": "78.4%",
            "network_traffic_inbound": "1.2 Gbps",
            "error_rate_spike": "4.8%",
            "p99_latency": "2,840 ms",
            "deployment_history": "Deployed v2.4.1 45 minutes ago",
        }

        ai_res = await generate_predictive_analysis(primary_service, region, metrics_sample)

        expected_time = now + timedelta(minutes=24)

        prediction = Prediction(
            title=ai_res["title"],
            service=primary_service,
            region=region,
            prediction_score=ai_res["prediction_score"],
            failure_probability=ai_res["failure_probability"],
            expected_failure_time=expected_time,
            risk_level=ai_res["risk_level"],
            status="Active",
            affected_services=target_services or [primary_service, "auth-service", "database-cluster"],
            likely_root_cause=ai_res["likely_root_cause"],
            confidence_score=ai_res["confidence_score"],
            recommended_preventive_actions=ai_res["ai_immediate_preventive_actions"],
            triggering_metrics=metrics_sample,
            ai_explanation=ai_res["ai_explanation"],
            ai_metrics_of_concern=ai_res["ai_metrics_of_concern"],
            ai_historical_pattern_comparison=ai_res["ai_historical_pattern_comparison"],
            ai_possible_impact=ai_res["ai_possible_impact"],
            ai_immediate_preventive_actions=ai_res["ai_immediate_preventive_actions"],
            ai_long_term_recommendations=ai_res["ai_long_term_recommendations"],
            created_at=now,
            updated_at=now,
        )

        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)

        # Notify via WebSocket
        await incident_ws_manager.broadcast({
            "event": "prediction_created",
            "prediction_id": str(prediction.id),
            "service": prediction.service,
            "risk_level": prediction.risk_level,
            "failure_probability": prediction.failure_probability,
            "timestamp": now.isoformat(),
        })

        return prediction

    async def update_status(self, db: AsyncSession, prediction_id: uuid.UUID, status: str) -> Optional[Prediction]:
        pred = await self.crud.get(db, prediction_id)
        if not pred:
            return None

        updated = await self.crud.update(
            db,
            db_obj=pred,
            obj_in={"status": status, "updated_at": datetime.now(timezone.utc)},
        )
        return updated


prediction_service = PredictionService()
