"""
Authentication endpoints.

Route summary
-------------
POST  /api/v1/auth/register  — Create account (+ optional org), return tokens
POST  /api/v1/auth/login     — Verify credentials, return tokens
POST  /api/v1/auth/refresh   — Exchange refresh token for a new access token
POST  /api/v1/auth/logout    — Stateless; instructs client to discard tokens
GET   /api/v1/auth/me        — Return the currently authenticated user
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.crud.crud_organization import crud_organization
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a user account and, if `organization_name` is supplied, "
        "a linked organization. Returns JWT access + refresh tokens on success."
    ),
)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    log.info(
        "register_attempt", email=payload.email, ip=request.client.host if request.client else None
    )

    existing = await crud_user.get_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    org = None
    if payload.organization_name:
        org = await crud_organization.create_with_unique_slug(db, name=payload.organization_name)

    user = await crud_user.create(
        db,
        obj_in=UserCreate(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        ),
    )

    if org:
        user = await crud_user.set_organization(db, user=user, organization_id=org.id)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    log.info("register_success", user_id=str(user.id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email + password",
    description="Returns JWT access + refresh tokens on successful authentication.",
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    log.info(
        "login_attempt", email=payload.email, ip=request.client.host if request.client else None
    )

    user = await crud_user.authenticate(db, email=payload.email, password=payload.password)

    # Use a single generic message to avoid user enumeration
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Contact support.",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    log.info("login_success", user_id=str(user.id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange a refresh token for a new access token",
)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AccessTokenResponse:
    _bad_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
    )

    try:
        token_data = decode_token(payload.refresh_token)
    except JWTError as exc:
        log.info("refresh_invalid_jwt", error=str(exc))
        raise _bad_token from exc

    if token_data.get("type") != "refresh":
        raise _bad_token

    raw_id: str | None = token_data.get("sub")
    if not raw_id:
        raise _bad_token

    try:
        user_id = UUID(raw_id)
    except ValueError as exc:
        raise _bad_token from exc

    # Verify the user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        log.info("refresh_user_not_found_or_inactive", user_id=raw_id)
        raise _bad_token

    new_access_token = create_access_token(user.id)
    log.info("refresh_success", user_id=str(user.id))

    return AccessTokenResponse(
        access_token=new_access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (instruct client to discard tokens)",
    description=(
        "This endpoint is stateless — the server does not invalidate the token. "
        "The client must delete both the access and refresh tokens. "
        "Production deployments should add the access token to a Redis blocklist."
    ),
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        from app.services.cache_service import cache_service

        await cache_service.blocklist_token(token)
    log.info("logout", user_id=str(current_user.id))
    return None


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Returns the user object associated with the Bearer access token.

    The ``organization`` relationship is eagerly loaded by ``get_current_user``
    so this endpoint never triggers a lazy-load error.
    """
    return current_user  # type: ignore[return-value]
