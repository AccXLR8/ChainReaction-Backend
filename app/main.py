from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.api.router import api_router
from app.redis.client import RedisClient
from app.database.session import Database
from app.database.migrations_runner import run_migrations_once


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("starting application", extra={"env": settings.app_env})
    await Database.connect(settings.database_url)
    run_migrations_once()
    await RedisClient.connect(settings.redis_url)
    try:
        yield
    finally:
        await RedisClient.disconnect()
        await Database.disconnect()
        logger.info("application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Chain Reaction Backend",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://chain-reaction-frontend-qx3wq7pkq-samyak-sharmas-projects.vercel.app",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    from app.websocket import routes as ws_routes

    app.include_router(ws_routes.router)

    return app


app = create_app()