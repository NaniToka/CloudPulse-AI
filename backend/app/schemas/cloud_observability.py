"""
Pydantic schemas for Multi-Cloud Observability Platform.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class CloudAccountCreate(BaseModel):
    name: str = Field(..., description="Display name for cloud account")
    provider: str = Field(..., description="AWS | Azure | GCP")
    account_id: str = Field(..., description="AWS Account ID, Azure Subscription ID, or GCP Project ID")
    credentials_type: str = Field("role_arn", description="role_arn | service_principal | service_account_key")
    credentials_meta: Dict[str, Any] = Field(default_factory=dict, description="Credentials or Role ARN metadata")
    default_region: Optional[str] = "us-east-1"
    environment: Optional[str] = "production"


class CloudAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    provider: str
    account_id: str
    credentials_type: str
    credentials_meta: Dict[str, Any]
    default_region: str
    environment: str
    status: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CloudResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    resource_type: str
    service: str
    provider: str
    region: str
    availability_zone: Optional[str] = None
    environment: str
    status: str
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_percent: Optional[float] = None
    network_in_mbps: Optional[float] = None
    network_out_mbps: Optional[float] = None
    monthly_cost: float
    risk_score: int
    tags: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime


class CloudCostSummaryResponse(BaseModel):
    total_monthly_spend: float
    forecasted_next_month: float
    provider_breakdown: Dict[str, float]
    idle_resource_savings: float


class CloudSecuritySummaryResponse(BaseModel):
    overall_compliance_score: int
    high_risk_resources_count: int
    open_vulnerabilities: int
    high_risk_list: List[Dict[str, Any]]


class CloudHealthSummaryResponse(BaseModel):
    total_resources: int
    healthy_count: int
    degraded_count: int
    critical_count: int
    health_score_percent: float
    ai_insights: List[Dict[str, Any]]
