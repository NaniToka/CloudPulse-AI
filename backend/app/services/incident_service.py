"""
Service Layer for Incident Management System.
Connects CRUD Repository, Gemini AI Service, and Real-time WebSocket Broadcaster.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_incident import crud_incident
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentCreate,
    IncidentResolve,
    IncidentResponse,
    IncidentStatsResponse,
    IncidentUpdate,
)
from app.services.incident_ai_service import analyze_incident_with_gemini
from app.services.websocket_manager import incident_ws_manager

log = structlog.get_logger(__name__)


class IncidentService:
    """Service layer orchestrating incident operations and AI analysis."""

    def __init__(self, crud_repo=crud_incident) -> None:
        self.crud = crud_repo

    async def list_incidents(
        self,
        db: AsyncSession,
        *,
        status: str | None = None,
        severity: str | None = None,
        priority: str | None = None,
        service: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Incident], int, int]:
        return await self.crud.get_filtered(
            db,
            status=status,
            severity=severity,
            priority=priority,
            service=service,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            size=size,
        )

    async def get_active(self, db: AsyncSession) -> list[Incident]:
        return await self.crud.get_active(db)

    async def get_stats(self, db: AsyncSession) -> IncidentStatsResponse:
        return await self.crud.get_stats(db)

    async def get_by_id(self, db: AsyncSession, incident_id: uuid.UUID) -> Incident | None:
        return await self.crud.get(db, incident_id)

    async def create(self, db: AsyncSession, payload: IncidentCreate) -> Incident:
        now = datetime.now(UTC)
        incident_data = payload.model_dump(exclude={"auto_analyze"})

        # Ensure started_at default
        if not incident_data.get("started_at"):
            incident_data["started_at"] = now

        # Ensure assigned_to and assigned_engineer synchronization
        if payload.assigned_engineer and not payload.assigned_to:
            incident_data["assigned_to"] = payload.assigned_engineer
        elif payload.assigned_to and not payload.assigned_engineer:
            incident_data["assigned_engineer"] = payload.assigned_to

        incident = Incident(**incident_data)

        if payload.auto_analyze:
            ai_data = await analyze_incident_with_gemini(
                title=payload.title,
                description=payload.description or "",
                severity=payload.severity.value,
                priority=payload.priority.value,
                affected_service=payload.affected_service or "api-gateway",
            )
            incident.ai_summary = ai_data.get("ai_summary")
            incident.root_cause = ai_data.get("root_cause")
            incident.ai_root_cause = ai_data.get("ai_root_cause")
            incident.ai_business_impact = ai_data.get("ai_business_impact")
            incident.ai_suggested_resolution = ai_data.get("ai_suggested_resolution")
            incident.ai_immediate_mitigation = ai_data.get("ai_immediate_mitigation")
            incident.ai_long_term_prevention = ai_data.get("ai_long_term_prevention")
            incident.ai_preventive_actions = ai_data.get("ai_preventive_actions")
            incident.ai_similar_incidents = ai_data.get("ai_similar_incidents")
            incident.ai_estimated_resolution_time = ai_data.get("ai_estimated_resolution_time")
            incident.ai_confidence_score = ai_data.get("ai_confidence_score", 0.94)

        db.add(incident)
        await db.commit()
        await db.refresh(incident)

        resp = IncidentResponse.model_validate(incident)

        # Broadcast WS event
        await incident_ws_manager.broadcast(
            {
                "event": "incident_created",
                "data": resp.model_dump(mode="json"),
                "timestamp": now.isoformat(),
            }
        )

        return incident

    async def update(
        self, db: AsyncSession, incident_id: uuid.UUID, payload: IncidentUpdate
    ) -> Incident | None:
        incident = await self.crud.get(db, incident_id)
        if not incident:
            return None

        old_severity = incident.severity
        old_assigned = incident.assigned_engineer or incident.assigned_to
        old_status = incident.status

        update_dict = payload.model_dump(exclude_unset=True)

        if "assigned_to" in update_dict and not update_dict.get("assigned_engineer"):
            update_dict["assigned_engineer"] = update_dict["assigned_to"]
        elif "assigned_engineer" in update_dict and not update_dict.get("assigned_to"):
            update_dict["assigned_to"] = update_dict["assigned_engineer"]

        if update_dict.get("status") in ["Resolved", "Closed"] and not incident.resolved_at:
            update_dict["resolved_at"] = datetime.now(UTC)

        update_dict["updated_at"] = datetime.now(UTC)

        updated_obj = await self.crud.update(db, db_obj=incident, obj_in=update_dict)
        resp = IncidentResponse.model_validate(updated_obj)

        # Broadcast events
        if old_severity != updated_obj.severity:
            await incident_ws_manager.broadcast(
                {
                    "event": "severity_changed",
                    "incident_id": str(updated_obj.id),
                    "old_severity": old_severity,
                    "new_severity": updated_obj.severity,
                    "data": resp.model_dump(mode="json"),
                }
            )

        if old_assigned != (updated_obj.assigned_engineer or updated_obj.assigned_to):
            await incident_ws_manager.broadcast(
                {
                    "event": "assignment_changed",
                    "incident_id": str(updated_obj.id),
                    "old_engineer": old_assigned,
                    "new_engineer": updated_obj.assigned_engineer or updated_obj.assigned_to,
                    "data": resp.model_dump(mode="json"),
                }
            )

        if old_status != updated_obj.status:
            await incident_ws_manager.broadcast(
                {
                    "event": "status_changed",
                    "incident_id": str(updated_obj.id),
                    "old_status": old_status,
                    "new_status": updated_obj.status,
                    "data": resp.model_dump(mode="json"),
                }
            )

        return updated_obj

    async def resolve(
        self, db: AsyncSession, incident_id: uuid.UUID, payload: IncidentResolve
    ) -> Incident | None:
        incident = await self.crud.get(db, incident_id)
        if not incident:
            return None

        now = datetime.now(UTC)
        update_data = {
            "status": "Resolved",
            "resolution_notes": payload.resolution_notes,
            "resolved_by": payload.resolved_by or "Engineer",
            "resolved_at": now,
            "updated_at": now,
        }

        updated_obj = await self.crud.update(db, db_obj=incident, obj_in=update_data)
        resp = IncidentResponse.model_validate(updated_obj)

        # Broadcast resolution
        await incident_ws_manager.broadcast(
            {
                "event": "incident_resolved",
                "incident_id": str(updated_obj.id),
                "resolution_notes": payload.resolution_notes,
                "data": resp.model_dump(mode="json"),
            }
        )

        return updated_obj

    async def analyze(self, db: AsyncSession, incident_id: uuid.UUID) -> dict[str, Any] | None:
        incident = await self.crud.get(db, incident_id)
        if not incident:
            return None

        ai_data = await analyze_incident_with_gemini(
            title=incident.title,
            description=incident.description or "",
            severity=incident.severity,
            priority=incident.priority,
            affected_service=incident.affected_service or "api-gateway",
        )

        update_dict = {
            "ai_summary": ai_data["ai_summary"],
            "root_cause": ai_data["root_cause"],
            "ai_root_cause": ai_data["ai_root_cause"],
            "ai_business_impact": ai_data["ai_business_impact"],
            "ai_suggested_resolution": ai_data["ai_suggested_resolution"],
            "ai_immediate_mitigation": ai_data["ai_immediate_mitigation"],
            "ai_long_term_prevention": ai_data["ai_long_term_prevention"],
            "ai_preventive_actions": ai_data["ai_preventive_actions"],
            "ai_similar_incidents": ai_data["ai_similar_incidents"],
            "ai_estimated_resolution_time": ai_data["ai_estimated_resolution_time"],
            "ai_confidence_score": ai_data.get("ai_confidence_score", 0.94),
            "updated_at": datetime.now(UTC),
        }

        await self.crud.update(db, db_obj=incident, obj_in=update_dict)
        return ai_data

    async def delete(self, db: AsyncSession, incident_id: uuid.UUID) -> bool:
        deleted = await self.crud.delete(db, id=incident_id)
        return deleted is not None


incident_service = IncidentService()
