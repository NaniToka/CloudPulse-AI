"""
Pydantic v2 schemas for Autonomous AIOps Agent & AI Operations Center.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    task_name: str
    target_system: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None


class AgentExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recommendation_id: uuid.UUID
    action_taken: str
    approved_by: str
    status: str
    execution_logs: list[Any] = Field(default_factory=list)
    executed_at: datetime


class AgentRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    title: str
    category: str
    priority: str
    executive_summary: str
    root_cause: str | None = None
    business_impact: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    automation_candidates: list[str] = Field(default_factory=list)
    confidence_score: float = 0.95
    expected_recovery_time: str = "10 mins"
    status: str = "Pending_Approval"
    created_at: datetime

    executions: list[AgentExecutionResponse] = Field(default_factory=list)


class AIOpsAgentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_name: str
    status: str  # Active, Autonomous, Paused
    current_phase: str  # Observe, Detect, Analyze, Plan, Recommend, Verify
    health_status: str  # Healthy, Degraded, Anomalous
    last_observation_at: datetime
    total_recommendations: int = 0
    pending_approvals: int = 0
    active_automations: int = 0
    tasks: list[AgentTaskResponse] = Field(default_factory=list)


class AgentAnalyzePayload(BaseModel):
    target_system: str | None = Field(
        "All", description="Metrics, Logs, Traces, Security, Cost, or All"
    )


class AgentApprovePayload(BaseModel):
    recommendation_id: uuid.UUID
    approved_by: str = Field(
        "Senior Site Reliability Engineer",
        description="User or automation controller approving action",
    )
    action: str = Field("Approve", description="Approve or Reject")


class AIOpsListResponse(BaseModel):
    items: list[AgentRecommendationResponse]
    total: int
    page: int
    size: int
    pages: int
