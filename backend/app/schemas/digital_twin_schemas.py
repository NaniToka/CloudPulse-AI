"""
Pydantic schemas for Digital Twin & Infrastructure Failure Simulations.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InfrastructureTwinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    status: str
    health_score: int
    virtual_resources: list[dict[str, Any]] = Field(default_factory=list)
    topology_graph: dict[str, Any] = Field(default_factory=dict)
    total_services_count: int
    active_simulations_count: int
    created_at: datetime
    updated_at: datetime


class SimulationScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    twin_id: uuid.UUID
    name: str
    category: str
    failure_type: str
    target_resource: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    severity: str
    created_at: datetime
    updated_at: datetime


class SimulationScenarioCreate(BaseModel):
    name: str
    category: str = "Infrastructure"
    failure_type: str
    target_resource: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    severity: str = "HIGH"


class SimulationExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    twin_id: uuid.UUID
    scenario_id: uuid.UUID
    status: str
    duration_seconds: int
    risk_score: int
    confidence_score: float
    financial_impact_usd: float
    estimated_recovery_minutes: int
    affected_services: list[str] = Field(default_factory=list)
    blast_radius: dict[str, Any] = Field(default_factory=dict)
    predicted_timeline: list[dict[str, Any]] = Field(default_factory=list)
    recovery_steps: list[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WhatIfQueryRequest(BaseModel):
    query: str


class WhatIfQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    query_text: str
    impact_summary: str
    predicted_risk_level: str
    financial_risk_estimate: str
    affected_components: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    created_at: datetime


class BlastRadiusDetailResponse(BaseModel):
    scenario_id: uuid.UUID
    scenario_name: str
    risk_score: int
    affected_services: list[str]
    financial_impact_usd: float
    estimated_recovery_minutes: int
    blast_radius: dict[str, Any]
    timeline: list[dict[str, Any]]
    recovery_steps: list[str]
