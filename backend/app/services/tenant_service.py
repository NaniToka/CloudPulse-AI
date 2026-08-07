"""
Service Layer for Multi-Tenant Enterprise SaaS Architecture.
"""

import re
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.base  # noqa: F401
from app.crud.crud_tenant import crud_tenant
from app.models.tenant import (
    AuditLog,
    Invitation,
    Organization,
    OrganizationMember,
    Project,
    Team,
)
from app.schemas.tenant import (
    MemberInvitePayload,
    OrganizationCreate,
    OrganizationUpdate,
    ProjectCreate,
    TeamCreate,
)

log = structlog.get_logger(__name__)


class TenantService:
    """Tenant Service handling multi-tenant SaaS lifecycle."""

    def __init__(self, crud_repo=crud_tenant) -> None:
        self.crud = crud_repo

    async def create_organization(
        self, db: AsyncSession, payload: OrganizationCreate, owner_id: uuid.UUID
    ) -> Organization:
        """Create new Organization and assign Owner role."""
        now = datetime.now(UTC)
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
        await self.create_team(
            db,
            TeamCreate(
                organization_id=org.id,
                name="Core SRE Team",
                description="Primary DevOps & Incident Response Team",
            ),
        )
        await self.create_project(
            db,
            ProjectCreate(
                organization_id=org.id,
                name="Production Cloud Cluster",
                cloud_provider="AWS",
                environment="Production",
                region="us-east-1",
            ),
        )

        return org

    async def get_user_organizations(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[Organization]:
        return await self.crud.get_user_organizations(db, user_id)

    async def get_organization(self, db: AsyncSession, org_id: uuid.UUID) -> Organization | None:
        return await self.crud.get(db, id=org_id)

    async def update_organization(
        self, db: AsyncSession, org_id: uuid.UUID, payload: OrganizationUpdate
    ) -> Organization | None:
        org = await self.get_organization(db, org_id)
        if not org:
            return None
        now = datetime.now(UTC)
        if payload.name is not None:
            org.name = payload.name
        if payload.logo is not None:
            org.logo_url = payload.logo
        if payload.plan is not None:
            org.plan = payload.plan
        if payload.status is not None:
            org.status = payload.status
        org.updated_at = now
        await db.commit()
        await db.refresh(org)
        return org

    async def delete_organization(self, db: AsyncSession, org_id: uuid.UUID) -> bool:
        org = await self.get_organization(db, org_id)
        if not org:
            return False
        await db.delete(org)
        await db.commit()
        return True

    async def create_team(self, db: AsyncSession, payload: TeamCreate) -> Team:
        now = datetime.now(UTC)
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

    async def get_team(self, db: AsyncSession, team_id: uuid.UUID) -> Team | None:
        stmt = select(Team).where(Team.id == team_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_team(
        self,
        db: AsyncSession,
        team_id: uuid.UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Team | None:
        team = await self.get_team(db, team_id)
        if not team:
            return None
        if name is not None:
            team.name = name
        if description is not None:
            team.description = description
        await db.commit()
        await db.refresh(team)
        return team

    async def delete_team(self, db: AsyncSession, team_id: uuid.UUID) -> bool:
        team = await self.get_team(db, team_id)
        if not team:
            return False
        await db.delete(team)
        await db.commit()
        return True

    async def get_teams(self, db: AsyncSession, org_id: uuid.UUID) -> list[Team]:
        return await self.crud.get_teams(db, org_id)

    async def create_project(self, db: AsyncSession, payload: ProjectCreate) -> Project:
        now = datetime.now(UTC)
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

    async def get_project(self, db: AsyncSession, project_id: uuid.UUID) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        name: str | None = None,
        cloud_provider: str | None = None,
        environment: str | None = None,
        region: str | None = None,
        team_id: uuid.UUID | None = None,
    ) -> Project | None:
        project = await self.get_project(db, project_id)
        if not project:
            return None
        if name is not None:
            project.name = name
        if cloud_provider is not None:
            project.cloud_provider = cloud_provider
        if environment is not None:
            project.environment = environment
        if region is not None:
            project.region = region
        if team_id is not None:
            project.team_id = team_id
        await db.commit()
        await db.refresh(project)
        return project

    async def delete_project(self, db: AsyncSession, project_id: uuid.UUID) -> bool:
        project = await self.get_project(db, project_id)
        if not project:
            return False
        await db.delete(project)
        await db.commit()
        return True

    async def get_projects(self, db: AsyncSession, org_id: uuid.UUID) -> list[Project]:
        return await self.crud.get_projects(db, org_id)

    async def invite_member(
        self, db: AsyncSession, payload: MemberInvitePayload, invited_by: uuid.UUID
    ) -> Invitation:
        now = datetime.now(UTC)
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

    async def get_members(self, db: AsyncSession, org_id: uuid.UUID) -> list[dict[str, Any]]:
        rows = await self.crud.get_organization_members(db, org_id)
        result = []
        for member, user in rows:
            result.append(
                {
                    "id": str(member.id),
                    "organization_id": str(member.organization_id),
                    "user_id": str(member.user_id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": member.role,
                    "created_at": member.created_at,
                }
            )
        return result

    async def get_audit_logs(self, db: AsyncSession, org_id: uuid.UUID) -> list[AuditLog]:
        return await self.crud.get_audit_logs(db, org_id)


tenant_service = TenantService()
