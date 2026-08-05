"""
Workspace Projects REST API Endpoints.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.tenant import ProjectCreate, ProjectResponse
from app.services.tenant_service import tenant_service, TenantService

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Create Workspace Project")
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Create a new workspace project."""
    project = await service.create_project(db, payload)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=List[ProjectResponse], summary="List Workspace Projects")
async def list_projects(
    organization_id: uuid.UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """List all workspace projects in an organization."""
    projects = await service.get_projects(db, organization_id)
    return [ProjectResponse.model_validate(p) for p in projects]
