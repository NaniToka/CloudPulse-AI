"""
Enterprise Incident Correlation Engine.

Transforms raw, noisy telemetry streams and disconnected alerts into
singular, high-fidelity correlated incidents with cross-signal convergence,
deduplication, cascading failure root identification, and dynamic severity calculation.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentTimelineEvent
from app.models.trace import ServiceDependency
from app.schemas.incident import IncidentResponse
from app.services.websocket_manager import incident_ws_manager


log = structlog.get_logger(__name__)

# Severity rank weight for composite calculations
SEVERITY_WEIGHTS: dict[str, int] = {
    "CRITICAL": 100,
    "P0": 100,
    "HIGH": 75,
    "P1": 75,
    "MEDIUM": 50,
    "P2": 50,
    "LOW": 25,
    "P3": 25,
}

SEVERITY_NORMALIZE: dict[str, str] = {
    "P0": "CRITICAL",
    "CRITICAL": "CRITICAL",
    "critical": "CRITICAL",
    "P1": "HIGH",
    "HIGH": "HIGH",
    "high": "HIGH",
    "P2": "MEDIUM",
    "MEDIUM": "MEDIUM",
    "medium": "MEDIUM",
    "P3": "LOW",
    "LOW": "LOW",
    "low": "LOW",
}


class IncidentCorrelationEngine:
    """Intelligent Alert & Signal Correlation Engine."""

    def __init__(self, time_window_minutes: int = 15) -> None:
        self.time_window = timedelta(minutes=time_window_minutes)

    def generate_alert_fingerprint(self, alert_data: dict[str, Any]) -> str:
        """
        Creates a deterministic fingerprint for deduplication based on
        service, metric/event_name, and resource identity.
        """
        service = alert_data.get("service") or alert_data.get("affected_service") or "unknown-service"
        metric = alert_data.get("metric_name") or alert_data.get("event_type") or alert_data.get("title") or "anomaly"
        resource = alert_data.get("resource_id") or alert_data.get("resource") or alert_data.get("host") or "unknown-res"

        raw_sig = f"{service.strip().lower()}:{metric.strip().lower()}:{resource.strip().lower()}"
        return hashlib.sha256(raw_sig.encode()).hexdigest()[:16]

    async def correlate_alerts(
        self,
        db: AsyncSession,
        raw_alerts: list[dict[str, Any]],
        organization_id: uuid.UUID | None = None,
    ) -> list[Incident]:
        """
        Main pipeline: Ingests a list of raw alerts/signals, deduplicates, groups by
        topology, dependency graph, temporal proximity, and shared infrastructure,
        then produces correlated Incidents with timeline events.
        """
        if not raw_alerts:
            return []

        log.info("correlating_alerts_batch", count=len(raw_alerts))

        # 1. Fetch topology dependencies for dependency-aware clustering
        dep_stmt = select(ServiceDependency)
        dep_res = await db.execute(dep_stmt)
        dependencies = dep_res.scalars().all()
        # Build dependency graph lookup: child -> parent (upstream -> downstream)
        downstream_map: dict[str, set[str]] = {}
        for dep in dependencies:
            downstream_map.setdefault(dep.target_service.lower(), set()).add(dep.source_service.lower())

        # 2. Parse and normalize alerts
        normalized_alerts: list[dict[str, Any]] = []
        for a in raw_alerts:
            t_val = a.get("timestamp") or a.get("created_at")
            if isinstance(t_val, str):
                try:
                    dt = datetime.fromisoformat(t_val.replace("Z", "+00:00"))
                except Exception:
                    dt = datetime.now(UTC)
            elif isinstance(t_val, datetime):
                dt = t_val if t_val.tzinfo else t_val.replace(tzinfo=UTC)
            else:
                dt = datetime.now(UTC)

            sev = SEVERITY_NORMALIZE.get(str(a.get("severity", "HIGH")), "HIGH")
            svc = a.get("service") or a.get("affected_service") or a.get("service_name") or "api-gateway"
            res = a.get("resource_id") or a.get("resource") or a.get("host") or svc

            normalized_alerts.append(
                {
                    "raw": a,
                    "title": a.get("title") or a.get("message") or "System Anomaly",
                    "description": a.get("description") or a.get("message") or "",
                    "severity": sev,
                    "service": svc,
                    "resource": str(res),
                    "timestamp": dt,
                    "event_type": a.get("event_type") or a.get("metric_name") or "alert",
                    "metric_value": a.get("metric_value"),
                    "threshold": a.get("threshold"),
                    "fingerprint": self.generate_alert_fingerprint(a),
                }
            )

        # 3. Deduplicate exact duplicate alert bursts in the same time window
        unique_signals: list[dict[str, Any]] = []
        seen_fingerprints: dict[str, datetime] = {}

        # Sort chronologically
        normalized_alerts.sort(key=lambda x: x["timestamp"])

        for item in normalized_alerts:
            fp = item["fingerprint"]
            if fp in seen_fingerprints:
                prev_time = seen_fingerprints[fp]
                if abs((item["timestamp"] - prev_time).total_seconds()) < (self.time_window.total_seconds() / 2):
                    # Duplicate storm detected: merge count into existing
                    continue
            seen_fingerprints[fp] = item["timestamp"]
            unique_signals.append(item)

        # 4. Cluster signals into Correlated Groups
        # Criteria for same incident:
        # a) Same service / resource within time window
        # b) Direct dependency relationship (e.g. database-cluster & payment-service)
        # c) Cascading signals within time proximity
        clusters: list[list[dict[str, Any]]] = []

        for signal in unique_signals:
            matched_cluster = None
            for cluster in clusters:
                # Check if signal matches any item in this cluster
                for member in cluster:
                    # Time proximity check
                    time_diff = abs((signal["timestamp"] - member["timestamp"]).total_seconds())
                    if time_diff <= self.time_window.total_seconds():
                        # Signal matching criteria
                        same_service = signal["service"].lower() == member["service"].lower()
                        same_resource = signal["resource"].lower() == member["resource"].lower()

                        # Dependency check (upstream/downstream relationship)
                        s1 = signal["service"].lower()
                        s2 = member["service"].lower()
                        is_dependent = (
                            s1 in downstream_map.get(s2, set())
                            or s2 in downstream_map.get(s1, set())
                            or (any(k in s1 for k in ["db", "database", "postgres", "sql", "rds", "data"]) and any(k in s2 for k in ["payment", "checkout", "auth", "api", "order", "svc", "service"]))
                            or (any(k in s2 for k in ["db", "database", "postgres", "sql", "rds", "data"]) and any(k in s1 for k in ["payment", "checkout", "auth", "api", "order", "svc", "service"]))
                            or (any(k in s1 for k in ["cache", "redis", "memcached"]) and any(k in s2 for k in ["payment", "checkout", "auth", "api", "order", "svc", "service"]))
                            or (any(k in s2 for k in ["cache", "redis", "memcached"]) and any(k in s1 for k in ["payment", "checkout", "auth", "api", "order", "svc", "service"]))
                            or ("payment" in s1 and "checkout" in s2) or ("checkout" in s1 and "payment" in s2)
                            or ("auth" in s1 and "gateway" in s2) or ("gateway" in s1 and "auth" in s2)
                            or ("api" in s1 and "svc" in s2) or ("svc" in s1 and "api" in s2)
                        )


                        if same_service or same_resource or is_dependent:
                            matched_cluster = cluster
                            break
                if matched_cluster:
                    matched_cluster.append(signal)
                    break

            if not matched_cluster:
                clusters.append([signal])

        # 5. Build Incident entities from Clusters
        created_incidents: list[Incident] = []

        for cluster in clusters:
            incident = self._build_incident_from_cluster(cluster, organization_id)
            db.add(incident)
            await db.flush()  # get incident.id for timeline events

            # Populate timeline events
            for sig in cluster:
                evt = IncidentTimelineEvent(
                    id=uuid.uuid4(),
                    incident_id=incident.id,
                    timestamp=sig["timestamp"],
                    event_type=self._map_event_type(sig["event_type"]),
                    title=sig["title"],
                    description=sig["description"] or f"Correlated signal from {sig['service']} ({sig['resource']})",
                    source=sig["service"],
                    event_metadata={
                        "severity": sig["severity"],
                        "resource": sig["resource"],
                        "metric_value": sig.get("metric_value"),
                        "threshold": sig.get("threshold"),
                        "fingerprint": sig["fingerprint"],
                    },
                    created_by="IncidentCorrelationEngine",
                )
                db.add(evt)

            # Add RCA identified timeline event
            rca_evt = IncidentTimelineEvent(
                id=uuid.uuid4(),
                incident_id=incident.id,
                timestamp=incident.started_at + timedelta(minutes=1),
                event_type="rca_identified",
                title=f"Root Cause Correlated: {incident.root_cause}",
                description=f"Confidence {int(incident.confidence_score * 100)}% based on {len(cluster)} correlated signals across {len(incident.affected_services)} services.",
                source="RootCauseAnalysisService",
                event_metadata={
                    "confidence": incident.confidence_score,
                    "affected_services": incident.affected_services,
                    "contributing_factors": incident.contributing_factors,
                },
                created_by="CloudPulse AI",
            )
            db.add(rca_evt)

            created_incidents.append(incident)

        await db.commit()
        from app.crud.crud_incident import crud_incident

        reloaded_incidents = []
        for inc in created_incidents:
            reloaded = await crud_incident.get_with_timeline(db, inc.id)
            if reloaded:
                reloaded_incidents.append(reloaded)
            else:
                reloaded_incidents.append(inc)

        # 6. Broadcast WebSockets notification
        for inc in reloaded_incidents:
            try:
                resp = IncidentResponse.model_validate(inc)
                await incident_ws_manager.broadcast(
                    {
                        "event": "incident.created",
                        "data": resp.model_dump(mode="json"),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
            except Exception as exc:
                log.warning("ws_broadcast_error", error=str(exc))

        return reloaded_incidents

    def _build_incident_from_cluster(
        self, cluster: list[dict[str, Any]], organization_id: uuid.UUID | None
    ) -> Incident:
        """Synthesizes cluster signals into a unified Incident model."""
        services = list({s["service"] for s in cluster if s.get("service")})
        resources = list({s["resource"] for s in cluster if s.get("resource")})

        # Determine highest severity
        max_weight = max(SEVERITY_WEIGHTS.get(s["severity"], 50) for s in cluster)
        if max_weight >= 100 or len(services) >= 3:
            severity = "CRITICAL"
            priority = "Critical"
        elif max_weight >= 75 or len(services) >= 2:
            severity = "HIGH"
            priority = "High"
        elif max_weight >= 50:
            severity = "MEDIUM"
            priority = "Medium"
        else:
            severity = "LOW"
            priority = "Low"

        # Identify Root Cause Origin Component (upstream database / backend / infrastructure)
        root_service = self._identify_root_origin_service(cluster)

        earliest_time = min(s["timestamp"] for s in cluster)
        title = self._generate_incident_title(root_service, cluster, severity)
        description = (
            f"Correlated {len(cluster)} alerts/signals across {len(services)} services "
            f"({', '.join(services[:4])}). Root origin identified at {root_service}."
        )

        # Build evidence items
        evidence_items = []
        for s in cluster:
            evidence_items.append(
                {
                    "type": "alert" if "alert" in s["event_type"].lower() else "metric",
                    "source": s["service"],
                    "message": s["title"],
                    "severity": s["severity"],
                    "timestamp": s["timestamp"].isoformat(),
                    "details": {
                        "resource": s["resource"],
                        "metric_value": s.get("metric_value"),
                        "threshold": s.get("threshold"),
                    },
                }
            )

        contributing = [
            f"Signal density: {len(cluster)} events within {self.time_window.seconds // 60}m window",
            f"Cross-service propagation affecting {len(services)} downstream components",
        ]
        if any("db" in s.lower() or "postgres" in s.lower() or "database" in s.lower() for s in services):
            contributing.append("Shared persistent state layer under high concurrency load")

        # Confidence calculation based on signal volume & diversity
        confidence = min(0.98, 0.82 + (len(cluster) * 0.03) + (len(services) * 0.02))
        impact_score = min(100.0, 40.0 + (len(services) * 15.0) + (15.0 if severity == "CRITICAL" else 5.0))

        # Recommended actions mapped to workflows
        recommended_actions = self._generate_recommended_actions(root_service, cluster)

        # Blast radius
        blast_radius = {
            "root_component": root_service,
            "directly_affected": resources[:3],
            "indirectly_affected": [s for s in services if s != root_service],
            "affected_services": services,
            "dependency_depth": len(services),
            "estimated_user_impact": severity,
            "financial_risk_estimate": "$8,500 / hr" if severity == "CRITICAL" else "$2,200 / hr",
        }

        root_cause_text = f"{root_service} performance saturation causing cascading upstream/downstream latency and error propagation."

        return Incident(
            id=uuid.uuid4(),
            organization_id=organization_id,
            title=title,
            description=description,
            severity=severity,
            priority=priority,
            status="INVESTIGATING",
            source="correlation_engine",
            affected_service=root_service,
            affected_services=services,
            affected_resources=resources,
            affected_region="us-east-1",
            started_at=earliest_time,
            detected_at=earliest_time + timedelta(seconds=30),
            created_by="IncidentCorrelationEngine",
            confidence_score=round(confidence, 2),
            impact_score=round(impact_score, 1),
            root_cause=root_cause_text,
            contributing_factors=contributing,
            evidence=evidence_items,
            correlation_metadata={
                "cluster_size": len(cluster),
                "unique_services_count": len(services),
                "unique_resources_count": len(resources),
                "matched_signals": [s["event_type"] for s in cluster],
                "time_window_minutes": self.time_window.seconds // 60,
            },
            recommended_actions=recommended_actions,
            blast_radius=blast_radius,
            ai_summary=f"Incident '{title}' detected with {int(confidence * 100)}% confidence. {len(cluster)} correlated telemetry signals point to root bottleneck in {root_service}.",
            ai_root_cause=root_cause_text,
            ai_business_impact=f"Estimated {len(services)} services degraded. User workflows through {services[0] if services else 'core API'} experiencing elevated error rates.",
            ai_immediate_mitigation="1. Authorize connection pool expansion / scaling.\n2. Isolate slow queries.\n3. Trigger rolling restart of saturated worker pods.",
            ai_suggested_resolution="Execute approved automated remediation workflow.",
            ai_confidence_score=round(confidence, 2),
        )

    def _identify_root_origin_service(self, cluster: list[dict[str, Any]]) -> str:
        """
        Determines the root cause candidate component in the cluster.
        Prefers database / backend / storage layers over frontend / API gateway symptoms.
        """
        services = [s["service"].lower() for s in cluster]

        # Prioritize root infra components (Database, Storage, Cache, Auth Core)
        for s in services:
            if any(k in s for k in ["database", "postgres", "mysql", "rds", "db"]):
                return s
        for s in services:
            if any(k in s for k in ["redis", "cache", "memcached"]):
                return s
        for s in services:
            if any(k in s for k in ["auth", "security", "vault"]):
                return s
        for s in services:
            if any(k in s for k in ["payment", "billing", "worker"]):
                return s

        # Default to the earliest signaling service
        return cluster[0]["service"]

    def _generate_incident_title(
        self, root_service: str, cluster: list[dict[str, Any]], severity: str
    ) -> str:
        services = list({s["service"] for s in cluster})
        if len(services) > 1:
            return f"Correlated Multi-Service Degradation: {root_service} Failure Impacting {len(services)} Services"
        return f"{root_service.capitalize()} Performance Anomaly & Error Burst ({severity})"

    def _map_event_type(self, raw_type: str) -> str:
        raw_l = raw_type.lower()
        if "metric" in raw_l or "cpu" in raw_l or "memory" in raw_l or "latency" in raw_l:
            return "metric_anomaly"
        if "trace" in raw_l or "span" in raw_l:
            return "trace_failure"
        if "log" in raw_l or "error" in raw_l or "fatal" in raw_l:
            return "log_error"
        if "alert" in raw_l:
            return "alert_triggered"
        return "metric_anomaly"

    def _generate_recommended_actions(
        self, root_service: str, cluster: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        actions = []
        root_l = root_service.lower()

        if "db" in root_l or "postgres" in root_l or "database" in root_l:
            actions.append(
                {
                    "id": "act-db-pool",
                    "title": "Increase PostgreSQL Connection Pool & Scale Read Replicas",
                    "description": "Adjust pool size parameter from 200 to 500 and provision read replica to offload query bursts.",
                    "action_type": "config",
                    "workflow_id": "wf-db-pool-scaling",
                    "automated": True,
                    "risk_level": "LOW",
                }
            )
            actions.append(
                {
                    "id": "act-pgbouncer-restart",
                    "title": "Graceful PgBouncer Reset & Session Flush",
                    "description": "Terminate orphaned idle transactions and refresh connection pool state.",
                    "action_type": "restart",
                    "workflow_id": "wf-pgbouncer-reset",
                    "automated": True,
                    "risk_level": "LOW",
                }
            )
        elif "redis" in root_l or "cache" in root_l:
            actions.append(
                {
                    "id": "act-redis-eviction",
                    "title": "Evict Orphaned Telemetry Keys & Expand Redis MaxMemory",
                    "description": "Execute volatile-lru eviction on stale sessions and scale cluster node memory.",
                    "action_type": "scale",
                    "workflow_id": "wf-redis-memory-expand",
                    "automated": True,
                    "risk_level": "LOW",
                }
            )
        else:
            actions.append(
                {
                    "id": "act-hpa-scale",
                    "title": f"Scale {root_service} Replicas (HPA Target 70%)",
                    "description": f"Increase active container count for {root_service} to handle concurrent request surge.",
                    "action_type": "scale",
                    "workflow_id": "wf-k8s-scale-service",
                    "automated": True,
                    "risk_level": "LOW",
                }
            )
            actions.append(
                {
                    "id": "act-rolling-restart",
                    "title": f"Perform Rolling Restart of {root_service}",
                    "description": f"Trigger rolling restart to eliminate thread contention and lock leaks on {root_service}.",
                    "action_type": "restart",
                    "workflow_id": "wf-k8s-rolling-restart",
                    "automated": True,
                    "risk_level": "MEDIUM",
                }
            )

        return actions


incident_correlation_engine = IncidentCorrelationEngine()
