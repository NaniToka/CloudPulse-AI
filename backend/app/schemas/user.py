"""
User Pydantic schemas.

Separation of concerns:
  UserCreate      — internal (password in plain text, used by CRUD layer)
  UserUpdate      — partial update (all fields optional)
  UserResponse    — API output (no sensitive fields)
  UserProfile     — UserResponse + org name (for /users/me)
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Internal schema used by CRUDUser.create — never exposed via API."""

    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "member"


class UserUpdate(BaseModel):
    """Partial update — all fields optional."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Safe user representation returned from API endpoints."""

    id: uuid.UUID
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    organization_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """
    Extended profile returned from GET /users/me.

    Adds a denormalised ``organization_name`` field populated by the
    endpoint after eagerly loading the relationship.
    """

    organization_name: Optional[str] = None

    model_config = {"from_attributes": True}
