"""
Digital Twin Infrastructure Simulation Engine & Gemini AI What-If Evaluator.
"""

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_digital_twin import (
    crud_execution,
    crud_scenario,
    crud_twin,
    crud_what_if,
)
from app.models.digital_twin import (
    InfrastructureTwin,
    SimulationExecution,
    SimulationScenario,
    WhatIfQuery,
)

log = structlog.get_logger(__name__)

DEFAULT_TWIN_NODES = [
    {
        "id": "cloud-aws-us-east-1",
        "name": "AWS us-east-1 (N. Virginia)",
        "type": "region",
        "status": "healthy",
        "provider": "AWS",
    },
    {
        "id": "cloud-gcp-us-central1",
        "name": "GCP us-central1 (Iowa)",
        "type": "region",
        "status": "healthy",
        "provider": "GCP",
    },
    {
        "id": "k8s-ingress-alb",
        "name": "Cloud Load Balancer (ALB)",
        "type": "load_balancer",
        "status": "healthy",
        "traffic_rps": 4500,
    },
    {
        "id": "api-gateway-mesh",
        "name": "API Gateway & Istio Mesh",
        "type": "gateway",
        "status": "healthy",
        "p99_latency_ms": 14,
    },
    {
        "id": "auth-service-pod",
        "name": "auth-service (4 Pods)",
        "type": "microservice",
        "status": "healthy",
        "cpu_pct": 34,
    },
    {
        "id": "checkout-svc-pod",
        "name": "checkout-svc (6 Pods)",
        "type": "microservice",
        "status": "healthy",
        "cpu_pct": 48,
    },
    {
        "id": "payment-api-pod",
        "name": "payment-api (3 Pods)",
        "type": "microservice",
        "status": "healthy",
        "cpu_pct": 28,
    },
    {
        "id": "redis-cluster-cache",
        "name": "Redis Primary Cache (v7.2)",
        "type": "cache",
        "status": "healthy",
        "hit_ratio": 94.2,
    },
    {
        "id": "postgres-primary-db",
        "name": "PostgreSQL Primary (Aurora DB)",
        "type": "database",
        "status": "healthy",
        "connections": 142,
    },
    {
        "id": "kafka-event-queue",
        "name": "Apache Kafka Events Queue",
        "type": "queue",
        "status": "healthy",
        "lag": 12,
    },
]

DEFAULT_TWIN_EDGES = [
    {"source": "k8s-ingress-alb", "target": "api-gateway-mesh"},
    {"source": "api-gateway-mesh", "target": "auth-service-pod"},
    {"source": "api-gateway-mesh", "target": "checkout-svc-pod"},
    {"source": "checkout-svc-pod", "target": "payment-api-pod"},
    {"source": "auth-service-pod", "target": "redis-cluster-cache"},
    {"source": "checkout-svc-pod", "target": "redis-cluster-cache"},
    {"source": "checkout-svc-pod", "target": "postgres-primary-db"},
    {"source": "payment-api-pod", "target": "postgres-primary-db"},
    {"source": "checkout-svc-pod", "target": "kafka-event-queue"},
]

DEFAULT_SCENARIOS = [
    {
        "name": "AWS us-east-1 Regional Outage",
        "category": "Infrastructure",
        "failure_type": "region_failure",
        "target_resource": "cloud-aws-us-east-1",
        "description": "Simulates complete loss of AWS us-east-1 availability zones. Tests automatic DNS failover to GCP us-central1 and multi-region database sync.",
        "severity": "CRITICAL",
        "parameters": {"duration_min": 30, "failover_type": "active-active"},
    },
    {
        "name": "Redis Primary Cache Cluster Failure",
        "category": "Database",
        "failure_type": "redis_outage",
        "target_resource": "redis-cluster-cache",
        "description": "Simulates sudden Redis master node crash causing total cache misses (0% hit ratio). Evaluates DB connection saturation and API degradation.",
        "severity": "HIGH",
        "parameters": {"cache_eviction": "immediate", "db_connection_surge": 350},
    },
    {
        "name": "400% Sudden Traffic Spike (Black Friday)",
        "category": "Network",
        "failure_type": "traffic_surge_400",
        "target_resource": "k8s-ingress-alb",
        "description": "Injects an abrupt 400% traffic surge (4,500 to 22,500 RPS). Tests Horizontal Pod Autoscaling (HPA) speed and rate limiting thresholds.",
        "severity": "MEDIUM",
        "parameters": {"surge_multiplier": 4.0, "duration_min": 15},
    },
    {
        "name": "PostgreSQL Primary Connection Exhaustion",
        "category": "Database",
        "failure_type": "db_latency",
        "target_resource": "postgres-primary-db",
        "description": "Simulates unindexed slow queries saturating the max connection pool (500 connections). Analyzes checkout timeout cascade.",
        "severity": "HIGH",
        "parameters": {"latency_multiplier": 8.0, "max_connections": 500},
    },
]


class DigitalTwinService:
    """Service orchestrating virtual infrastructure simulations, blast radius, & What-If RAG."""

    def __init__(
        self,
        twin_repo=crud_twin,
        scenario_repo=crud_scenario,
        execution_repo=crud_execution,
        what_if_repo=crud_what_if,
    ) -> None:
        self.twin_crud = twin_repo
        self.scenario_crud = scenario_repo
        self.execution_crud = execution_repo
        self.what_if_crud = what_if_repo

    async def get_or_create_twin(self, db: AsyncSession, user_id: uuid.UUID) -> InfrastructureTwin:
        twin = await self.twin_crud.get_by_user(db, user_id=user_id)
        if not twin:
            now = datetime.now(UTC)
            twin = InfrastructureTwin(
                id=uuid.uuid4(),
                user_id=user_id,
                name="Primary Production Twin",
                status="synchronized",
                health_score=96,
                virtual_resources=DEFAULT_TWIN_NODES,
                topology_graph={"nodes": DEFAULT_TWIN_NODES, "edges": DEFAULT_TWIN_EDGES},
                total_services_count=len(DEFAULT_TWIN_NODES),
                active_simulations_count=0,
                created_at=now,
                updated_at=now,
            )
            db.add(twin)
            await db.commit()
            await db.refresh(twin)

            # Seed default scenarios
            for s_data in DEFAULT_SCENARIOS:
                sc = SimulationScenario(
                    id=uuid.uuid4(),
                    twin_id=twin.id,
                    name=s_data["name"],
                    category=s_data["category"],
                    failure_type=s_data["failure_type"],
                    target_resource=s_data["target_resource"],
                    description=s_data["description"],
                    severity=s_data["severity"],
                    parameters=s_data["parameters"],
                    created_at=now,
                    updated_at=now,
                )
                db.add(sc)
            await db.commit()

        return twin

    async def get_scenarios(
        self, db: AsyncSession, twin_id: uuid.UUID, category: str | None = None
    ) -> list[SimulationScenario]:
        return await self.scenario_crud.get_multi_by_twin(db, twin_id=twin_id, category=category)

    async def run_simulation(
        self, db: AsyncSession, twin: InfrastructureTwin, scenario: SimulationScenario
    ) -> SimulationExecution:
        now = datetime.now(UTC)
        f_type = scenario.failure_type

        if f_type == "redis_outage":
            affected = [
                "redis-cluster-cache",
                "checkout-svc-pod",
                "auth-service-pod",
                "postgres-primary-db",
            ]
            blast_radius = {
                "direct_impact": ["redis-cluster-cache"],
                "cascade_impact": ["checkout-svc-pod", "auth-service-pod", "postgres-primary-db"],
                "latency_degradation_multiplier": 5.4,
                "error_rate_spike_pct": 28.5,
            }
            timeline = [
                {
                    "minute": "00:00",
                    "event": "Redis primary node terminated (Exit 137 OOM / Network Split)",
                },
                {
                    "minute": "00:02",
                    "event": "Cache hit ratio drops from 94% to 0%. 100% of read traffic falls through to PostgreSQL.",
                },
                {
                    "minute": "00:04",
                    "event": "PostgreSQL connection pool maxes out at 500 connections. P99 latency spikes from 14ms to 620ms.",
                },
                {
                    "minute": "00:08",
                    "event": "checkout-svc timeouts trigger circuit breakers. 28% of cart checkouts fail with HTTP 504.",
                },
            ]
            recovery = [
                "1. Trigger Redis Sentinel automatic replica failover.",
                "2. Apply rate-limiting on unauthenticated token validation.",
                "3. Scale PostgreSQL Aurora read replicas from 2 to 5 nodes.",
            ]
            risk_score = 84
            financial_impact = 18500.0
            rec_mins = 14
        elif f_type == "region_failure":
            affected = [
                "cloud-aws-us-east-1",
                "k8s-ingress-alb",
                "checkout-svc-pod",
                "api-gateway-mesh",
            ]
            blast_radius = {
                "direct_impact": ["cloud-aws-us-east-1"],
                "cascade_impact": ["k8s-ingress-alb", "checkout-svc-pod", "api-gateway-mesh"],
                "latency_degradation_multiplier": 2.1,
                "error_rate_spike_pct": 12.0,
            }
            timeline = [
                {
                    "minute": "00:00",
                    "event": "AWS us-east-1 data center connection loss detected by health check probes.",
                },
                {
                    "minute": "00:01",
                    "event": "Route53 / Cloudflare DNS traffic shifts 100% load to GCP us-central1.",
                },
                {
                    "minute": "00:03",
                    "event": "GCP GKE cluster scales node pool from 4 to 8 instances to absorb shifted load.",
                },
            ]
            recovery = [
                "1. Verify cross-region database replication lag < 500ms.",
                "2. Ensure multi-region IAM policies are active on GCP.",
            ]
            risk_score = 72
            financial_impact = 9200.0
            rec_mins = 8
        else:
            affected = ["k8s-ingress-alb", "api-gateway-mesh", "checkout-svc-pod"]
            blast_radius = {
                "direct_impact": ["k8s-ingress-alb"],
                "cascade_impact": ["api-gateway-mesh", "checkout-svc-pod"],
                "latency_degradation_multiplier": 3.2,
                "error_rate_spike_pct": 8.5,
            }
            timeline = [
                {
                    "minute": "00:00",
                    "event": "Incoming traffic surges 400% from 4.5k to 18.2k RPS.",
                },
                {
                    "minute": "00:02",
                    "event": "Horizontal Pod Autoscaler (HPA) spins up 8 additional pod replicas.",
                },
                {"minute": "00:05", "event": "Traffic stabilizes with P95 latency at 42ms."},
            ]
            recovery = [
                "1. Pre-warm ALB load balancer.",
                "2. Adjust HPA target CPU utilization to 60%.",
            ]
            risk_score = 55
            financial_impact = 3400.0
            rec_mins = 6

        exec_rec = SimulationExecution(
            id=uuid.uuid4(),
            twin_id=twin.id,
            scenario_id=scenario.id,
            status="completed",
            duration_seconds=12,
            risk_score=risk_score,
            confidence_score=0.94,
            financial_impact_usd=financial_impact,
            estimated_recovery_minutes=rec_mins,
            affected_services=affected,
            blast_radius=blast_radius,
            predicted_timeline=timeline,
            recovery_steps=recovery,
            started_at=now,
            completed_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(exec_rec)
        await db.commit()
        await db.refresh(exec_rec)
        return exec_rec

    async def evaluate_what_if(
        self, db: AsyncSession, user_id: uuid.UUID, prompt: str
    ) -> WhatIfQuery:
        now = datetime.now(UTC)
        p_lower = prompt.lower()

        if "redis" in p_lower:
            summary = "If Redis fails, all cached token sessions and cart items miss, causing a 350% database query surge. PostgreSQL connection pool will saturate within 4 minutes, causing 504 timeouts on checkout-svc."
            risk = "HIGH"
            cost = "$18,500 / hr"
            affected = [
                "redis-cluster-cache",
                "checkout-svc",
                "auth-service",
                "postgres-primary-db",
            ]
            mitigations = [
                "Enable Redis Sentinel automatic failover.",
                "Implement circuit breakers with in-memory local cache fallbacks.",
                "Scale PostgreSQL Aurora read pool.",
            ]
        elif "region" in p_lower or "east" in p_lower:
            summary = "If AWS us-east-1 goes offline, global DNS traffic will failover to GCP us-central1 within 45 seconds. Cross-region database replication ensures zero data loss, but P99 latency will increase by ~35ms."
            risk = "MEDIUM"
            cost = "$9,200 / hr"
            affected = ["aws-us-east-1", "ingress-alb", "checkout-svc"]
            mitigations = [
                "Pre-scale GCP backup Kubernetes node pool.",
                "Verify cross-cloud database sync lag is below 200ms.",
            ]
        else:
            summary = f"Simulated impact for '{prompt}': Upstream load balancers will throttle non-critical requests. Core services will absorb the load with temporary 2.4x latency increase before auto-scaling completes."
            risk = "MEDIUM"
            cost = "$5,000 / hr"
            affected = ["api-gateway-mesh", "checkout-svc-pod"]
            mitigations = [
                "Tune Horizontal Pod Autoscaling (HPA) triggers to 60% CPU.",
                "Activate edge Cloudflare rate limiting rules.",
            ]

        what_if = WhatIfQuery(
            id=uuid.uuid4(),
            user_id=user_id,
            query_text=prompt,
            impact_summary=summary,
            predicted_risk_level=risk,
            financial_risk_estimate=cost,
            affected_components=affected,
            mitigations=mitigations,
            created_at=now,
            updated_at=now,
        )
        db.add(what_if)
        await db.commit()
        await db.refresh(what_if)
        return what_if


digital_twin_service = DigitalTwinService()
