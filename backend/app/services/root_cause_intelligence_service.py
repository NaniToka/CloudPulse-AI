"""
AI Service Dependency & Root-Cause Intelligence Service.

Combines:
- Transparent 4-factor deterministic scoring model
- Service Dependency Graph topology depth
- Multi-modal telemetry anomalies & propagation cascades
- Grounded Google Gemini AI Diagnostics (Pydantic Schema)
- Explainable evidence graph records
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.incident import Incident
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.schemas.dependency import (
    BlastRadiusResponse,
    RootCauseCandidate,
    RootCauseRankingResponse,
)
from app.services.blast_radius_engine import blast_radius_engine

log = structlog.get_logger(__name__)


class GeminiRCAStructuredSchema(BaseModel):
    """Pydantic schema for strict Gemini AI response validation."""

    primary_root_cause: str = Field(..., description="The definitive root cause service or component")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning_summary: str = Field(..., description="Concise engineering explanation of the failure cascade")
    candidate_explanations: list[str] = Field(default_factory=list, description="Analysis of candidate services")
    recommended_actions: list[dict[str, Any]] = Field(default_factory=list, description="Remediation steps")
    preventive_actions: list[str] = Field(default_factory=list, description="Long-term prevention")


class RootCauseIntelligenceService:
    """Ranks and explains root cause candidates using topology and telemetry."""

    def _calculate_candidate_score(
        self,
        service_name: str,
        signals_for_svc: list[dict[str, Any]],
        all_signals: list[dict[str, Any]],
        in_degree: int,
        out_degree: int,
        is_backend_leaf: bool,
    ) -> tuple[float, float, float, float, float, list[dict[str, Any]]]:
        """
        Calculates transparent 4-factor root cause score:
        Score = 0.30 * Temporal + 0.25 * TopologyOrigin + 0.25 * AnomalySeverity + 0.20 * PropagationImpact
        """
        evidence_items: list[dict[str, Any]] = []
        now = datetime.now(UTC)

        # 1. Anomaly Severity (0.0 - 1.0)
        max_error = 0.0
        max_latency = 45.0
        has_critical_alert = False

        for s in signals_for_svc:
            err = float(s.get("error_rate") or s.get("value") or 0.0)
            if "error" in str(s.get("metric_name") or s.get("title") or "").lower():
                max_error = max(max_error, err)
            lat = float(s.get("latency_ms") or s.get("duration_ms") or 0.0)
            if "latency" in str(s.get("metric_name") or s.get("title") or "").lower() or lat > 0:
                max_latency = max(max_latency, lat)
            if str(s.get("severity", "")).upper() in ["CRITICAL", "P0"]:
                has_critical_alert = True

            evidence_items.append(
                {
                    "type": s.get("source") or s.get("event_type") or "telemetry",
                    "source": service_name,
                    "target": s.get("target") or service_name,
                    "observation": s.get("message") or s.get("title") or f"Degradation on {service_name}",
                    "timestamp": s.get("timestamp") or now.isoformat(),
                    "strength": 0.92 if has_critical_alert else 0.75,
                }
            )

        if signals_for_svc:
            err_score = min(1.0, max_error / 45.0)
            lat_score = min(1.0, max(0.0, (max_latency - 150.0) / 1800.0))
            crit_boost = 0.40 if has_critical_alert else 0.0
            anomaly_score = min(1.0, max(0.30, (err_score * 0.5) + (lat_score * 0.3) + crit_boost))
            temporal_score = 0.90
        else:
            anomaly_score = 0.05
            temporal_score = 0.10

        # 2. Topology Origin Score (0.0 - 1.0)
        # Backend dependencies / leaf resources that are called by others receive high origin score
        if is_backend_leaf or any(k in service_name for k in ["postgres", "mysql", "db", "redis", "database"]):
            topo_score = 0.95
        elif in_degree > out_degree:
            # More callers than callees => deeper in backend
            topo_score = 0.85
        elif any(k in service_name for k in ["payment", "billing", "auth"]):
            topo_score = 0.80
        elif any(k in service_name for k in ["order", "cart", "user"]):
            topo_score = 0.50
        elif any(k in service_name for k in ["gateway", "ingress", "frontend"]):
            topo_score = 0.25
        else:
            topo_score = 0.40

        # 4. Propagation Impact (0.0 - 1.0)
        # Services whose failure impacts the whole cluster
        propagation_score = min(1.0, 0.40 + (in_degree * 0.15))

        # Weighted final score
        final_score = (
            (0.30 * temporal_score)
            + (0.25 * topo_score)
            + (0.25 * anomaly_score)
            + (0.20 * propagation_score)
        )
        final_score = round(min(0.99, max(0.10, final_score)), 2)

        return (
            final_score,
            round(temporal_score, 2),
            round(topo_score, 2),
            round(anomaly_score, 2),
            round(propagation_score, 2),
            evidence_items,
        )

    def _generate_candidate_actions(self, service_name: str) -> list[dict[str, Any]]:
        """Generates contextual remediation actions for a candidate root cause."""
        svc = service_name.lower()
        if any(k in svc for k in ["db", "postgres", "mysql", "rds"]):
            return [
                {
                    "id": "act-db-scale-pool",
                    "title": f"Scale Connection Pool for {service_name}",
                    "action_type": "scale",
                    "workflow_id": "wf-db-pool-expand",
                    "automated": True,
                    "risk_level": "LOW",
                    "risk": "LOW",
                    "requires_approval": True,
                    "dry_run": True,
                },
                {
                    "id": "act-db-failover",
                    "title": f"Trigger Read Replica Promotion for {service_name}",
                    "action_type": "failover",
                    "workflow_id": "wf-db-failover",
                    "automated": False,
                    "risk_level": "HIGH",
                    "risk": "HIGH",
                    "requires_approval": True,
                    "dry_run": True,
                },
            ]
        elif any(k in svc for k in ["redis", "cache", "memcached"]):
            return [
                {
                    "id": "act-redis-flush-keys",
                    "title": f"Evict Expired Keys on {service_name}",
                    "action_type": "config",
                    "workflow_id": "wf-cache-evict",
                    "automated": True,
                    "risk_level": "LOW",
                    "risk": "LOW",
                    "requires_approval": True,
                    "dry_run": True,
                }
            ]
        else:
            return [
                {
                    "id": "act-k8s-scale",
                    "title": f"Scale {service_name} Replicas (+3)",
                    "action_type": "scale",
                    "workflow_id": "wf-k8s-autoscale",
                    "automated": True,
                    "risk_level": "LOW",
                    "risk": "LOW",
                    "requires_approval": True,
                    "dry_run": True,
                },
                {
                    "id": "act-k8s-restart",
                    "title": f"Perform Rolling Restart of {service_name}",
                    "action_type": "restart",
                    "workflow_id": "wf-k8s-rolling-restart",
                    "automated": True,
                    "risk_level": "LOW",
                    "risk": "LOW",
                    "requires_approval": True,
                    "dry_run": True,
                },
            ]

    async def _analyze_with_gemini(
        self,
        primary_candidate: str,
        candidates: list[RootCauseCandidate],
        all_signals: list[dict[str, Any]],
        blast: BlastRadiusResponse,
    ) -> tuple[dict[str, Any] | None, str]:
        """Invokes Google Gemini with Pydantic structured output validation."""
        api_key = settings.GEMINI_API_KEY
        if not api_key or "your-gemini-api-key" in api_key.lower():
            return None, "local"

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                },
            )

            prompt = (
                f"You are the CloudPulse-AI Chief SRE Diagnostic Engine.\n\n"
                f"Analyze this incident failure cascade:\n"
                f"- Primary Root Cause Candidate: {primary_candidate}\n"
                f"- Candidate Services Ranked: {[c.model_dump() for c in candidates]}\n"
                f"- Blast Radius Affected Services: {blast.affected_services}\n"
                f"- Propagation Paths: {blast.propagation_paths}\n"
                f"- Telemetry Signals: {all_signals[:8]}\n\n"
                f"Return JSON matching schema: {{'primary_root_cause': str, 'confidence': float, 'reasoning_summary': str, 'candidate_explanations': list[str], 'recommended_actions': list[dict], 'preventive_actions': list[str]}}."
            )

            response = await model.generate_content_async(prompt)
            if response and response.text:
                parsed = json.loads(response.text)
                validated = GeminiRCAStructuredSchema(**parsed)
                return validated.model_dump(), "gemini"

        except Exception as exc:
            log.warning("gemini_rca_diagnostic_failed", error=str(exc))

        return None, "local"

    async def rank_root_causes(
        self,
        db: AsyncSession,
        service_name: str | None = None,
        incident_id: uuid.UUID | None = None,
        signals: list[dict[str, Any]] | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> RootCauseRankingResponse:
        """
        Calculates explainable root cause candidate rankings using dependency topology and telemetry.
        """
        all_signals = list(signals or [])
        target_service = service_name

        # 1. If incident_id provided, load incident context
        if incident_id:
            inc_stmt = select(Incident).where(Incident.id == incident_id)
            inc_res = await db.execute(inc_stmt)
            incident = inc_res.scalar_one_or_none()
            if incident:
                if not target_service:
                    target_service = incident.affected_service
                if incident.evidence:
                    all_signals.extend(incident.evidence)

        if not target_service:
            target_service = "api-gateway"

        # 2. Fetch Dependency Graph
        dep_stmt = select(ServiceDependency).where(
            (ServiceDependency.organization_id == organization_id)
            if organization_id
            else ServiceDependency.organization_id.is_(None)
        )
        dep_res = await db.execute(dep_stmt)
        dependencies = dep_res.scalars().all()

        # In-degree (callers) and Out-degree (callees) maps
        in_degree_map: dict[str, int] = {}
        out_degree_map: dict[str, int] = {}
        unique_services: set[str] = {target_service.lower()}

        for d in dependencies:
            src = d.source_service.strip().lower()
            tgt = d.target_service.strip().lower()
            unique_services.add(src)
            unique_services.add(tgt)
            out_degree_map[src] = out_degree_map.get(src, 0) + 1
            in_degree_map[tgt] = in_degree_map.get(tgt, 0) + 1

        # Also add services mentioned in signals
        for s in all_signals:
            svc = s.get("service") or s.get("service_name") or s.get("source")
            if svc:
                unique_services.add(str(svc).strip().lower())

        # 3. Score every candidate service
        candidates: list[RootCauseCandidate] = []
        all_evidence_graph: list[dict[str, Any]] = []

        for svc_name in unique_services:
            svc_signals = [
                s
                for s in all_signals
                if str(s.get("service") or s.get("service_name") or s.get("source") or "").lower()
                == svc_name
            ]
            in_deg = in_degree_map.get(svc_name, 0)
            out_deg = out_degree_map.get(svc_name, 0)
            is_leaf = out_deg == 0 and in_deg > 0

            final_score, temp_sc, topo_sc, anom_sc, prop_sc, ev_items = self._calculate_candidate_score(
                service_name=svc_name,
                signals_for_svc=svc_signals,
                all_signals=all_signals,
                in_degree=in_deg,
                out_degree=out_deg,
                is_backend_leaf=is_leaf,
            )

            actions = self._generate_candidate_actions(svc_name)
            all_evidence_graph.extend(ev_items)

            candidate = RootCauseCandidate(
                service_name=svc_name,
                score=final_score,
                rank=1,
                temporal_score=temp_sc,
                dependency_score=topo_sc,
                anomaly_score=anom_sc,
                propagation_score=prop_sc,
                evidence=ev_items,
                recommended_actions=actions,
            )
            candidates.append(candidate)

        # 4. Sort Candidates by Score Descending
        candidates.sort(key=lambda c: c.score, reverse=True)
        for idx, c in enumerate(candidates, start=1):
            c.rank = idx

        primary_cand = candidates[0] if candidates else RootCauseCandidate(
            service_name=target_service,
            score=0.90,
            rank=1,
            temporal_score=0.85,
            dependency_score=0.85,
            anomaly_score=0.85,
            propagation_score=0.80,
            evidence=[],
            recommended_actions=self._generate_candidate_actions(target_service),
        )

        # 5. Compute Blast Radius for Primary Candidate
        blast = await blast_radius_engine.calculate_blast_radius(
            db, primary_cand.service_name, organization_id=organization_id
        )

        # 6. Run Gemini AI Diagnostics
        ai_result, analysis_engine = await self._analyze_with_gemini(
            primary_candidate=primary_cand.service_name,
            candidates=candidates[:5],
            all_signals=all_signals,
            blast=blast,
        )

        reasoning_summary = (
            (ai_result.get("reasoning_summary") if ai_result else None)
            or f"Primary root cause isolated to '{primary_cand.service_name}' (Score: {int(primary_cand.score * 100)}%). "
            f"Failure propagated downstream across {len(blast.affected_services)} dependent services "
            f"leading to cascading latency and elevated error rates."
        )

        confidence = (
            ai_result.get("confidence")
            if (ai_result and ai_result.get("confidence"))
            else primary_cand.score
        )

        recommended_actions = (
            (ai_result.get("recommended_actions") if ai_result else None)
            or primary_cand.recommended_actions
        )

        return RootCauseRankingResponse(
            primary_root_cause=primary_cand.service_name,
            primary_score=primary_cand.score,
            confidence=round(confidence, 2),
            candidates=candidates,
            reasoning_summary=reasoning_summary,
            evidence_graph=all_evidence_graph,
            blast_radius=blast,
            analysis_engine=analysis_engine,
            recommended_actions=recommended_actions,
        )


root_cause_intelligence_service = RootCauseIntelligenceService()
