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

from pydantic import BaseModel, EmailStr

# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    """Internal schema used by CRUDUser.create — never exposed via API."""

    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    role: str = "member"


class UserUpdate(BaseModel):
    """Partial update — all fields optional."""

    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------


class UserResponse(BaseModel):
    """Safe user representation returned from API endpoints."""

    id: uuid.UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: str
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    organization_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """
    Extended profile returned from GET /users/me.

    Adds a denormalised ``organization_name`` field populated by the
    endpoint after eagerly loading the relationship.
    """

    organization_name: str | None = None

    model_config = {"from_attributes": True}
