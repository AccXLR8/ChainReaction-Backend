from fastapi import APIRouter, Depends

from app.database.session import Database
from app.redis.client import RedisClient

router = APIRouter()


@router.get("/health")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    db_ready = Database.is_connected()
    redis_ready = RedisClient.is_connected()
    status = "ok" if db_ready and redis_ready else "degraded"
    return {
        "status": status,
        "database": "ready" if db_ready else "down",
        "redis": "ready" if redis_ready else "down",
    }
