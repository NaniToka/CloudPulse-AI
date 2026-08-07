"""
Pydantic v2 schemas for Predictive Incident Detection Engine.
"""

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
    MITIGATED = "Mitigated"
    DISMISSED = "Dismissed"
    TRIGGERED = "Triggered"


class MetricConcern(BaseModel):
    name: str
    current_value: str
    threshold: str
    anomaly_trend: str
    risk_impact: str


class PredictionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500, description="Title of predicted incident")
    service: str = Field(default="api-gateway", description="Service at risk")
    region: str = Field(default="us-east-1", description="Cloud region")
    prediction_score: float = Field(
        default=0.88, ge=0.0, le=1.0, description="Normalized prediction score 0-1"
    )
    failure_probability: float = Field(
        default=88.5, ge=0.0, le=100.0, description="Predicted probability %"
    )
    expected_failure_time: datetime | None = Field(
        None, description="Estimated timestamp of predicted outage"
    )
    risk_level: RiskLevel = Field(default=RiskLevel.HIGH)
    status: PredictionStatus = Field(default=PredictionStatus.ACTIVE)
    affected_services: list[str] = Field(default_factory=list)
    likely_root_cause: str | None = None
    confidence_score: float = Field(default=0.94, ge=0.0, le=1.0)
    recommended_preventive_actions: list[str] = Field(default_factory=list)
    triggering_metrics: dict[str, Any] = Field(default_factory=dict)


class PredictionCreate(PredictionBase):
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
    created_at: datetime
    updated_at: datetime

    # AI Detailed Explanation
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
