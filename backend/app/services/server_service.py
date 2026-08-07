"""
Server & Infrastructure Management Service with auto-seeding.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.crud.crud_server import crud_server
from app.models.infrastructure import Server, ServerMetric, InfraAlert
from app.schemas.infrastructure import ServerCreate, ServerUpdate

log = structlog.get_logger(__name__)

DEFAULT_SERVERS = [
    {
        "name": "web-prod-01",
        "hostname": "web-prod-01.us-east-1.compute.internal",
        "ip_address": "10.0.1.14",
        "server_type": "container",
        "provider": "AWS",
        "region": "us-east-1",
        "environment": "production",
        "status": "healthy",
        "cpu_percent": 72.4,
        "memory_percent": 68.1,
        "disk_percent": 45.0,
        "network_in_mbps": 124.5,
        "network_out_mbps": 88.2,
        "uptime_seconds": 864000,
    },
    {
        "name": "web-prod-02",
        "hostname": "web-prod-02.us-east-1.compute.internal",
        "ip_address": "10.0.1.15",
        "server_type": "container",
        "provider": "AWS",
        "region": "us-east-1",
        "environment": "production",
        "status": "healthy",
        "cpu_percent": 65.2,
        "memory_percent": 71.0,
        "disk_percent": 48.0,
        "network_in_mbps": 115.0,
        "network_out_mbps": 82.0,
        "uptime_seconds": 860000,
    },
    {
        "name": "api-prod-01",
        "hostname": "api-prod-01.us-central1.gke.internal",
        "ip_address": "10.128.0.8",
        "server_type": "vm",
        "provider": "GCP",
        "region": "us-central1",
        "environment": "production",
        "status": "degraded",
        "cpu_percent": 91.8,
        "memory_percent": 88.4,
        "disk_percent": 62.0,
        "network_in_mbps": 340.0,
        "network_out_mbps": 290.0,
        "uptime_seconds": 432000,
    },
    {
        "name": "db-primary",
        "hostname": "db-primary.rds.us-east-1.amazonaws.com",
        "ip_address": "10.0.3.50",
        "server_type": "linux",
        "provider": "AWS",
        "region": "us-east-1",
        "environment": "production",
        "status": "healthy",
        "cpu_percent": 48.0,
        "memory_percent": 75.5,
        "disk_percent": 72.0,
        "network_in_mbps": 410.0,
        "network_out_mbps": 380.0,
        "uptime_seconds": 1296000,
    },
    {
        "name": "cache-01",
        "hostname": "cache-01.redis.us-east-1.internal",
        "ip_address": "10.0.4.12",
        "server_type": "container",
        "provider": "AWS",
        "region": "us-east-1",
        "environment": "production",
        "status": "healthy",
        "cpu_percent": 22.1,
        "memory_percent": 45.2,
        "disk_percent": 18.0,
        "network_in_mbps": 85.0,
        "network_out_mbps": 64.0,
        "uptime_seconds": 1500000,
    },
    {
        "name": "worker-prod-02",
        "hostname": "worker-prod-02.eastus.azure.internal",
        "ip_address": "10.2.0.44",
        "server_type": "vm",
        "provider": "Azure",
        "region": "eastus",
        "environment": "production",
        "status": "offline",
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "disk_percent": 0.0,
        "network_in_mbps": 0.0,
        "network_out_mbps": 0.0,
        "uptime_seconds": 0,
    },
]


class ServerService:
    """Service handling server infrastructure CRUD & health seeding."""

    def __init__(self, crud_repo=crud_server) -> None:
        self.crud = crud_repo

    async def get_servers(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Server]:
        servers = await self.crud.get_multi_by_user(
            db, user_id=user_id, provider=provider, status=status, search=search
        )
        if not servers:
            # Seed default servers for user
            servers = await self.seed_default_servers(db, user_id)
        return servers

    async def seed_default_servers(self, db: AsyncSession, user_id: uuid.UUID) -> List[Server]:
        created = []
        now = datetime.now(timezone.utc)
        for data in DEFAULT_SERVERS:
            server = Server(
                id=uuid.uuid4(),
                user_id=user_id,
                name=data["name"],
                hostname=data["hostname"],
                ip_address=data["ip_address"],
                server_type=data["server_type"],
                provider=data["provider"],
                region=data["region"],
                environment=data["environment"],
                status=data["status"],
                cpu_percent=data["cpu_percent"],
                memory_percent=data["memory_percent"],
                disk_percent=data["disk_percent"],
                network_in_mbps=data["network_in_mbps"],
                network_out_mbps=data["network_out_mbps"],
                uptime_seconds=data["uptime_seconds"],
                created_at=now,
                updated_at=now,
            )
            db.add(server)
            created.append(server)
        await db.commit()
        for s in created:
            await db.refresh(s)
        return created

    async def create_server(self, db: AsyncSession, user_id: uuid.UUID, payload: ServerCreate) -> Server:
        now = datetime.now(timezone.utc)
        server = Server(
            id=uuid.uuid4(),
            user_id=user_id,
            name=payload.name,
            hostname=payload.hostname or f"{payload.name}.internal",
            ip_address=payload.ip_address or "10.0.0.1",
            server_type=payload.server_type,
            provider=payload.provider,
            region=payload.region,
            environment=payload.environment,
            status="healthy",
            cpu_percent=15.0,
            memory_percent=30.0,
            disk_percent=25.0,
            network_in_mbps=50.0,
            network_out_mbps=35.0,
            uptime_seconds=3600,
            created_at=now,
            updated_at=now,
        )
        db.add(server)
        await db.commit()
        await db.refresh(server)
        return server

    async def get_server(self, db: AsyncSession, server_id: uuid.UUID) -> Optional[Server]:
        return await self.crud.get(db, id=server_id)

    async def update_server(self, db: AsyncSession, server_id: uuid.UUID, payload: ServerUpdate) -> Optional[Server]:
        server = await self.get_server(db, server_id)
        if not server:
            return None
        now = datetime.now(timezone.utc)
        if payload.name is not None:
            server.name = payload.name
        if payload.status is not None:
            server.status = payload.status
        if payload.cpu_percent is not None:
            server.cpu_percent = payload.cpu_percent
        if payload.memory_percent is not None:
            server.memory_percent = payload.memory_percent
        if payload.disk_percent is not None:
            server.disk_percent = payload.disk_percent
        server.updated_at = now
        await db.commit()
        await db.refresh(server)
        return server

    async def delete_server(self, db: AsyncSession, server_id: uuid.UUID) -> bool:
        server = await self.get_server(db, server_id)
        if not server:
            return False
        await db.delete(server)
        await db.commit()
        return True


server_service = ServerService()
