"""Organization Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    team_size: str | None = None
    industry: str | None = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    team_size: str | None
    industry: str | None
    member_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
