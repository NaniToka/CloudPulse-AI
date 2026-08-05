"""
Teams REST API Endpoints.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.tenant import TeamCreate, TeamResponse
from app.services.tenant_service import tenant_service, TenantService

router = APIRouter()


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED, summary="Create Team")
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Create a new team in an organization."""
    team = await service.create_team(db, payload)
    return TeamResponse.model_validate(team)


@router.get("", response_model=List[TeamResponse], summary="List Teams")
async def list_teams(
    organization_id: uuid.UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """List all teams in an organization."""
    teams = await service.get_teams(db, organization_id)
    return [TeamResponse.model_validate(t) for t in teams]
