"""
User management endpoints (protected).

GET    /users/me         — profile
PATCH  /users/me         — update profile
GET    /users/{id}       — get user by ID (admin)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, get_db
from app.crud.crud_user import crud_user
from app.schemas.user import UserProfileResponse, UserUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse, summary="Get current user profile")
async def get_my_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, UUID(current_user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile = UserProfileResponse.model_validate(user)
    if user.organization:
        profile.organization_name = user.organization.name
    return profile


@router.patch("/me", response_model=UserResponse, summary="Update current user profile")
async def update_my_profile(
    payload: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, UUID(current_user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user = await crud_user.update(db, db_obj=user, obj_in=payload)
    return user


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user_by_id(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user
