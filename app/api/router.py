from fastapi import APIRouter

from app.api import health, games, matchmaking, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(matchmaking.router, prefix="/matchmaking", tags=["matchmaking"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
