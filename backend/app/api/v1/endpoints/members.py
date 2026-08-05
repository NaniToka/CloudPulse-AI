"""
Members, Invitations, & RBAC Permissions REST API Endpoints.
"""

import uuid
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import get_all_permissions_matrix
from app.models.user import User
from app.schemas.tenant import MemberInvitePayload, InvitationResponse, MemberResponse
from app.services.tenant_service import tenant_service, TenantService

router = APIRouter()


@router.post("/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED, summary="Invite User to Organization")
async def invite_member(
    payload: MemberInvitePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Invite a new user to join the organization with a assigned RBAC role."""
    invitation = await service.invite_member(db, payload, current_user.id)
    return InvitationResponse.model_validate(invitation)


@router.get("", response_model=List[MemberResponse], summary="List Organization Members")
async def list_members(
    organization_id: uuid.UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Retrieve members of an organization."""
    members = await service.get_members(db, organization_id)
    return [MemberResponse.model_validate(m) for m in members]


@router.get("/permissions", summary="Get Role-Permission Matrix")
async def get_permissions_matrix():
    """Retrieve granular role-permission matrix mapping for Owner, Admin, Manager, Engineer, Viewer."""
    return get_all_permissions_matrix()
