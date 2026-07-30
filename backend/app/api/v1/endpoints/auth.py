"""
Authentication endpoints.

POST /auth/register  — create account + org
POST /auth/login     — returns access + refresh tokens
POST /auth/refresh   — exchange refresh token for new access token
POST /auth/logout    — client-side (stateless JWT; documented here)
GET  /auth/me        — current user info
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user_id, get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.crud.crud_organization import crud_organization
from app.crud.crud_user import crud_user
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    existing = await crud_user.get_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create or reuse organization
    org = None
    if payload.organization_name:
        org = await crud_organization.create_with_unique_slug(
            db, name=payload.organization_name
        )

    # Create user
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

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_user.authenticate(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange a refresh token for a new access token",
)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
    )
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            raise credentials_exception
        user_id: str = token_data.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verify user still exists and is active
    from uuid import UUID
    user = await crud_user.get(db, UUID(user_id))
    if not user or not user.is_active:
        raise credentials_exception

    access_token = create_access_token(str(user.id))
    return AccessTokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Logout (documented — JWT is stateless; client drops tokens)
# ---------------------------------------------------------------------------
@router.post(
    "/logout",
    summary="Logout (client should discard tokens)",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(_: str = Depends(get_current_user_id)):
    # Stateless JWT — in a production system you'd add the token to a
    # Redis blocklist here. For now the client simply discards both tokens.
    return None


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def get_me(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    user = await crud_user.get(db, UUID(current_user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user
