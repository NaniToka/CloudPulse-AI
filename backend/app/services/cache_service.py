"""
Redis Cache & Token Blocklist Service.
"""

from __future__ import annotations

import json
import time
from typing import Any

import redis.asyncio as redis
import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)


class CacheService:
    """Redis Cache Service with JSON serialization, token revocation support, and local memory fallback."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client: redis.Redis | None = None
        self._memory_cache: dict[str, tuple[str, float]] = {}  # key -> (serialized_val, expire_at)
        self._redis_failed: bool = False

    def _get_client(self) -> redis.Redis | None:
        if self._redis_failed:
            return None
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            except Exception as exc:
                log.warning("redis_connection_failed_falling_back_to_memory", error=str(exc))
                self._redis_failed = True
                return None
        return self._redis_client

    async def get(self, key: str) -> Any | None:
        client = self._get_client()
        if client:
            try:
                val = await client.get(key)
                if val is not None:
                    return json.loads(val)
                return None
            except Exception:
                self._redis_failed = True

        # In-memory fallback
        item = self._memory_cache.get(key)
        if item:
            val, expire_at = item
            if time.time() < expire_at:
                return json.loads(val)
            del self._memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> bool:
        serialized = json.dumps(value, default=str)
        client = self._get_client()
        if client:
            try:
                await client.set(key, serialized, ex=ttl_seconds)
                return True
            except Exception:
                self._redis_failed = True

        # In-memory fallback
        expire_at = time.time() + ttl_seconds
        self._memory_cache[key] = (serialized, expire_at)
        return True

    async def delete(self, key: str) -> bool:
        client = self._get_client()
        if client:
            try:
                await client.delete(key)
            except Exception:
                self._redis_failed = True

        self._memory_cache.pop(key, None)
        return True

    async def blocklist_token(self, token: str, ttl_seconds: int = 1800) -> bool:
        """Revoke a JWT token by adding its key to Redis/Memory blocklist."""
        return await self.set(f"blocklist:{token}", "revoked", ttl_seconds=ttl_seconds)

    async def is_token_blocklisted(self, token: str) -> bool:
        """Check if a JWT token has been revoked."""
        res = await self.get(f"blocklist:{token}")
        return res is not None

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        client = self._get_client()
        if not client:
            return False
        try:
            return bool(await client.ping())
        except Exception:
            return False


cache_service = CacheService()

