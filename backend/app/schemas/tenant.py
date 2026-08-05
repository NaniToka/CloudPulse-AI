"""
Pydantic v2 schemas for Multi-Tenant SaaS Architecture.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class OrganizationCreate(BaseModel):
    name: str = Field(..., description="Organization name")
    slug: Optional[str] = Field(None, description="URL slug (auto-generated if omitted)")
    logo: Optional[str] = None
    plan: str = Field("Enterprise", description="Free, Pro, Enterprise")


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    logo: Optional[str] = None
    logo_url: Optional[str] = None
    plan: str
    status: str
    owner_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class TeamCreate(BaseModel):
    organization_id: uuid.UUID
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime


class ProjectCreate(BaseModel):
    organization_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    name: str
    cloud_provider: str = "AWS"
    environment: str = "Production"
    region: str = "us-east-1"


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
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
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
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
    user_id: Optional[uuid.UUID] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
