"""
Pydantic v2 Schemas for Predictive AIOps & Anomaly Intelligence Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PredictionStatus(str, Enum):
    ACTIVE = "Active"
    MONITORING = "Monitoring"
    RESOLVED = "Resolved"
    EXPIRED = "Expired"
    FALSE_POSITIVE = "False_Positive"
    MITIGATED = "Mitigated"
    DISMISSED = "Dismissed"
    TRIGGERED = "Triggered"


class DataSufficiencySchema(BaseModel):
    samples: int
    minimum_required: int
    sufficient: bool
    confidence_factor: float = 1.0


class MetricConcern(BaseModel):
    name: str
    current_value: str
    threshold: str
    anomaly_trend: str
    risk_impact: str


class MetricForecastPointSchema(BaseModel):
    horizon: str  # 5m, 15m, 30m, 1h, 6h, 24h
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


class MetricForecastResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    metric_name: str
    service: str
    current_value: float
    forecast_points: list[MetricForecastPointSchema]
    historical_points: list[dict[str, Any]]
    model_used: str
    data_sufficiency: dict[str, Any]
    generated_at: datetime


class ForecastRequest(BaseModel):
    service: str = Field(default="api-gateway")
    metric_name: str = Field(default="memory_utilization")
    historical_values: list[float] | None = None
    horizons: list[str] = Field(default=["5m", "15m", "30m", "1h", "6h", "24h"])
    step_minutes: int = Field(default=1)


class AnomalyDetectionRequest(BaseModel):
    service: str = Field(default="api-gateway")
    metric_name: str = Field(default="cpu_utilization")
    current_value: float | None = None
    historical_values: list[float] | None = None
    custom_critical_threshold: float | None = None


class AnomalyDetectionResponse(BaseModel):
    metric_name: str
    value: float
    baseline_value: float
    anomaly_score: float
    severity: str
    is_anomaly: bool
    direction: str
    method_used: str
    z_score: float
    deviation_percent: float
    explanation: str


class AnomalyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    service: str
    metric_name: str
    resource_id: str | None = None
    value: float
    baseline_value: float
    anomaly_score: float
    severity: str
    direction: str
    method: str
    detected_at: datetime
    details: dict[str, Any] | None = None


class BaselineResponse(BaseModel):
    metric_name: str
    window: str
    samples_count: int
    mean: float
    median: float
    standard_deviation: float
    variance: float
    min_value: float
    max_value: float
    p50: float
    p90: float
    p95: float
    p99: float
    rolling_average: float
    rolling_std: float
    data_sufficiency: DataSufficiencySchema
    calculated_at: datetime


class CapacityRiskRequest(BaseModel):
    service: str = Field(default="api-gateway")
    resource_name: str = Field(default="memory_utilization")
    historical_values: list[float] | None = None
    custom_threshold: float | None = None


class CapacityRiskResponse(BaseModel):
    resource_name: str
    current_value: float
    capacity_limit: float
    exhaustion_threshold: float
    risk_score: float
    risk_level: str
    is_exhaustion_imminent: bool
    estimated_time_to_threshold_minutes: float | None = None
    rate_of_growth_per_minute: float
    data_status: str
    summary: str
    recommended_mitigation: str


class PredictionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    service: str = Field(default="api-gateway")
    metric_name: str | None = Field(default="memory_utilization")
    resource_id: str | None = None
    environment: str = Field(default="production")
    region: str = Field(default="us-east-1")
    prediction_score: float = Field(default=0.88, ge=0.0, le=1.0)
    failure_probability: float = Field(default=88.5, ge=0.0, le=100.0)
    confidence_score: float = Field(default=0.94, ge=0.0, le=1.0)
    risk_level: RiskLevel = Field(default=RiskLevel.HIGH)
    status: PredictionStatus = Field(default=PredictionStatus.ACTIVE)
    trend_direction: str = Field(default="STABLE")
    trend_strength: float = Field(default=0.0)
    rate_of_change: float = Field(default=0.0)
    anomaly_score: float = Field(default=0.0)
    expected_failure_time: datetime | None = None
    estimated_time_to_threshold_minutes: float | None = None
    affected_services: list[str] = Field(default_factory=list)
    likely_root_cause: str | None = None
    recommended_preventive_actions: list[str] = Field(default_factory=list)
    triggering_metrics: dict[str, Any] = Field(default_factory=dict)
    data_sufficiency: dict[str, Any] | None = Field(default_factory=dict)
    forecast_points: list[dict[str, Any]] | None = Field(default_factory=list)
    correlated_signals: list[dict[str, Any]] | None = Field(default_factory=list)


class PredictionCreate(PredictionBase):
    analysis_engine: str = "local"
    ai_explanation: str | None = None
    ai_metrics_of_concern: list[MetricConcern] | None = Field(default_factory=list)
    ai_historical_pattern_comparison: str | None = None
    ai_possible_impact: str | None = None
    ai_immediate_preventive_actions: list[str] | None = Field(default_factory=list)
    ai_long_term_recommendations: list[str] | None = Field(default_factory=list)


class PredictionUpdate(BaseModel):
    title: str | None = None
    service: str | None = None
    region: str | None = None
    risk_level: RiskLevel | None = None
    status: PredictionStatus | None = None
    recommended_preventive_actions: list[str] | None = None


class PredictionStatusUpdate(BaseModel):
    status: PredictionStatus


class PredictionResponse(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    analysis_engine: str = "local"
    ai_explanation: str | None = None
    ai_metrics_of_concern: list[MetricConcern] | None = Field(default_factory=list)
    ai_historical_pattern_comparison: str | None = None
    ai_possible_impact: str | None = None
    ai_immediate_preventive_actions: list[str] | None = Field(default_factory=list)
    ai_long_term_recommendations: list[str] | None = Field(default_factory=list)


class PredictionListResponse(BaseModel):
    items: list[PredictionResponse]
    total: int
    page: int
    size: int
    pages: int


class PredictionStatsResponse(BaseModel):
    predicted_failures: int
    high_risk_services: int
    avg_confidence_percent: float
    prevented_downtime_hours: float


class PredictionAnalyticsResponse(BaseModel):
    total_predictions: int
    active_risks: int
    critical_risks: int
    anomaly_events_count: int
    predicted_failures: int
    average_confidence: float
    predictions_by_service: dict[str, int]
    predictions_by_metric: dict[str, int]
    predictions_by_risk: dict[str, int]


class ServiceRiskItem(BaseModel):
    service: str
    region: str
    risk_level: str
    failure_probability: float
    active_predictions_count: int


class InfrastructureRiskHeatmapResponse(BaseModel):
    items: list[ServiceRiskItem]


class PredictionAnalyzeRequest(BaseModel):
    services: list[str] | None = Field(
        default=None, description="Optional list of specific services to analyze"
    )
    lookback_hours: int = Field(
        default=24, ge=1, le=168, description="Telemetry lookback window in hours"
    )
    telemetry_map: dict[str, list[float]] | None = Field(
        default=None, description="Optional explicit telemetry series to evaluate"
    )


class CreateIncidentFromPredictionRequest(BaseModel):
    severity: str | None = Field(default=None, description="Optional override severity")
    title: str | None = Field(default=None, description="Optional incident title")
