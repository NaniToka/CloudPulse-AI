"""
Pydantic v2 schemas for Multi-Tenant SaaS Architecture.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., description="Organization name")
    slug: str | None = Field(None, description="URL slug (auto-generated if omitted)")
    logo: str | None = None
    plan: str = Field("Enterprise", description="Free, Pro, Enterprise")


class OrganizationUpdate(BaseModel):
    name: str | None = None
    logo: str | None = None
    plan: str | None = None
    status: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    logo: str | None = None
    logo_url: str | None = None
    plan: str
    status: str
    owner_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class TeamCreate(BaseModel):
    organization_id: uuid.UUID
    name: str
    description: str | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    created_at: datetime


class ProjectCreate(BaseModel):
    organization_id: uuid.UUID
    team_id: uuid.UUID | None = None
    name: str
    cloud_provider: str = "AWS"
    environment: str = "Production"
    region: str = "us-east-1"


class ProjectUpdate(BaseModel):
    name: str | None = None
    cloud_provider: str | None = None
    environment: str | None = None
    region: str | None = None
    team_id: uuid.UUID | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    team_id: uuid.UUID | None = None
    name: str
    cloud_provider: str
    environment: str
    region: str
    created_at: datetime


class MemberInvitePayload(BaseModel):
    organization_id: uuid.UUID
    email: EmailStr
    role: str = Field("Engineer", description="Owner, Admin, Manager, Engineer, Viewer")


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str
    created_at: datetime


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    role: str
    token: str
    status: str
    created_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None
    action: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
