"""
Predictive AIOps & Anomaly Intelligence Engine API Endpoints.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.prediction import Prediction
from app.schemas.incident import IncidentResponse
from app.schemas.prediction import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    AnomalyEventResponse,
    CapacityRiskRequest,
    CapacityRiskResponse,
    CreateIncidentFromPredictionRequest,
    ForecastRequest,
    InfrastructureRiskHeatmapResponse,
    MetricForecastResponse,
    PredictionAnalyticsResponse,
    PredictionAnalyzeRequest,
    PredictionListResponse,
    PredictionResponse,
    PredictionStatsResponse,
    PredictionStatusUpdate,
)
from app.services.prediction_service import PredictionService, prediction_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_prediction_service() -> PredictionService:
    return prediction_service


async def _seed_initial_predictions_if_empty(
    db: AsyncSession, service: PredictionService, organization_id: uuid.UUID | None = None
) -> None:
    preds, total, _ = await service.list_predictions(db, organization_id=organization_id, size=1)
    if total == 0:
        log.info("seeding_initial_predictive_failures")
        now = datetime.now(UTC)
        sample_predictions = [
            Prediction(
                id=uuid.uuid4(),
                organization_id=organization_id,
                title="Imminent OOM & Thread Pool Exhaustion on api-gateway",
                service="api-gateway",
                metric_name="memory_utilization",
                environment="production",
                region="us-east-1",
                prediction_score=0.89,
                failure_probability=88.5,
                confidence_score=0.95,
                risk_level="Critical",
                status="Active",
                trend_direction="ACCELERATING_DEGRADATION",
                trend_strength=0.92,
                rate_of_change=3.4,
                anomaly_score=0.88,
                expected_failure_time=now + timedelta(minutes=28),
                estimated_time_to_threshold_minutes=28.0,
                affected_services=["api-gateway", "auth-service", "payment-service"],
                likely_root_cause="Linear heap memory leak (+450MB/15m) in session handler during traffic burst.",
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
                data_sufficiency={"samples": 45, "minimum_required": 15, "sufficient": True, "confidence_factor": 1.0},
                analysis_engine="local",
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
                id=uuid.uuid4(),
                organization_id=organization_id,
                title="PostgreSQL Read Replica Replication Lag Desynchronization",
                service="database-cluster",
                metric_name="replication_lag",
                environment="production",
                region="us-east-1",
                prediction_score=0.82,
                failure_probability=82.0,
                confidence_score=0.91,
                risk_level="High",
                status="Active",
                trend_direction="INCREASING",
                trend_strength=0.85,
                rate_of_change=1.8,
                anomaly_score=0.79,
                expected_failure_time=now + timedelta(minutes=45),
                estimated_time_to_threshold_minutes=45.0,
                affected_services=["database-cluster", "analytics-pipeline", "reporting-service"],
                likely_root_cause="WAL sender buffer saturation causing 42s replication lag on replica-02.",
                recommended_preventive_actions=[
                    "Increase max_wal_senders and wal_sender_timeout parameters",
                    "Direct read queries temporarily to replica-01",
                ],
                triggering_metrics={
                    "replication_lag": "42.5 sec",
                    "wal_generation_rate": "125 MB/s",
                    "replica_io_wait": "84.2%",
                },
                data_sufficiency={"samples": 60, "minimum_required": 15, "sufficient": True, "confidence_factor": 1.0},
                analysis_engine="local",
                ai_explanation="Replication lag between primary DB cluster and replica-02 has grown exponentially from 1.2s to 42.5s due to heavy analytical transaction write load.",
                ai_metrics_of_concern=[
                    {
                        "name": "Replication Lag",
                        "current_value": "42.5s",
                        "threshold": "5.0s",
                        "anomaly_trend": "+41.3s in 20m",
                        "risk_impact": "Stale analytics read queries",
                    }
                ],
                ai_historical_pattern_comparison="Matches Postgres IO bottleneck pattern observed during Q3 bulk data migrations.",
                ai_possible_impact="Reporting queries returning stale financial ledger state.",
                ai_immediate_preventive_actions=[
                    "Reroute analytical reporting traffic to cold replica-03",
                    "Temporarily pause non-critical batch index optimization jobs",
                ],
                ai_long_term_recommendations=[
                    "Upgrade EBS GP3 IOPS allocation on replica storage volumes",
                ],
                created_at=now - timedelta(minutes=25),
                updated_at=now - timedelta(minutes=25),
            ),
        ]
        for p in sample_predictions:
            db.add(p)
        await db.commit()


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    service: str | None = Query(None, description="Filter by service name"),
    resource: str | None = Query(None, description="Filter by resource ID"),
    metric: str | None = Query(None, description="Filter by metric name"),
    environment: str | None = Query(None, description="Filter by environment"),
    region: str | None = Query(None, description="Filter by cloud region"),
    risk: str | None = Query(None, description="Filter by risk level (Critical, High, Medium, Low)"),
    status: str | None = Query(None, description="Filter by status (Active, Mitigated, Dismissed, Triggered)"),
    search: str | None = Query(None, description="Search term for title or root cause"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_dir: str = Query("desc", description="Sort direction (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionListResponse:
    """List predictive incident alerts with multi-dimensional filtering, search, and pagination."""
    await _seed_initial_predictions_if_empty(db, pred_svc)

    items, total, pages = await pred_svc.list_predictions(
        db,
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

    return PredictionListResponse(
        items=[PredictionResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/stats", response_model=PredictionStatsResponse)
async def get_prediction_stats(
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionStatsResponse:
    """Retrieve high-level KPI stats for predictive intelligence banner."""
    await _seed_initial_predictions_if_empty(db, pred_svc)
    return await pred_svc.get_stats(db)


@router.get("/analytics", response_model=PredictionAnalyticsResponse)
async def get_prediction_analytics(
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionAnalyticsResponse:
    """Retrieve comprehensive analytics breakdown by service, metric, risk, and anomaly event count."""
    await _seed_initial_predictions_if_empty(db, pred_svc)
    return await pred_svc.get_analytics(db)


@router.get("/heatmap", response_model=InfrastructureRiskHeatmapResponse)
async def get_infrastructure_risk_heatmap(
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> InfrastructureRiskHeatmapResponse:
    """Retrieve aggregated risk heatmap coordinates across infrastructure services."""
    await _seed_initial_predictions_if_empty(db, pred_svc)
    items = await pred_svc.get_risk_heatmap(db)
    return InfrastructureRiskHeatmapResponse(items=items)


@router.get("/anomalies", response_model=list[AnomalyEventResponse])
async def list_anomaly_events(
    service: str | None = Query(None, description="Filter by service"),
    severity: str | None = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> list[AnomalyEventResponse]:
    """Retrieve persistent historical anomaly event ledger."""
    items, _ = await pred_svc.get_anomalies(
        db, service=service, severity=severity, page=page, size=size
    )
    return [AnomalyEventResponse.model_validate(a) for a in items]


@router.post("/anomalies", response_model=AnomalyDetectionResponse)
async def detect_metric_anomalies(
    payload: AnomalyDetectionRequest,
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> AnomalyDetectionResponse:
    """Execute deterministic multi-algorithm anomaly detection on submitted metric stream."""
    return await pred_svc.detect_anomalies(payload)


@router.post("/forecast", response_model=MetricForecastResponse)
async def generate_metric_forecast(
    payload: ForecastRequest,
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> MetricForecastResponse:
    """Generate multi-horizon forecast with upper and lower confidence intervals."""
    return await pred_svc.generate_forecast(payload)


@router.post("/capacity", response_model=CapacityRiskResponse)
async def evaluate_capacity_risk(
    payload: CapacityRiskRequest,
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> CapacityRiskResponse:
    """Evaluate resource exhaustion risk and estimate time to threshold breach."""
    return await pred_svc.evaluate_capacity(payload)


@router.post("/analyze", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def trigger_predictive_analysis(
    payload: PredictionAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Trigger full Predictive AIOps Analysis with Grounded Gemini diagnostics."""
    prediction = await pred_svc.trigger_analysis(
        db,
        target_services=payload.services,
        lookback_hours=payload.lookback_hours,
        telemetry_map=payload.telemetry_map,
    )
    return PredictionResponse.model_validate(prediction)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction_by_id(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Fetch detailed prediction record by ID."""
    pred = await pred_svc.get_by_id(db, prediction_id)
    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found",
        )
    return PredictionResponse.model_validate(pred)


@router.patch("/{prediction_id}/status", response_model=PredictionResponse)
@router.post("/{prediction_id}/status", response_model=PredictionResponse)
async def update_prediction_status(
    prediction_id: uuid.UUID,
    payload: PredictionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Update lifecycle status of a prediction alert."""
    pred = await pred_svc.update_status(
        db, prediction_id, payload.status.value
    )
    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found",
        )
    return PredictionResponse.model_validate(pred)


@router.post("/{prediction_id}/create-incident", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_from_prediction(
    prediction_id: uuid.UUID,
    payload: CreateIncidentFromPredictionRequest = CreateIncidentFromPredictionRequest(),
    db: AsyncSession = Depends(get_db),
    pred_svc: PredictionService = Depends(get_prediction_service),
) -> IncidentResponse:
    """Escalate a high-risk prediction directly into an active Incident in Incident Command Center."""
    inc = await pred_svc.create_incident_from_prediction(
        db,
        prediction_id=prediction_id,
        custom_severity=payload.severity,
        custom_title=payload.title,
    )
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found",
        )
    return IncidentResponse.model_validate(inc)
