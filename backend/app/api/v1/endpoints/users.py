"""
User profile endpoints (protected).

Route summary
-------------
GET   /api/v1/users/me        — Full profile (includes org name)
PATCH /api/v1/users/me        — Update profile fields
GET   /api/v1/users/{user_id} — Fetch any user by ID
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user, get_db, require_active_user
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.user import UserProfile, UserResponse, UserUpdate

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get the current user's full profile",
)
async def get_profile(
    current_user: User = Depends(require_active_user),
) -> UserProfile:
    """
    Returns the authenticated user's profile.

    The ``organization`` relationship is pre-loaded by ``require_active_user``
    (via ``get_current_user`` → ``selectinload``), so we can safely read
    ``current_user.organization`` without issuing a second query.
    """
    # Build the response manually to include the denormalised org name.
    # Avoids mutating a validated Pydantic model instance after construction.
    org_name: str | None = None
    try:
        if current_user.organization is not None:
            org_name = current_user.organization.name
    except Exception:
        # Defensive: if the relationship was somehow not loaded, skip silently
        pass

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        organization_id=current_user.organization_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        organization_name=org_name,
    )


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the current user's profile",
)
async def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    updated = await crud_user.update(db, db_obj=current_user, obj_in=payload)
    log.info("user_profile_updated", user_id=str(current_user.id))
    return updated  # type: ignore[return-value]


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all users",
)
async def list_users(
    _: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Fetch a user by ID",
)
async def get_user(
    user_id: UUID,
    _: User = Depends(require_active_user),  # auth guard only
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user  # type: ignore[return-value]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user account",
)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    await db.delete(user)
    await db.commit()
    log.info("user_deleted", user_id=str(user_id), deleted_by=str(current_user.id))
    return None
