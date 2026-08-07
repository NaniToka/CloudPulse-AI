"""
Metrics Streaming Service — Generates real-time telemetry updates every 2 seconds
and manages WebSocket stream broadcasting.
"""

import random
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_metric import crud_metric

log = structlog.get_logger(__name__)


def generate_live_telemetry_point() -> dict[str, Any]:
    """Generates realistic live infrastructure metrics with organic noise and subtle trend spikes."""
    now = datetime.now(UTC)

    # Base values with organic fluctuations
    cpu = round(max(15.0, min(99.0, 48.0 + random.uniform(-12.0, 18.0))), 1)
    memory = round(max(20.0, min(98.0, 64.0 + random.uniform(-4.0, 6.0))), 1)
    disk = round(max(30.0, min(95.0, 58.4 + random.uniform(-0.1, 0.2))), 1)
    network = round(max(100.0, 1280.0 + random.uniform(-150.0, 280.0)), 1)
    active_users = int(max(1000, 8420 + random.randint(-250, 480)))
    rps = int(max(100, 1450 + random.randint(-180, 320)))
    error_rate = round(
        max(0.01, min(15.0, 0.22 + (0.8 if cpu > 85.0 else 0.0) + random.uniform(-0.08, 0.15))), 2
    )
    response_time = round(
        max(20.0, 118.0 + (180.0 if cpu > 85.0 else 0.0) + random.uniform(-15.0, 35.0)), 1
    )
    db_active = int(max(10, min(200, 86 + random.randint(-12, 18))))

    pods = [
        {
            "name": "api-gateway-7f9d4b-x92",
            "namespace": "prod",
            "node": "node-us-east-1a",
            "service": "api-gateway",
            "status": "Running" if cpu < 90 else "Rebuilding",
            "cpu_percent": round(cpu * 0.8, 1),
            "memory_mb": 420.0,
            "restarts": 0,
            "uptime": "5d 14h",
        },
        {
            "name": "auth-service-84c1b-p10",
            "namespace": "prod",
            "node": "node-us-west-2b",
            "service": "auth-service",
            "status": "Running",
            "cpu_percent": round(cpu * 0.6, 1),
            "memory_mb": 610.0,
            "restarts": 1,
            "uptime": "12d 02h",
        },
        {
            "name": "payment-service-592f-m88",
            "namespace": "prod",
            "node": "node-us-east-1b",
            "service": "payment-service",
            "status": "Running",
            "cpu_percent": 34.2,
            "memory_mb": 290.0,
            "restarts": 0,
            "uptime": "8d 19h",
        },
        {
            "name": "database-cluster-primary-0",
            "namespace": "data",
            "node": "node-us-east-1c",
            "service": "database-cluster",
            "status": "Running",
            "cpu_percent": round(cpu * 0.9, 1),
            "memory_mb": 3400.0,
            "restarts": 0,
            "uptime": "45d 08h",
        },
        {
            "name": "storage-service-91a-k02",
            "namespace": "storage",
            "node": "node-eu-west-1a",
            "service": "storage-service",
            "status": "Running",
            "cpu_percent": 18.5,
            "memory_mb": 850.0,
            "restarts": 0,
            "uptime": "22d 11h",
        },
    ]

    return {
        "id": str(uuid.uuid4()),
        "cpu_usage": cpu,
        "memory_usage": memory,
        "disk_usage": disk,
        "network_traffic_mbps": network,
        "active_users": active_users,
        "requests_per_second": rps,
        "error_rate": error_rate,
        "response_time_ms": response_time,
        "db_connections_active": db_active,
        "db_connections_max": 200,
        "k8s_pods": pods,
        "timestamp": now.isoformat(),
    }


class MetricsService:
    """Metrics Service managing live stream telemetry."""

    def __init__(self, crud_repo=crud_metric) -> None:
        self.crud = crud_repo

    async def get_current(self, db: AsyncSession) -> dict[str, Any]:
        """Fetch current telemetry metric point."""
        db_point = await self.crud.get_current(db)
        if db_point:
            return {
                "id": str(db_point.id),
                "cpu_usage": db_point.cpu_usage,
                "memory_usage": db_point.memory_usage,
                "disk_usage": db_point.disk_usage,
                "network_traffic_mbps": db_point.network_traffic_mbps,
                "active_users": db_point.active_users,
                "requests_per_second": db_point.requests_per_second,
                "error_rate": db_point.error_rate,
                "response_time_ms": db_point.response_time_ms,
                "db_connections_active": db_point.db_connections_active,
                "db_connections_max": db_point.db_connections_max,
                "k8s_pods": db_point.k8s_pods_json or [],
                "timestamp": db_point.timestamp.isoformat(),
            }
        return generate_live_telemetry_point()

    async def get_history(self, db: AsyncSession, limit: int = 300) -> list[dict[str, Any]]:
        """Fetch sliding window history (up to limit points)."""
        db_points = await self.crud.get_history(db, limit=limit)
        if db_points and len(db_points) > 0:
            res = []
            for p in db_points:
                res.append(
                    {
                        "id": str(p.id),
                        "cpu_usage": p.cpu_usage,
                        "memory_usage": p.memory_usage,
                        "disk_usage": p.disk_usage,
                        "network_traffic_mbps": p.network_traffic_mbps,
                        "active_users": p.active_users,
                        "requests_per_second": p.requests_per_second,
                        "error_rate": p.error_rate,
                        "response_time_ms": p.response_time_ms,
                        "db_connections_active": p.db_connections_active,
                        "db_connections_max": p.db_connections_max,
                        "k8s_pods": p.k8s_pods_json or [],
                        "timestamp": p.timestamp.isoformat(),
                    }
                )
            return res

        # Generate seed sliding window if DB is empty
        items = []
        for _ in range(30, 0, -1):
            pt = generate_live_telemetry_point()
            items.append(pt)
        return items


metrics_service = MetricsService()
