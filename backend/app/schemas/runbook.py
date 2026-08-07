"""
Pydantic v2 schemas for Auto Remediation Center & Runbook Generator.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AutomationStepBase(BaseModel):
    step_number: int
    title: str
    description: str | None = None
    command: str
    expected_output: str | None = None
    rollback_command: str | None = None
    estimated_time: str = "2 mins"
    verification_method: str = "HTTP 200 Health Probe"
    status: str = "Pending"


class AutomationStepResponse(AutomationStepBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    runbook_id: uuid.UUID


class RunbookExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    runbook_id: uuid.UUID
    executed_by: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    logs_json: list[Any] = Field(default_factory=list)


class RunbookCreatePayload(BaseModel):
    incident_id: str | None = Field(None, description="Optional associated incident ID")
    service_name: str = Field(default="api-gateway", description="Target service for runbook")
    severity: str = Field(default="P1", description="Severity P0, P1, P2, P3")
    title: str | None = Field(None, description="Optional custom runbook title")


class RunbookApprovePayload(BaseModel):
    approved_by: str = Field(default="SRE Lead", description="Name/email of approving engineer")


class RunbookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    incident_id: str | None = None
    service_name: str
    severity: str
    generated_by_ai: bool = True
    status: str = "Draft"
    executive_summary: str | None = None
    root_cause: str | None = None
    rollback_procedure: str | None = None
    verification_checklist: list[str] = Field(default_factory=list)
    post_recovery_checklist: list[str] = Field(default_factory=list)
    estimated_resolution_time: str = "15 mins"
    risk_score: float = 2.5
    confidence_score: float = 0.95
    created_at: datetime
    updated_at: datetime

    steps: list[AutomationStepResponse] = Field(default_factory=list)
    executions: list[RunbookExecutionResponse] = Field(default_factory=list)


class RunbookListResponse(BaseModel):
    items: list[RunbookResponse]
    total: int
    page: int
    size: int
    pages: int
