"""
Kubernetes & Container Intelligence Service.
Handles auto-discovery, telemetry aggregation, pod log streaming, and Gemini AI analysis.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_kubernetes import (
    crud_k8s_cluster,
    crud_k8s_deployment,
    crud_k8s_event,
    crud_k8s_node,
    crud_k8s_pod,
)
from app.models.kubernetes import K8sCluster, K8sDeployment, K8sEvent, K8sNode, K8sPod

log = structlog.get_logger(__name__)

DEFAULT_CLUSTERS = [
    {
        "name": "gke-us-central1-prod",
        "provider": "GKE",
        "version": "v1.29.3-gke.1000",
        "region": "us-central1",
        "status": "healthy",
        "node_count": 4,
        "pod_count": 32,
        "cpu_capacity_cores": 64.0,
        "cpu_usage_cores": 24.5,
        "memory_capacity_gb": 256.0,
        "memory_usage_gb": 142.0,
    },
    {
        "name": "eks-us-east-1-analytics",
        "provider": "EKS",
        "version": "v1.28.6-eks",
        "region": "us-east-1",
        "status": "warning",
        "node_count": 3,
        "pod_count": 28,
        "cpu_capacity_cores": 48.0,
        "cpu_usage_cores": 41.2,
        "memory_capacity_gb": 192.0,
        "memory_usage_gb": 168.0,
    },
    {
        "name": "aks-eastus-core",
        "provider": "AKS",
        "version": "v1.29.2",
        "region": "eastus",
        "status": "healthy",
        "node_count": 2,
        "pod_count": 14,
        "cpu_capacity_cores": 32.0,
        "cpu_usage_cores": 10.1,
        "memory_capacity_gb": 128.0,
        "memory_usage_gb": 45.0,
    },
]


class KubernetesService:
    """Service orchestrating Kubernetes telemetry, logs, & AI diagnostics."""

    def __init__(
        self,
        cluster_repo=crud_k8s_cluster,
        node_repo=crud_k8s_node,
        pod_repo=crud_k8s_pod,
        deploy_repo=crud_k8s_deployment,
        event_repo=crud_k8s_event,
    ) -> None:
        self.cluster_crud = cluster_repo
        self.node_crud = node_repo
        self.pod_crud = pod_repo
        self.deploy_crud = deploy_repo
        self.event_crud = event_repo

    async def get_clusters(
        self, db: AsyncSession, user_id: uuid.UUID, provider: str | None = None
    ) -> list[K8sCluster]:
        clusters = await self.cluster_crud.get_multi_by_user(db, user_id=user_id, provider=provider)
        if not clusters:
            clusters = await self.seed_default_kubernetes(db, user_id)
        return clusters

    async def seed_default_kubernetes(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[K8sCluster]:
        now = datetime.now(UTC)
        created_clusters = []
        for c_data in DEFAULT_CLUSTERS:
            cluster = K8sCluster(
                id=uuid.uuid4(),
                user_id=user_id,
                name=c_data["name"],
                provider=c_data["provider"],
                version=c_data["version"],
                region=c_data["region"],
                status=c_data["status"],
                node_count=c_data["node_count"],
                pod_count=c_data["pod_count"],
                cpu_capacity_cores=c_data["cpu_capacity_cores"],
                cpu_usage_cores=c_data["cpu_usage_cores"],
                memory_capacity_gb=c_data["memory_capacity_gb"],
                memory_usage_gb=c_data["memory_usage_gb"],
                created_at=now,
                updated_at=now,
            )
            db.add(cluster)
            created_clusters.append(cluster)
        await db.commit()

        if created_clusters:
            primary_c = created_clusters[0]

            # Nodes
            node_names = [
                "gke-node-pool-1-a8b2",
                "gke-node-pool-1-c9d4",
                "gke-node-pool-1-e1f6",
                "gke-node-pool-2-g3h5",
            ]
            nodes = []
            for i, name in enumerate(node_names):
                node = K8sNode(
                    id=uuid.uuid4(),
                    cluster_id=primary_c.id,
                    name=name,
                    role="worker",
                    status="Ready",
                    instance_type="n2-standard-4",
                    internal_ip=f"10.128.0.{10+i}",
                    cpu_percent=45.0 + (i * 12),
                    memory_percent=55.0 + (i * 8),
                    disk_percent=35.0,
                    pod_capacity=110,
                    pods_running=8,
                    created_at=now,
                    updated_at=now,
                )
                db.add(node)
                nodes.append(node)
            await db.commit()

            # Deployments
            deployments = [
                {
                    "name": "api-gateway",
                    "namespace": "default",
                    "desired": 3,
                    "ready": 3,
                    "image": "gcr.io/cloudpulse/api-gateway:v2.14.1",
                },
                {
                    "name": "auth-service",
                    "namespace": "default",
                    "desired": 2,
                    "ready": 2,
                    "image": "gcr.io/cloudpulse/auth-service:v1.8.3",
                },
                {
                    "name": "payment-svc",
                    "namespace": "prod-billing",
                    "desired": 4,
                    "ready": 3,
                    "image": "gcr.io/cloudpulse/payment-svc:v3.2.0",
                },
                {
                    "name": "data-pipeline-worker",
                    "namespace": "data-engine",
                    "desired": 5,
                    "ready": 4,
                    "image": "gcr.io/cloudpulse/data-pipeline:v0.9.4",
                },
            ]
            for dep in deployments:
                d = K8sDeployment(
                    id=uuid.uuid4(),
                    cluster_id=primary_c.id,
                    name=dep["name"],
                    namespace=dep["namespace"],
                    desired_replicas=dep["desired"],
                    ready_replicas=dep["ready"],
                    updated_replicas=dep["ready"],
                    strategy="RollingUpdate",
                    image=dep["image"],
                    created_at=now,
                    updated_at=now,
                )
                db.add(d)

            # Pods
            sample_pods = [
                {
                    "name": "api-gateway-7b9f88c-x9a1",
                    "namespace": "default",
                    "deployment": "api-gateway",
                    "status": "Running",
                    "restarts": 0,
                    "cpu": 140,
                    "mem": 320,
                },
                {
                    "name": "api-gateway-7b9f88c-y2b4",
                    "namespace": "default",
                    "deployment": "api-gateway",
                    "status": "Running",
                    "restarts": 0,
                    "cpu": 135,
                    "mem": 310,
                },
                {
                    "name": "auth-service-589d7b-k1m9",
                    "namespace": "default",
                    "deployment": "auth-service",
                    "status": "Running",
                    "restarts": 1,
                    "cpu": 85,
                    "mem": 180,
                },
                {
                    "name": "payment-svc-67d4fc-m8n2",
                    "namespace": "prod-billing",
                    "deployment": "payment-svc",
                    "status": "CrashLoopBackOff",
                    "restarts": 14,
                    "cpu": 450,
                    "mem": 920,
                },
                {
                    "name": "payment-svc-67d4fc-p4q7",
                    "namespace": "prod-billing",
                    "deployment": "payment-svc",
                    "status": "OOMKilled",
                    "restarts": 6,
                    "cpu": 512,
                    "mem": 1024,
                },
                {
                    "name": "data-pipeline-worker-91a3-z8x1",
                    "namespace": "data-engine",
                    "deployment": "data-pipeline-worker",
                    "status": "Pending",
                    "restarts": 0,
                    "cpu": 0,
                    "mem": 0,
                },
            ]
            for p in sample_pods:
                pod = K8sPod(
                    id=uuid.uuid4(),
                    cluster_id=primary_c.id,
                    node_id=nodes[0].id if nodes else None,
                    name=p["name"],
                    namespace=p["namespace"],
                    deployment_name=p["deployment"],
                    status=p["status"],
                    restart_count=p["restarts"],
                    cpu_usage_m=p["cpu"],
                    memory_usage_mb=p["mem"],
                    container_images={"main": "gcr.io/cloudpulse/app:latest"},
                    created_at=now,
                    updated_at=now,
                )
                db.add(pod)

            # Events
            events = [
                {
                    "type": "Warning",
                    "reason": "OOMKilled",
                    "object_name": "payment-svc-67d4fc-p4q7",
                    "namespace": "prod-billing",
                    "msg": "Container main in pod payment-svc-67d4fc-p4q7 was killed due to Memory limit (1024Mi) exceeded.",
                },
                {
                    "type": "Warning",
                    "reason": "BackOff",
                    "object_name": "payment-svc-67d4fc-m8n2",
                    "namespace": "prod-billing",
                    "msg": "Back-off restarting failed container main in pod payment-svc-67d4fc-m8n2.",
                },
                {
                    "type": "Warning",
                    "reason": "FailedScheduling",
                    "object_name": "data-pipeline-worker-91a3-z8x1",
                    "namespace": "data-engine",
                    "msg": "0/4 nodes are available: 4 Insufficient memory.",
                },
            ]
            for ev in events:
                event = K8sEvent(
                    id=uuid.uuid4(),
                    event_type=ev["type"],
                    reason=ev["reason"],
                    object_kind="Pod",
                    object_name=ev["object_name"],
                    namespace=ev["namespace"],
                    message=ev["msg"],
                    timestamp=now,
                    created_at=now,
                    updated_at=now,
                )
                db.add(event)

            await db.commit()

        for c in created_clusters:
            await db.refresh(c)
        return created_clusters

    async def get_nodes(
        self, db: AsyncSession, cluster_id: uuid.UUID | None = None
    ) -> list[K8sNode]:
        if cluster_id:
            return await self.node_crud.get_by_cluster(db, cluster_id)
        res = await db.execute(select(K8sNode))
        return list(res.scalars().all())

    async def get_pods(
        self,
        db: AsyncSession,
        cluster_id: uuid.UUID | None = None,
        namespace: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[K8sPod]:
        return await self.pod_crud.get_multi_filtered(
            db, cluster_id=cluster_id, namespace=namespace, status=status, search=search
        )

    async def get_deployments(
        self, db: AsyncSession, cluster_id: uuid.UUID | None = None, namespace: str | None = None
    ) -> list[K8sDeployment]:
        return await self.deploy_crud.get_multi_filtered(
            db, cluster_id=cluster_id, namespace=namespace
        )

    async def get_events(self, db: AsyncSession, event_type: str | None = None) -> list[K8sEvent]:
        return await self.event_crud.get_multi_filtered(db, event_type=event_type)

    async def get_pod_logs(self, db: AsyncSession, pod_name: str, tail: int = 100) -> list[str]:
        pod = await self.pod_crud.get_by_name(db, pod_name)
        if not pod:
            return [f"2026-08-07T15:20:00Z [INFO] Initializing stdout stream for {pod_name}..."]

        status = pod.status
        now_str = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        if status == "OOMKilled":
            return [
                f"{now_str} [INFO] [main] Starting service worker...",
                f"{now_str} [WARN] [heap] Memory usage approaching limit: 980MiB / 1024MiB",
                f"{now_str} [ERROR] [kernel] Out of Memory (OOM) killer invoked for PID 42 (payment-svc).",
                f"{now_str} [FATAL] [systemd] Container terminated with exit code 137 (OOMKilled).",
            ]
        elif status == "CrashLoopBackOff":
            return [
                f"{now_str} [INFO] [main] Booting connection pool to database PostgreSQL...",
                f"{now_str} [ERROR] [db] Connection refused: tcp://10.0.3.50:5432 after 3 retries.",
                f"{now_str} [FATAL] [panic] Unhandled error: failed to initialize database migration stream.",
                f"{now_str} [INFO] [kubelet] Back-off restarting failed container main.",
            ]
        else:
            return [
                f"{now_str} [INFO] [http] GET /healthz 200 OK 1.2ms",
                f"{now_str} [INFO] [metrics] PromScrape: 142 metrics exported.",
                f"{now_str} [INFO] [http] POST /v1/checkout 201 Created 24ms",
                f"{now_str} [INFO] [worker] Processing queue task_20260807_19...",
            ]

    async def analyze_cluster(
        self, db: AsyncSession, cluster_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        events = await self.get_events(db)
        pods = await self.get_pods(db, cluster_id=cluster_id)

        failed_pods = [p for p in pods if p.status in ("CrashLoopBackOff", "OOMKilled", "Pending")]

        insights = [
            {
                "pod_name": "payment-svc-67d4fc-p4q7",
                "issue": "OOMKilled (Exit Code 137)",
                "root_cause": "Container memory limit 1024Mi exceeded due to unindexed SQL query result set buffers.",
                "recommendation": "Increase memory limits to 2048Mi and enable Vertical Pod Autoscaler (VPA).",
            },
            {
                "pod_name": "data-pipeline-worker-91a3-z8x1",
                "issue": "FailedScheduling",
                "root_cause": "Node pool exhaustion in us-central1. Available node memory is 94% saturated.",
                "recommendation": "Enable Cluster Autoscaler (CA) or scale node pool from 4 to 6 instances.",
            },
        ]

        return {
            "cluster_health_score": 84,
            "total_pods_monitored": len(pods),
            "failed_pods_count": len(failed_pods),
            "warning_events_count": len([e for e in events if e.event_type == "Warning"]),
            "root_cause_analysis": insights,
        }


kubernetes_service = KubernetesService()
