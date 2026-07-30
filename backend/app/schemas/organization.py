"""Organization Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    team_size: Optional[str] = None
    industry: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    team_size: Optional[str]
    industry: Optional[str]
    member_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
