"""
Security utilities: password hashing (bcrypt) and JWT token management.

Design decisions
----------------
- Separate access tokens (short-lived, 30 min default) from refresh tokens
  (long-lived, 7 days default) via a ``type`` claim.
- ``decode_token`` never swallows exceptions; callers decide how to handle them.
- ``CryptContext`` is instantiated once at module level — it is thread-safe and
  reusing it avoids repeated bcrypt work-factor lookups.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _build_token(subject: Any, token_type: str, expires_delta: timedelta) -> str:
    """Internal: encode a signed JWT with standard claims."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Return a signed JWT access token for *subject* (typically a user UUID)."""
    delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return _build_token(subject, token_type="access", expires_delta=delta)


def create_refresh_token(subject: Any) -> str:
    """Return a signed JWT refresh token for *subject*."""
    return _build_token(
        subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify *token*.

    Raises
    ------
    jose.JWTError
        If the token is expired, has an invalid signature, or is malformed.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
