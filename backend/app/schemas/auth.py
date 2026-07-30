"""
Authentication request / response schemas.

Validation rules are enforced here so the API layer stays thin.
All validators are class-methods decorated with ``@field_validator``
(Pydantic v2 style).
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def _name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be blank.")
        if len(v) > 100:
            raise ValueError("Cannot exceed 100 characters.")
        return v

    @field_validator("organization_name")
    @classmethod
    def _org_name_optional_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload for POST /auth/refresh."""

    refresh_token: str


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """Returned on successful register or login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class AccessTokenResponse(BaseModel):
    """Returned on successful token refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
