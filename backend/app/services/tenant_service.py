"""
Service Layer for Multi-Tenant Enterprise SaaS Architecture.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

import app.db.base  # noqa: F401
from app.crud.crud_tenant import crud_tenant
from app.models.tenant import (
    Organization,
    Team,
    Project,
    OrganizationMember,
    TeamMember,
    Invitation,
    AuditLog,
)
from app.models.user import User
from app.schemas.tenant import (
    OrganizationCreate,
    OrganizationUpdate,
    TeamCreate,
    ProjectCreate,
    MemberInvitePayload,
)

log = structlog.get_logger(__name__)


class TenantService:
    """Tenant Service handling multi-tenant SaaS lifecycle."""

    def __init__(self, crud_repo=crud_tenant) -> None:
        self.crud = crud_repo

    async def create_organization(self, db: AsyncSession, payload: OrganizationCreate, owner_id: uuid.UUID) -> Organization:
        """Create new Organization and assign Owner role."""
        now = datetime.now(timezone.utc)
        slug = payload.slug or re.sub(r"[^a-z0-9]", "-", payload.name.lower()).strip("-")
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

        org = Organization(
            id=uuid.uuid4(),
            name=payload.name,
            slug=slug,
            logo_url=payload.logo,
            plan=payload.plan,
            status="Active",
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        db.add(org)

        # Add Owner Member
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=owner_id,
            role="Owner",
            created_at=now,
        )
        db.add(member)

        # Audit Log
        audit = AuditLog(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=owner_id,
            action="Organization.Created",
            details={"name": org.name, "plan": org.plan},
            created_at=now,
        )
        db.add(audit)

        await db.commit()
        await db.refresh(org)

        # Seed default team and project
        await self.create_team(db, TeamCreate(organization_id=org.id, name="Core SRE Team", description="Primary DevOps & Incident Response Team"))
        await self.create_project(db, ProjectCreate(organization_id=org.id, name="Production Cloud Cluster", cloud_provider="AWS", environment="Production", region="us-east-1"))

        return org

    async def get_user_organizations(self, db: AsyncSession, user_id: uuid.UUID) -> List[Organization]:
        return await self.crud.get_user_organizations(db, user_id)

    async def get_organization(self, db: AsyncSession, org_id: uuid.UUID) -> Optional[Organization]:
        return await self.crud.get(db, id=org_id)

    async def create_team(self, db: AsyncSession, payload: TeamCreate) -> Team:
        now = datetime.now(timezone.utc)
        team = Team(
            id=uuid.uuid4(),
            organization_id=payload.organization_id,
            name=payload.name,
            description=payload.description,
            created_at=now,
        )
        db.add(team)
        await db.commit()
        await db.refresh(team)
        return team

    async def get_teams(self, db: AsyncSession, org_id: uuid.UUID) -> List[Team]:
        return await self.crud.get_teams(db, org_id)

    async def create_project(self, db: AsyncSession, payload: ProjectCreate) -> Project:
        now = datetime.now(timezone.utc)
        project = Project(
            id=uuid.uuid4(),
            organization_id=payload.organization_id,
            team_id=payload.team_id,
            name=payload.name,
            cloud_provider=payload.cloud_provider,
            environment=payload.environment,
            region=payload.region,
            created_at=now,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    async def get_projects(self, db: AsyncSession, org_id: uuid.UUID) -> List[Project]:
        return await self.crud.get_projects(db, org_id)

    async def invite_member(self, db: AsyncSession, payload: MemberInvitePayload, invited_by: uuid.UUID) -> Invitation:
        now = datetime.now(timezone.utc)
        token = f"inv-{uuid.uuid4().hex}"

        invitation = Invitation(
            id=uuid.uuid4(),
            organization_id=payload.organization_id,
            email=payload.email,
            role=payload.role,
            invited_by=invited_by,
            token=token,
            status="Pending",
            created_at=now,
        )
        db.add(invitation)

        audit = AuditLog(
            id=uuid.uuid4(),
            organization_id=payload.organization_id,
            user_id=invited_by,
            action="Member.Invited",
            details={"email": payload.email, "role": payload.role},
            created_at=now,
        )
        db.add(audit)

        await db.commit()
        await db.refresh(invitation)
        return invitation

    async def get_members(self, db: AsyncSession, org_id: uuid.UUID) -> List[Dict[str, Any]]:
        rows = await self.crud.get_organization_members(db, org_id)
        result = []
        for member, user in rows:
            result.append({
                "id": str(member.id),
                "organization_id": str(member.organization_id),
                "user_id": str(member.user_id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": member.role,
                "created_at": member.created_at,
            })
        return result

    async def get_audit_logs(self, db: AsyncSession, org_id: uuid.UUID) -> List[AuditLog]:
        return await self.crud.get_audit_logs(db, org_id)


tenant_service = TenantService()
