from __future__ import annotations

import json
import logging
from redis.asyncio import Redis

from wonderhow.config import settings
from wonderhow.models.message import ChatMessage

logger = logging.getLogger(__name__)

MAX_RECENT_MESSAGES = 50


class ShortTermMemory:
    """Redis-backed recent conversation context per group."""

    def __init__(self):
        self._redis: Redis | None = None

    async def connect(self):
        if self._redis is None:
            try:
                self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
                await self._redis.ping()
                logger.info("Connected to Redis for short-term memory")
            except Exception:
                logger.warning("Redis unavailable, falling back to in-memory")
                self._redis = None
        self._fallback: dict[str, list[dict]] = {}

    def _key(self, group_id: str) -> str:
        return f"stm:group:{group_id}"

    async def add_message(self, group_id: str, message: ChatMessage):
        data = message.model_dump(mode="json")
        if self._redis:
            try:
                await self._redis.rpush(self._key(group_id), json.dumps(data))
                await self._redis.ltrim(self._key(group_id), -MAX_RECENT_MESSAGES, -1)
                return
            except Exception:
                logger.warning("Redis write failed, using fallback")

        if group_id not in self._fallback:
            self._fallback[group_id] = []
        self._fallback[group_id].append(data)
        self._fallback[group_id] = self._fallback[group_id][-MAX_RECENT_MESSAGES:]

    async def get_recent(self, group_id: str, count: int = 20) -> list[ChatMessage]:
        raw: list[str] = []
        if self._redis:
            try:
                raw = await self._redis.lrange(self._key(group_id), -count, -1)
                return [ChatMessage(**json.loads(r)) for r in raw]
            except Exception:
                pass

        items = self._fallback.get(group_id, [])[-count:]
        return [ChatMessage(**d) for d in items]

    async def clear_group(self, group_id: str):
        if self._redis:
            await self._redis.delete(self._key(group_id))
        self._fallback.pop(group_id, None)
