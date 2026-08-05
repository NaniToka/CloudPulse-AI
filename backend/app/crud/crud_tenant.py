"""
CRUD Repository for Organizations, Teams, Projects, Members, Invitations, & Audit Logs.
"""

import uuid
from typing import List, Optional, Tuple, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
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


class CRUDTenant(CRUDBase[Organization, Any, Any]):
    """Tenant Repository managing multi-tenant SaaS structures."""

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.slug == slug)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_organizations(self, db: AsyncSession, user_id: uuid.UUID) -> List[Organization]:
        """Fetch all organizations a user belongs to."""
        stmt = (
            select(Organization)
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
            .order_by(Organization.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_organization_members(self, db: AsyncSession, org_id: uuid.UUID) -> List[Tuple[OrganizationMember, User]]:
        """Fetch all members of an organization with User objects."""
        stmt = (
            select(OrganizationMember, User)
            .join(User, User.id == OrganizationMember.user_id)
            .where(OrganizationMember.organization_id == org_id)
            .order_by(OrganizationMember.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.all())

    async def get_teams(self, db: AsyncSession, org_id: uuid.UUID) -> List[Team]:
        """Fetch all teams in an organization."""
        stmt = select(Team).where(Team.organization_id == org_id).order_by(Team.name.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_projects(self, db: AsyncSession, org_id: uuid.UUID) -> List[Project]:
        """Fetch all workspace projects in an organization."""
        stmt = select(Project).where(Project.organization_id == org_id).order_by(Project.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_audit_logs(self, db: AsyncSession, org_id: uuid.UUID, limit: int = 50) -> List[AuditLog]:
        """Fetch security audit trail for an organization."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.organization_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


crud_tenant = CRUDTenant(Organization)
