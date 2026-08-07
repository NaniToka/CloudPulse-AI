"""
Pydantic schemas for Workflow Automation Platform.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowBase(BaseModel):
    name: str
    description: str | None = None
    status: str = "active"
    trigger_type: str = "manual"
    trigger_config: dict[str, Any] = Field(default_factory=dict)
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    trigger_type: str | None = None
    trigger_config: dict[str, Any] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    tags: list[str] | None = None


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime


class WorkflowStepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    execution_id: uuid.UUID
    node_id: str
    node_label: str
    action_type: str
    status: str
    input_payload: dict[str, Any] = Field(default_factory=dict)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error_detail: str | None = None
    retry_count: int
    execution_time_ms: int
    created_at: datetime


class WorkflowApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    execution_id: uuid.UUID
    node_id: str
    step_title: str
    approver_role: str
    status: str
    requested_at: datetime
    decided_at: datetime | None = None
    decided_by: str | None = None
    rejection_reason: str | None = None


class WorkflowApprovalDecision(BaseModel):
    approval_id: uuid.UUID
    decision: str  # approved | rejected
    reason: str | None = None


class WorkflowExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    status: str
    trigger_source: str
    trigger_payload: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int | None = None
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    context_variables: dict[str, Any] = Field(default_factory=dict)
    step_results: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class WorkflowTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: str
    description: str
    trigger_type: str
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    icon: str
    created_at: datetime


class WorkflowAIGenerateRequest(BaseModel):
    prompt: str
