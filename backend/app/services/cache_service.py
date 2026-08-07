"""
Redis Cache & Token Blocklist Service.
"""

import json
from typing import Any

import redis.asyncio as redis
import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)


class CacheService:
    """Redis Cache Service with JSON serialization and token revocation support."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client: redis.Redis | None = None

    def _get_client(self) -> redis.Redis | None:
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            except Exception as exc:
                log.warning("redis_connection_failed", error=str(exc))
                return None
        return self._redis_client

    async def get(self, key: str) -> Any | None:
        client = self._get_client()
        if not client:
            return None
        try:
            val = await client.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as exc:
            log.warning("cache_get_failed", key=key, error=str(exc))
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> bool:
        client = self._get_client()
        if not client:
            return False
        try:
            serialized = json.dumps(value, default=str)
            await client.set(key, serialized, ex=ttl_seconds)
            return True
        except Exception as exc:
            log.warning("cache_set_failed", key=key, error=str(exc))
            return False

    async def delete(self, key: str) -> bool:
        client = self._get_client()
        if not client:
            return False
        try:
            await client.delete(key)
            return True
        except Exception as exc:
            log.warning("cache_delete_failed", key=key, error=str(exc))
            return False

    async def blocklist_token(self, token: str, ttl_seconds: int = 1800) -> bool:
        """Revoke a JWT token by adding its key to Redis blocklist."""
        return await self.set(f"blocklist:{token}", "revoked", ttl_seconds=ttl_seconds)

    async def is_token_blocklisted(self, token: str) -> bool:
        """Check if a JWT token has been revoked."""
        res = await self.get(f"blocklist:{token}")
        return res is not None


cache_service = CacheService()
