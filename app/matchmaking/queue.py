from __future__ import annotations

import uuid
from typing import Optional

from redis.asyncio import Redis

from app.redis.keys import matchmaking_queue_key


class MatchmakingQueue:
    def __init__(self, redis: Redis, mode: str = "default"):
        self.redis = redis
        self.mode = mode

    async def enqueue(self, user_id: uuid.UUID) -> None:
        await self.redis.lpush(matchmaking_queue_key(self.mode), str(user_id))

    async def dequeue_pair(self) -> Optional[tuple[str, str]]:
        queue = matchmaking_queue_key(self.mode)
        player1 = await self.redis.rpop(queue)
        player2 = await self.redis.rpop(queue)
        if player1 and player2:
            return player1.decode(), player2.decode()
        if player1:
            await self.redis.rpush(queue, player1)
        return None

    async def remove(self, user_id: uuid.UUID) -> None:
        await self.redis.lrem(matchmaking_queue_key(self.mode), 0, str(user_id))
