"""
Predictive Incident Detection Engine API Endpoints.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.prediction import Prediction
from app.schemas.prediction import (
    PredictionResponse,
    PredictionListResponse,
    PredictionStatsResponse,
    InfrastructureRiskHeatmapResponse,
    PredictionAnalyzeRequest,
    PredictionStatusUpdate,
)
from app.services.prediction_service import prediction_service, PredictionService

log = structlog.get_logger(__name__)

router = APIRouter()


def get_prediction_service() -> PredictionService:
    return prediction_service


async def _seed_initial_predictions_if_empty(db: AsyncSession, service: PredictionService) -> None:
    preds, total, _ = await service.list_predictions(db, size=1)
    if total == 0:
        log.info("seeding_initial_predictive_failures")
        now = datetime.now(timezone.utc)
        sample_predictions = [
            Prediction(
                title="Imminent OOM & Thread Exhaustion on api-gateway",
                service="api-gateway",
                region="us-east-1",
                prediction_score=0.89,
                failure_probability=88.5,
                expected_failure_time=now + timedelta(minutes=28),
                risk_level="Critical",
                status="Active",
                affected_services=["api-gateway", "auth-service", "payment-service"],
                likely_root_cause="Linear heap memory leak (+450MB/15m) in session handler during traffic burst.",
                confidence_score=0.95,
                recommended_preventive_actions=[
                    "Scale api-gateway pod replicas from 4 to 12 instances",
                    "Flush stale session memory cache entries",
                    "Route ingress traffic away from worker node-us-east-1a",
                ],
                triggering_metrics={
                    "cpu_usage": "94.2%",
                    "memory_heap": "7.8 GB / 8.0 GB",
                    "p99_latency": "2,840 ms",
                    "error_rate": "4.8%",
                },
                ai_explanation="CloudPulse AI Watchdog detected a linear memory heap growth rate of +450MB/15m alongside CPU saturation at 94.2% on api-gateway (us-east-1). If unmitigated, memory capacity limits will breach in ~28 minutes, triggering Kubernetes OOM-Kills.",
                ai_metrics_of_concern=[
                    {
                        "name": "CPU Utilization",
                        "current_value": "94.2%",
                        "threshold": "85.0%",
                        "anomaly_trend": "+14.2% in 30m",
                        "risk_impact": "Thread pool lock contention",
                    },
                    {
                        "name": "Memory Heap Limit",
                        "current_value": "7.8 GB / 8.0 GB",
                        "threshold": "7.2 GB",
                        "anomaly_trend": "+450 MB / 15m",
                        "risk_impact": "Imminent OOM process termination",
                    },
                    {
                        "name": "P99 HTTP Latency",
                        "current_value": "2,840 ms",
                        "threshold": "500 ms",
                        "anomaly_trend": "+480% spike",
                        "risk_impact": "HTTP 504 Gateway Timeouts",
                    },
                ],
                ai_historical_pattern_comparison="Pattern matches 96% similarity with historical outage INC-8921 on api-gateway (Redis pool exhaustion).",
                ai_possible_impact="Cascade failure across 3 downstream services affecting ~12,400 active user sessions.",
                ai_immediate_preventive_actions=[
                    "Scale container instances for api-gateway in us-east-1",
                    "Flush stale session memory cache entries",
                    "Rebalance worker pool traffic",
                ],
                ai_long_term_recommendations=[
                    "Fix unclosed session object references in api-gateway codebase",
                    "Configure Kubernetes Horizontal Pod Autoscaler target at 70% Memory",
                ],
                created_at=now - timedelta(minutes=15),
                updated_at=now - timedelta(minutes=15),
            ),
            Prediction(
                title="Database Connection Pool Lock Contention on auth-service",
                service="auth-service",
                region="us-west-2",
                prediction_score=0.94,
                failure_probability=94.2,
                expected_failure_time=now + timedelta(minutes=14),
                risk_level="Critical",
                status="Active",
                affected_services=["auth-service", "database-cluster"],
                likely_root_cause="Unbounded bcrypt worker thread pool locking PostgreSQL connection pool during login spike.",
                confidence_score=0.96,
                recommended_preventive_actions=[
                    "Increase max_connections limit in PgBouncer pool",
                    "Scale auth-service pods from 6 to 15",
                ],
                triggering_metrics={
                    "cpu_usage": "98.1%",
                    "db_pool_active": "198 / 200",
                    "login_latency": "1,820 ms",
                },
                ai_explanation="Auth worker node CPU utilization reached 98.1% with 198 of 200 database connections occupied by pending bcrypt verification jobs.",
                ai_metrics_of_concern=[
                    {
                        "name": "DB Pool Saturation",
                        "current_value": "198 / 200",
                        "threshold": "160",
                        "anomaly_trend": "+35 connections / 10m",
                        "risk_impact": "DB connection rejection",
                    }
                ],
                ai_historical_pattern_comparison="92% match with INC-388 connection pool lock contention.",
                ai_possible_impact="User authentication failure rate rising to > 15%.",
                ai_immediate_preventive_actions=["Increase PgBouncer max_connections to 400"],
                ai_long_term_recommendations=["Offload bcrypt password hashing to async worker queue"],
                created_at=now - timedelta(minutes=20),
                updated_at=now - timedelta(minutes=20),
            ),
            Prediction(
                title="Storage IOPS Throttling on storage-service",
                service="storage-service",
                region="eu-west-1",
                prediction_score=0.64,
                failure_probability=64.0,
                expected_failure_time=now + timedelta(minutes=95),
                risk_level="Medium",
                status="Active",
                affected_services=["storage-service"],
                likely_root_cause="EBS volume burst balance depleted under heavy log write volume.",
                confidence_score=0.88,
                recommended_preventive_actions=[
                    "Provision gp3 IOPS from 3,000 to 10,000",
                    "Compress log export stream before flush",
                ],
                triggering_metrics={
                    "iops_utilization": "92.0%",
                    "ebs_burst_balance": "14%",
                },
                ai_explanation="EBS burst balance down to 14%. Disk I/O queues accumulating.",
                ai_metrics_of_concern=[],
                ai_historical_pattern_comparison="Similar to prior month storage throttling.",
                ai_possible_impact="Delayed log archiving export.",
                ai_immediate_preventive_actions=["Increase volume IOPS rating"],
                ai_long_term_recommendations=["Implement log streaming compression"],
                created_at=now - timedelta(minutes=45),
                updated_at=now - timedelta(minutes=45),
            ),
            Prediction(
                title="Kafka Consumer Rebalance Degradation on kafka-ingestion",
                service="kafka-ingestion",
                region="us-central1",
                prediction_score=0.58,
                failure_probability=58.5,
                expected_failure_time=now + timedelta(minutes=140),
                risk_level="Medium",
                status="Mitigated",
                affected_services=["kafka-ingestion"],
                likely_root_cause="Batch poll records count exceeding max.poll.interval.ms processing time.",
                confidence_score=0.90,
                recommended_preventive_actions=["Tune max.poll.records to 150"],
                triggering_metrics={"consumer_lag": "45,000 msgs"},
                ai_explanation="Mitigated after tuning batch size.",
                ai_metrics_of_concern=[],
                ai_historical_pattern_comparison="Routine consumer lag pattern.",
                ai_possible_impact="Minor telemetry latency.",
                ai_immediate_preventive_actions=["Adjust poll timeout"],
                ai_long_term_recommendations=["Automate partition rebalancing"],
                created_at=now - timedelta(hours=2),
                updated_at=now - timedelta(minutes=30),
            ),
        ]
        for pred in sample_predictions:
            db.add(pred)
        await db.commit()


@router.get("/stats", response_model=PredictionStatsResponse, summary="Get prediction KPI stats")
async def get_prediction_stats(
    db: AsyncSession = Depends(get_db),
    service: PredictionService = Depends(get_prediction_service),
):
    """Retrieve top KPI cards stats: Predicted Failures, High Risk Services, Average Confidence %, Prevented Downtime."""
    await _seed_initial_predictions_if_empty(db, service)
    return await service.get_stats(db)


@router.get("/heatmap", response_model=InfrastructureRiskHeatmapResponse, summary="Get Infrastructure Risk Heatmap")
async def get_risk_heatmap(
    db: AsyncSession = Depends(get_db),
    service: PredictionService = Depends(get_prediction_service),
):
    """Retrieve color-coded risk heatmap grid items across services and regions."""
    await _seed_initial_predictions_if_empty(db, service)
    heatmap_items = await service.get_risk_heatmap(db)
    return InfrastructureRiskHeatmapResponse(items=heatmap_items)


@router.get("/history", response_model=PredictionListResponse, summary="Get historical predictions")
async def get_prediction_history(
    service: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: PredictionService = Depends(get_prediction_service),
):
    """Retrieve historical predictions (including Mitigated, Dismissed, and Triggered)."""
    await _seed_initial_predictions_if_empty(db, service_layer)
    items, total, pages = await service_layer.list_predictions(
        db,
        service=service,
        region=region,
        risk=risk,
        search=search,
        page=page,
        size=size,
    )
    return PredictionListResponse(
        items=[PredictionResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("", response_model=PredictionListResponse, summary="List active predictions")
async def list_predictions(
    service: Optional[str] = Query(None, description="Filter by service name"),
    region: Optional[str] = Query(None, description="Filter by region"),
    risk: Optional[str] = Query(None, description="Filter by risk level (Critical, High, Medium, Low)"),
    status: Optional[str] = Query(None, description="Filter by status (Active, Mitigated, Dismissed)"),
    search: Optional[str] = Query(None, description="Search in title or root cause"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_dir: str = Query("desc", description="Sort direction"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service_layer: PredictionService = Depends(get_prediction_service),
):
    """Retrieve paginated predictions with search and risk filters."""
    await _seed_initial_predictions_if_empty(db, service_layer)
    items, total, pages = await service_layer.list_predictions(
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
    return PredictionListResponse(
        items=[PredictionResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("/analyze", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED, summary="Trigger predictive analysis")
async def analyze_predictions(
    req: PredictionAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    service_layer: PredictionService = Depends(get_prediction_service),
):
    """Trigger Google Gemini Predictive AI Engine to analyze infrastructure telemetry."""
    prediction = await service_layer.trigger_analysis(
        db,
        target_services=req.services,
        lookback_hours=req.lookback_hours,
    )
    return PredictionResponse.model_validate(prediction)


@router.get("/{prediction_id}", response_model=PredictionResponse, summary="Get prediction details")
async def get_prediction(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service_layer: PredictionService = Depends(get_prediction_service),
):
    """Retrieve single prediction record with complete AI explanation."""
    prediction = await service_layer.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail=f"Prediction '{prediction_id}' not found.")
    return PredictionResponse.model_validate(prediction)


@router.patch("/{prediction_id}/status", response_model=PredictionResponse, summary="Update prediction status")
async def update_prediction_status(
    prediction_id: uuid.UUID,
    payload: PredictionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    service_layer: PredictionService = Depends(get_prediction_service),
):
    """Update status of a prediction (e.g. Mitigated, Dismissed)."""
    updated = await service_layer.update_status(db, prediction_id, payload.status.value)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Prediction '{prediction_id}' not found.")
    return PredictionResponse.model_validate(updated)
