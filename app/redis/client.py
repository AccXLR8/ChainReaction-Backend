from __future__ import annotations

from redis.asyncio import Redis


class RedisClient:
    _client: Redis | None = None

    @classmethod
    async def connect(cls, url: str) -> None:
        if cls._client is not None:
            return
        cls._client = Redis.from_url(url)
        await cls._client.ping()

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client is not None:
            await cls._client.close()
            cls._client = None

    @classmethod
    def instance(cls) -> Redis:
        if cls._client is None:
            raise RuntimeError("Redis not initialized")
        return cls._client

    @classmethod
    def is_connected(cls) -> bool:
        return cls._client is not None
