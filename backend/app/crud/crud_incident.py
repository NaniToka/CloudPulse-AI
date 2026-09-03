"""
CRUD operations (Repository Pattern) for Incidents & Timeline Events.
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.incident import Incident, IncidentTimelineEvent
from app.schemas.incident import (
    IncidentAnalyticsResponse,
    IncidentCreate,
    IncidentStatsResponse,
    IncidentTimelineEventCreate,
    IncidentUpdate,
    MonthlyTrendPoint,
    SeverityCount,
)


class CRUDIncident(CRUDBase[Incident, IncidentCreate, IncidentUpdate]):
    """Incident Repository implementing database access patterns."""

    async def get_with_timeline(self, db: AsyncSession, incident_id: uuid.UUID) -> Incident | None:
        """Fetch an incident by ID with eagerly loaded timeline events."""
        stmt = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(selectinload(Incident.timeline_events))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> list[Incident]:
        """Fetch all active (non-resolved, non-closed) incidents."""
        filters = [func.lower(Incident.status).notin_(["resolved", "closed"])]
        if organization_id:
            filters.append(
                or_(Incident.organization_id == organization_id, Incident.organization_id.is_(None))
            )

        stmt = (
            select(Incident)
            .where(and_(*filters))
            .options(selectinload(Incident.timeline_events))
            .order_by(Incident.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_stats(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> IncidentStatsResponse:
        """Calculate KPI statistics for Incident Management Center."""
        base_filters = []
        if organization_id:
            base_filters.append(
                or_(Incident.organization_id == organization_id, Incident.organization_id.is_(None))
            )

        # Total active incidents (Open, Investigating, Monitoring, Detected, Mitigating)
        active_filters = base_filters + [func.lower(Incident.status).notin_(["resolved", "closed"])]
        active_stmt = select(func.count(Incident.id)).where(and_(*active_filters))
        active_res = await db.execute(active_stmt)
        open_incidents = active_res.scalar() or 0

        # Critical incidents (CRITICAL / P0 / P1 / HIGH) that are still active
        crit_filters = active_filters + [
            func.upper(Incident.severity).in_(["CRITICAL", "P0", "P1", "HIGH"])
        ]
        critical_stmt = select(func.count(Incident.id)).where(and_(*crit_filters))
        crit_res = await db.execute(critical_stmt)
        critical_incidents = crit_res.scalar() or 0

        # Calculate Average Resolution Time & SLA compliance from resolved incidents
        resolved_filters = base_filters + [Incident.resolved_at.isnot(None)]
        resolved_stmt = select(Incident).where(and_(*resolved_filters))
        res_items = list((await db.execute(resolved_stmt)).scalars().all())

        total_diff_minutes = 0.0
        valid_count = 0
        sla_met_count = 0

        for inc in res_items:
            ref_start = inc.started_at or inc.created_at
            if inc.resolved_at and ref_start:
                res_time = inc.resolved_at
                if res_time.tzinfo is None:
                    res_time = res_time.replace(tzinfo=UTC)
                if ref_start.tzinfo is None:
                    ref_start = ref_start.replace(tzinfo=UTC)
                diff_sec = (res_time - ref_start).total_seconds()
                if diff_sec >= 0:
                    diff_min = diff_sec / 60.0
                    total_diff_minutes += diff_min
                    valid_count += 1
                    target_sec = inc.sla_target_seconds or 1800
                    if diff_sec <= target_sec:
                        sla_met_count += 1

        avg_resolution_time = (
            round(total_diff_minutes / valid_count, 1) if valid_count > 0 else 0.0
        )
        sla_compliance = round((sla_met_count / valid_count) * 100, 1) if valid_count > 0 else 100.0

        return IncidentStatsResponse(
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            avg_resolution_time_minutes=avg_resolution_time,
            sla_compliance_percent=sla_compliance,
        )

    async def get_analytics(
        self, db: AsyncSession, organization_id: uuid.UUID | None = None
    ) -> IncidentAnalyticsResponse:
        """Computes comprehensive Incident Analytics and MTTR from real database records."""
        base_filters = []
        if organization_id:
            base_filters.append(
                or_(Incident.organization_id == organization_id, Incident.organization_id.is_(None))
            )

        # Fetch all incidents
        stmt = select(Incident).where(and_(*base_filters) if base_filters else True).order_by(Incident.created_at.desc())
        res = await db.execute(stmt)
        all_incidents = list(res.scalars().all())

        total_incidents = len(all_incidents)
        resolved_incidents = 0
        critical_incidents = 0
        high_incidents = 0

        by_severity: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        by_service: dict[str, int] = {}
        root_cause_counts: dict[str, int] = {}

        mttr_values_sec: list[float] = []
        sla_met_count = 0

        for inc in all_incidents:
            sev_u = (inc.severity or "HIGH").upper()
            if sev_u in ["CRITICAL", "P0"]:
                by_severity["CRITICAL"] += 1
                critical_incidents += 1
            elif sev_u in ["HIGH", "P1"]:
                by_severity["HIGH"] += 1
                high_incidents += 1
            elif sev_u in ["MEDIUM", "P2"]:
                by_severity["MEDIUM"] += 1
            else:
                by_severity["LOW"] += 1

            svc = inc.affected_service or "api-gateway"
            by_service[svc] = by_service.get(svc, 0) + 1

            if inc.root_cause:
                rc_key = inc.root_cause.strip()
                root_cause_counts[rc_key] = root_cause_counts.get(rc_key, 0) + 1

            is_resolved = str(inc.status).upper() in ["RESOLVED", "CLOSED"] or inc.resolved_at is not None
            if is_resolved:
                resolved_incidents += 1
                ref_start = inc.started_at or inc.created_at
                if inc.resolved_at and ref_start:
                    res_time = inc.resolved_at
                    if res_time.tzinfo is None:
                        res_time = res_time.replace(tzinfo=UTC)
                    if ref_start.tzinfo is None:
                        ref_start = ref_start.replace(tzinfo=UTC)
                    diff_sec = inc.mttr_seconds if inc.mttr_seconds is not None else (res_time - ref_start).total_seconds()
                    if diff_sec >= 0:
                        mttr_values_sec.append(diff_sec)
                        target_sec = inc.sla_target_seconds or 1800
                        if diff_sec <= target_sec:
                            sla_met_count += 1

        open_incidents = total_incidents - resolved_incidents

        # Average and Median MTTR
        if mttr_values_sec:
            avg_mttr_sec = sum(mttr_values_sec) / len(mttr_values_sec)
            sorted_mttr = sorted(mttr_values_sec)
            mid = len(sorted_mttr) // 2
            if len(sorted_mttr) % 2 == 0:
                median_mttr_sec = (sorted_mttr[mid - 1] + sorted_mttr[mid]) / 2.0
            else:
                median_mttr_sec = sorted_mttr[mid]
            sla_compliance = round((sla_met_count / len(mttr_values_sec)) * 100, 1)
        else:
            avg_mttr_sec = 0.0
            median_mttr_sec = 0.0
            sla_compliance = 100.0

        # Top root causes
        sorted_rc = sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_root_causes = [{"root_cause": k, "count": v} for k, v in sorted_rc]

        incidents_by_severity = [
            SeverityCount(severity=k, count=v) for k, v in by_severity.items()
        ]

        resolution_rate = (
            round((resolved_incidents / total_incidents) * 100, 1) if total_incidents > 0 else 0.0
        )

        now = datetime.now(UTC)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        current_month = months[now.month - 1]
        monthly_trend = [
            MonthlyTrendPoint(month=current_month, count=total_incidents, resolved_count=resolved_incidents)
        ]

        return IncidentAnalyticsResponse(
            total_incidents=total_incidents,
            open_incidents=open_incidents,
            resolved_incidents=resolved_incidents,
            critical_incidents=critical_incidents,
            high_incidents=high_incidents,
            average_mttr_seconds=round(avg_mttr_sec, 1),
            median_mttr_seconds=round(median_mttr_sec, 1),
            sla_compliance_percent=sla_compliance,
            by_severity=by_severity,
            by_service=by_service,
            top_root_causes=top_root_causes,
            incidents_by_severity=incidents_by_severity,
            mean_time_to_resolve_minutes=round(avg_mttr_sec / 60.0, 1),
            monthly_trend=monthly_trend,
            resolution_rate_percent=resolution_rate,
            active_incidents=open_incidents,
        )

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        status: str | None = None,
        severity: str | None = None,
        priority: str | None = None,
        service: str | None = None,
        environment: str | None = None,
        region: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Incident], int, int]:
        """Fetch filtered and paginated list of incidents with total count."""
        query = select(Incident).options(selectinload(Incident.timeline_events))

        filters = []
        if organization_id:
            filters.append(
                or_(Incident.organization_id == organization_id, Incident.organization_id.is_(None))
            )
        if status:
            filters.append(func.lower(Incident.status) == status.lower())
        if severity:
            filters.append(func.upper(Incident.severity) == severity.upper())
        if priority:
            filters.append(func.lower(Incident.priority) == priority.lower())
        if service:
            filters.append(func.lower(Incident.affected_service) == service.lower())
        if environment:
            filters.append(func.lower(Incident.environment) == environment.lower())
        if region:
            filters.append(func.lower(Incident.affected_region) == region.lower())
        if start_date:
            filters.append(Incident.created_at >= start_date)
        if end_date:
            filters.append(Incident.created_at <= end_date)

        if search:
            search_pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Incident.title).like(search_pattern),
                    func.lower(Incident.description).like(search_pattern),
                    func.lower(Incident.affected_service).like(search_pattern),
                    func.lower(Incident.assigned_engineer).like(search_pattern),
                    func.lower(Incident.assigned_to).like(search_pattern),
                    func.lower(Incident.root_cause).like(search_pattern),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Sorting
        sort_column = getattr(Incident, sort_by, Incident.created_at)
        if sort_dir.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        incidents = list(result.scalars().all())
        pages = math.ceil(total / size) if total > 0 else 1

        return incidents, total, pages

    async def get_timeline(
        self, db: AsyncSession, incident_id: uuid.UUID
    ) -> list[IncidentTimelineEvent]:
        """Fetch all timeline events for an incident ordered chronologically."""
        stmt = (
            select(IncidentTimelineEvent)
            .where(IncidentTimelineEvent.incident_id == incident_id)
            .order_by(IncidentTimelineEvent.timestamp.asc(), IncidentTimelineEvent.id.asc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def add_timeline_event(
        self,
        db: AsyncSession,
        incident_id: uuid.UUID,
        payload: IncidentTimelineEventCreate,
        created_by: str | None = "Engineer",
    ) -> IncidentTimelineEvent:
        """Appends a new timeline event to the incident."""
        now = payload.timestamp or datetime.now(UTC)
        evt = IncidentTimelineEvent(
            id=uuid.uuid4(),
            incident_id=incident_id,
            timestamp=now,
            event_type=payload.event_type,
            title=payload.title,
            description=payload.description,
            source=payload.source,
            event_metadata=payload.event_metadata,
            created_by=created_by,
        )
        db.add(evt)
        await db.commit()
        await db.refresh(evt)
        return evt


crud_incident = CRUDIncident(Incident)
