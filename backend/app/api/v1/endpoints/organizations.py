"""
Organizations REST API Endpoints.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.tenant import (
    AuditLogResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.tenant_service import TenantService, tenant_service

router = APIRouter()


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Create a new multi-tenant Organization and set current user as Owner."""
    org = await service.create_organization(db, payload, current_user.id)
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=list[OrganizationResponse], summary="List User Organizations")
async def list_user_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """List all organizations current user belongs to."""
    orgs = await service.get_user_organizations(db, current_user.id)
    if not orgs:
        # Seed default organization for current user if none exists
        default_org = await service.create_organization(
            db,
            OrganizationCreate(name="CloudPulse Global Corp", plan="Enterprise"),
            current_user.id,
        )
        orgs = [default_org]
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get("/{org_id}", response_model=OrganizationResponse, summary="Get Organization Details")
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Retrieve organization metadata."""
    org = await service.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


@router.patch("/{org_id}", response_model=OrganizationResponse, summary="Update Organization")
async def update_organization(
    org_id: uuid.UUID,
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Update organization settings."""
    org = await service.update_organization(db, org_id, payload)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Organization")
async def delete_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Delete an organization."""
    success = await service.delete_organization(db, org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return None


@router.get(
    "/{org_id}/audit-logs",
    response_model=list[AuditLogResponse],
    summary="Get Organization Audit Trail",
)
async def get_audit_logs(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TenantService = Depends(lambda: tenant_service),
):
    """Retrieve security audit logs for an organization."""
    logs = await service.get_audit_logs(db, org_id)
    return [AuditLogResponse.model_validate(log_item) for log_item in logs]
