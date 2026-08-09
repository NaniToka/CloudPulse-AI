"""
Unified Database Initializer & Local Development Data Seeder.
Initializes tables and seeds rich deterministic baseline data for local development.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.crud_cost import seed_default_costs_if_empty
from app.models.organization import Organization
from app.models.tenant import OrganizationMember
from app.models.user import User

log = structlog.get_logger(__name__)


async def init_db(db: AsyncSession) -> None:
    """Seed initial admin user, organization, and baseline telemetry for local development."""
    log.info("init_db_seeding_check")

    try:
        await db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;"))
        await db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Active';"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS team_size VARCHAR(50);"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS industry VARCHAR(100);"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS member_count INTEGER DEFAULT 1;"))
        await db.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS owner_id UUID;"))

        # Incidents table migrations
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS description TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'HIGH';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'High';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'INVESTIGATING';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS source VARCHAR(100) DEFAULT 'correlation_engine';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS affected_service VARCHAR(255) DEFAULT 'api-gateway';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS affected_services JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS affected_resources JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS affected_region VARCHAR(100) DEFAULT 'us-east-1';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS assigned_engineer VARCHAR(255);"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(255);"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS created_by VARCHAR(255) DEFAULT 'System';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS detected_at TIMESTAMP WITH TIME ZONE;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITH TIME ZONE;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS resolution_notes TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS resolved_by VARCHAR(50);"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 0.94;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS impact_score FLOAT DEFAULT 85.0;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS root_cause TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS contributing_factors JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS evidence JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS correlation_metadata JSON DEFAULT '{}';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS recommended_actions JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS blast_radius JSON DEFAULT '{}';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_summary TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_root_cause TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_business_impact TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_suggested_resolution TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_immediate_mitigation TEXT;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_long_term_prevention JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_preventive_actions JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_similar_incidents JSON DEFAULT '[]';"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_estimated_resolution_time VARCHAR(100);"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ai_confidence_score FLOAT DEFAULT 0.94;"))
        await db.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS organization_id UUID;"))
        await db.execute(text("ALTER TABLE incidents ALTER COLUMN organization_id DROP NOT NULL;"))

        # Incident timeline events migrations
        await db.execute(text("ALTER TABLE incident_timeline_events ADD COLUMN IF NOT EXISTS source VARCHAR(100) DEFAULT 'system';"))
        await db.execute(text("ALTER TABLE incident_timeline_events ADD COLUMN IF NOT EXISTS event_metadata JSON DEFAULT '{}';"))
        await db.execute(text("ALTER TABLE incident_timeline_events ADD COLUMN IF NOT EXISTS created_by VARCHAR(255);"))
        await db.commit()
    except Exception as exc:
        await db.rollback()
        log.warning("schema_migration_check", error=str(exc))

    # 1. Seed Default Admin User & Organization
    admin_user = await _seed_admin_user_and_org(db)


    # 2. Seed Baseline Cost Optimizer Data
    if admin_user:
        await seed_default_costs_if_empty(db, admin_user.id)

    log.info("init_db_seeding_complete")



async def _seed_admin_user_and_org(db: AsyncSession) -> User | None:
    """Ensure default admin user exists for immediate local development login."""
    stmt = select(User).where(User.email == "admin@cloudpulse.io")
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        log.info("seeding_default_admin_user")

        # Create Organization
        org = Organization(
            id=uuid.uuid4(),
            name="CloudPulse Enterprise",
            slug="cloudpulse-enterprise",
            plan="enterprise",
            status="Active",
            created_at=datetime.now(UTC),
        )
        db.add(org)

        await db.flush()

        # Create Admin User
        user = User(
            id=uuid.uuid4(),
            email="admin@cloudpulse.io",
            hashed_password=hash_password("Password123!"),

            first_name="Admin",
            last_name="Engineer",
            role="admin",
            is_active=True,
            is_verified=True,
            organization_id=org.id,
            created_at=datetime.now(UTC),
        )
        db.add(user)
        await db.flush()

        # Link Org Member
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=user.id,
            role="admin",
            created_at=datetime.now(UTC),
        )
        db.add(member)
        await db.commit()
        log.info("default_admin_user_seeded", email="admin@cloudpulse.io")

    return user

