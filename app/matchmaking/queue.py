from __future__ import annotations

import random
import uuid
from typing import Optional

from redis.asyncio import Redis

from app.redis.keys import matchmaking_queue_key


class MatchmakingQueue:
    def __init__(self, redis: Redis, mode: str = "default"):
        self.redis = redis
        self.mode = mode

    async def enqueue(self, user_id: uuid.UUID) -> None:
        await self.redis.sadd(matchmaking_queue_key(self.mode), str(user_id))

    async def try_match(self) -> Optional[tuple[str, str]]:
        key = matchmaking_queue_key(self.mode)
        members = await self.redis.smembers(key)
        decoded = [member.decode() for member in members]
        if len(decoded) < 2:
            return None
        player1, player2 = random.sample(decoded, 2)
        await self.redis.srem(key, player1, player2)
        return player1, player2

    async def remove(self, user_id: uuid.UUID) -> None:
        await self.redis.srem(matchmaking_queue_key(self.mode), str(user_id))
