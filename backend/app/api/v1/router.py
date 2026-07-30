"""
API v1 root router.

All route groups are registered here with their prefixes and tags.
Add new endpoint modules here as the platform grows.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
