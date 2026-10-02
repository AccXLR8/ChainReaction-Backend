from __future__ import annotations

import uuid

from app.redis.client import RedisClient
from app.matchmaking.queue import MatchmakingQueue


class MatchmakingService:
    def __init__(self):
        self.redis = RedisClient.instance

    async def join_queue(self, user_id: uuid.UUID) -> None:
        queue = MatchmakingQueue(self.redis())
        await queue.enqueue(user_id)

    async def leave_queue(self, user_id: uuid.UUID) -> None:
        queue = MatchmakingQueue(self.redis())
        await queue.remove(user_id)

    async def poll_pair(self) -> tuple[str, str] | None:
        queue = MatchmakingQueue(self.redis())
        return await queue.dequeue_pair()


matchmaking_service = MatchmakingService()
