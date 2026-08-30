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

from datetime import UTC, datetime, timedelta
from typing import Any

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
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }
    return jwt.encode(payload, settings.effective_secret_key, algorithm=settings.effective_jwt_algorithm)


def create_access_token(
    subject: Any,
    expires_delta: timedelta | None = None,
) -> str:
    """Return a signed JWT access token for *subject* (typically a user UUID)."""
    delta = expires_delta or timedelta(minutes=settings.effective_access_token_expire_minutes)
    return _build_token(subject, token_type="access", expires_delta=delta)


def create_refresh_token(subject: Any) -> str:
    """Return a signed JWT refresh token for *subject*."""
    return _build_token(
        subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.effective_refresh_token_expire_days),
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
        settings.effective_secret_key,
        algorithms=[settings.effective_jwt_algorithm],
    )
