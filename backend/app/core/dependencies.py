"""
FastAPI dependency injection — database sessions and authentication.

Usage in endpoints
------------------
    @router.get("/me")
    async def me(user: User = Depends(get_current_user)):
        return user

Dependency graph
----------------
    get_db          — yields an AsyncSession per request
    get_current_user_id   — validates Bearer JWT, returns user UUID str
    get_current_user      — resolves UUID → User ORM object (preferred)
    require_active_user   — same as above but asserts is_active == True
"""

from typing import AsyncGenerator
from uuid import UUID

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal

log = structlog.get_logger(__name__)

# Reusable bearer scheme instance (auto_error=False lets us return 403 instead of 422)
_bearer = HTTPBearer(auto_error=True)


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a per-request async database session.

    Commits on clean exit, rolls back on exception, always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# JWT extraction
# ---------------------------------------------------------------------------

def _extract_user_id(token: str) -> str:
    """
    Decode *token* and return the ``sub`` claim as a string.

    Raises HTTPException 401 on any failure so FastAPI can short-circuit.
    """
    _unauth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except JWTError as exc:
        log.warning("jwt_decode_failed", error=str(exc))
        raise _unauth from exc

    if payload.get("type") != "access":
        log.warning("jwt_wrong_type", token_type=payload.get("type"))
        raise _unauth

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise _unauth

    return user_id


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """Return the authenticated user's UUID as a plain string."""
    return _extract_user_id(credentials.credentials)


# ---------------------------------------------------------------------------
# ORM-level user resolution
# ---------------------------------------------------------------------------

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve the JWT subject to a full ``User`` ORM object.

    Eagerly loads the ``organization`` relationship so callers never trigger
    implicit lazy loads (which raise ``MissingGreenlet`` in async context).

    Raises 401 if the user no longer exists in the database.
    """
    # Import here to avoid circular imports at module load time
    from app.models.user import User  # noqa: PLC0415

    try:
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    result = await db.execute(
        select(User)
        .where(User.id == uid)
        .options(selectinload(User.organization))
    )
    user = result.scalar_one_or_none()

    if user is None:
        log.warning("authenticated_user_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_active_user(user=Depends(get_current_user)):
    """
    Same as ``get_current_user`` but additionally asserts ``is_active == True``.

    Use this on any endpoint that should reject deactivated accounts.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )
    return user
