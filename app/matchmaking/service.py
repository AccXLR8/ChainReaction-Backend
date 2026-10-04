from __future__ import annotations

import uuid

from app.redis.client import RedisClient
from app.redis.keys import matchmaking_assignment_key
from app.matchmaking.queue import MatchmakingQueue


class MatchmakingService:
    def __init__(self):
        self._redis_factory = RedisClient.instance

    def _queue(self) -> MatchmakingQueue:
        return MatchmakingQueue(self._redis_factory())

    async def join_queue(self, user_id: uuid.UUID) -> tuple[str, str] | None:
        queue = self._queue()
        await queue.enqueue(user_id)
        return await queue.try_match()

    async def leave_queue(self, user_id: uuid.UUID) -> None:
        queue = self._queue()
        await queue.remove(user_id)

    async def poll_pair(self) -> tuple[str, str] | None:
        queue = self._queue()
        return await queue.try_match()

    async def save_assignment(self, user_id: uuid.UUID, game_id: uuid.UUID, ttl_seconds: int = 600) -> None:
        client = self._redis_factory()
        await client.set(matchmaking_assignment_key(str(user_id)), str(game_id), ex=ttl_seconds)

    async def pop_assignment(self, user_id: uuid.UUID) -> str | None:
        client = self._redis_factory()
        key = matchmaking_assignment_key(str(user_id))
        value = await client.get(key)
        if value is None:
            return None
        await client.delete(key)
        return value.decode() if isinstance(value, bytes) else value


matchmaking_service = MatchmakingService()
