"""
Multi-Cloud Observability REST API Endpoints (AWS, Azure, GCP).
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.cloud_observability import (
    CloudAccountCreate,
    CloudAccountResponse,
    CloudCostSummaryResponse,
    CloudHealthSummaryResponse,
    CloudResourceResponse,
    CloudSecuritySummaryResponse,
)
from app.services.cloud_observability_service import (
    CloudObservabilityService,
    cloud_observability_service,
)

router = APIRouter()


@router.get(
    "/accounts", response_model=list[CloudAccountResponse], summary="List Connected Cloud Accounts"
)
async def list_cloud_accounts(
    provider: str | None = Query(None, description="Filter provider (AWS, Azure, GCP)"),
    status_filter: str | None = Query(None, alias="status", description="Filter status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Retrieve connected AWS, Azure, and Google Cloud accounts."""
    accounts = await service.get_accounts(
        db, user_id=current_user.id, provider=provider, status=status_filter
    )
    return [CloudAccountResponse.model_validate(a) for a in accounts]


@router.post(
    "/accounts",
    response_model=CloudAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect Cloud Account",
)
async def connect_cloud_account(
    payload: CloudAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Connect a new cloud account (IAM Role, Service Principal, or Service Account Key)."""
    account = await service.create_account(
        db,
        user_id=current_user.id,
        name=payload.name,
        provider=payload.provider,
        account_id=payload.account_id,
        credentials_type=payload.credentials_type,
        credentials_meta=payload.credentials_meta,
        default_region=payload.default_region or "us-east-1",
        environment=payload.environment or "production",
    )
    return CloudAccountResponse.model_validate(account)


@router.get(
    "/resources", response_model=list[CloudResourceResponse], summary="List Multi-Cloud Resources"
)
async def list_cloud_resources(
    provider: str | None = Query(None, description="Filter provider (AWS, Azure, GCP)"),
    resource_type: str | None = Query(None, description="Filter resource type"),
    region: str | None = Query(None, description="Filter region"),
    status_filter: str | None = Query(None, alias="status", description="Filter status"),
    search: str | None = Query(None, description="Search resource name or service"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Explore auto-discovered infrastructure resources across AWS, Azure, and GCP."""
    resources = await service.get_resources(
        db,
        provider=provider,
        resource_type=resource_type,
        region=region,
        status=status_filter,
        search=search,
    )
    return [CloudResourceResponse.model_validate(r) for r in resources]


@router.get(
    "/cost", response_model=CloudCostSummaryResponse, summary="Get Multi-Cloud Cost Breakdown"
)
async def get_cloud_cost(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Retrieve cost burn rate, provider cost distribution, and forecasted savings."""
    return await service.get_cost_summary(db)


@router.get(
    "/security",
    response_model=CloudSecuritySummaryResponse,
    summary="Get Multi-Cloud Security Findings",
)
async def get_cloud_security(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Retrieve multi-cloud compliance score, vulnerabilities, and high-risk resources."""
    return await service.get_security_summary(db)


@router.get(
    "/health",
    response_model=CloudHealthSummaryResponse,
    summary="Get Multi-Cloud Health & AI Insights",
)
async def get_cloud_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Retrieve multi-cloud health score and Gemini AI architecture recommendations."""
    return await service.get_health_summary(db)


@router.post("/sync", summary="Trigger Auto-Discovery Sync")
async def trigger_cloud_sync(
    account_id: uuid.UUID | None = Query(None, description="Optional account ID to sync"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: CloudObservabilityService = Depends(lambda: cloud_observability_service),
):
    """Trigger real-time resource discovery and telemetry synchronization."""
    return await service.trigger_sync(db, account_id)
