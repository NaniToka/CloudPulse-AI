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

    if admin_user:
        # 2. Seed Baseline Cost Optimizer Data
        try:
            await seed_default_costs_if_empty(db, admin_user.id)
        except Exception as e:
            log.warning("seed_cost_skipped", error=str(e))

        # 3. Seed Incidents & Timeline Events
        try:
            from app.api.v1.endpoints.incidents import _seed_initial_incidents_if_empty, incident_service
            await _seed_initial_incidents_if_empty(db, incident_service)
        except Exception as e:
            log.warning("seed_incidents_skipped", error=str(e))

        # 4. Seed Predictions
        try:
            from app.api.v1.endpoints.predictions import _seed_initial_predictions_if_empty, prediction_service
            await _seed_initial_predictions_if_empty(db, prediction_service)
        except Exception as e:
            log.warning("seed_predictions_skipped", error=str(e))

        # 5. Seed Distributed Traces
        try:
            from app.api.v1.endpoints.traces import _seed_initial_traces_if_empty, trace_service
            await _seed_initial_traces_if_empty(db, trace_service)
        except Exception as e:
            log.warning("seed_traces_skipped", error=str(e))

        # 6. Seed Alerts
        try:
            from app.services.alert_service import alert_service
            await alert_service.get_alerts(db)
        except Exception as e:
            log.warning("seed_alerts_skipped", error=str(e))

        # 7. Seed Servers & Infrastructure
        try:
            from app.services.server_service import server_service
            await server_service.get_servers(db)
        except Exception as e:
            log.warning("seed_servers_skipped", error=str(e))

        # 8. Seed Security Scans & Findings
        try:
            from app.api.v1.endpoints.security import _seed_initial_security_scans_if_empty, security_service
            await _seed_initial_security_scans_if_empty(db, security_service)
        except Exception as e:
            log.warning("seed_security_skipped", error=str(e))

        # 9. Seed AIOps Recommendations
        try:
            from app.api.v1.endpoints.aiops import _seed_initial_aiops_recommendations, aiops_service
            await _seed_initial_aiops_recommendations(db, aiops_service)
        except Exception as e:
            log.warning("seed_aiops_skipped", error=str(e))

        # 10. Seed Kubernetes Clusters & Workloads
        try:
            from app.services.kubernetes_service import kubernetes_service
            await kubernetes_service.get_clusters(db, user_id=admin_user.id)
        except Exception as e:
            log.warning("seed_k8s_skipped", error=str(e))

        # 11. Seed Multi-Cloud Accounts & Resources
        try:
            from app.services.cloud_observability_service import cloud_observability_service
            await cloud_observability_service.get_accounts(db, user_id=admin_user.id)
        except Exception as e:
            log.warning("seed_cloud_skipped", error=str(e))

        # 12. Seed Digital Twin Infrastructure
        try:
            from app.services.digital_twin_service import digital_twin_service
            await digital_twin_service.get_or_create_twin(db, user_id=admin_user.id)
        except Exception as e:
            log.warning("seed_digital_twin_skipped", error=str(e))

        # 13. Seed Workflows & Templates
        try:
            from app.services.workflow_engine_service import workflow_engine_service
            await workflow_engine_service.get_workflows(db, user_id=admin_user.id)
        except Exception as e:
            log.warning("seed_workflows_skipped", error=str(e))

        # 14. Seed Auto-Remediation Runbooks
        try:
            from app.api.v1.endpoints.runbooks import _seed_initial_runbooks_if_empty, runbook_service
            await _seed_initial_runbooks_if_empty(db, runbook_service)
        except Exception as e:
            log.warning("seed_runbooks_skipped", error=str(e))

        # 15. Seed Vector Store RAG collections
        try:
            from app.services.rag_service import seed_infrastructure_rag_data
            seed_infrastructure_rag_data()
        except Exception as e:
            log.warning("seed_rag_skipped", error=str(e))

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

