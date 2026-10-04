from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config.settings import get_settings


def _sync_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg"):
        return url.replace("+asyncpg", "", 1)
    if url.startswith("postgresql+psycopg"):
        return url.replace("+psycopg", "", 1)
    return url


_MIGRATIONS_RAN = False


def run_migrations_once() -> None:
    global _MIGRATIONS_RAN
    if _MIGRATIONS_RAN:
        return
    settings = get_settings()
    config_path = Path(__file__).resolve().parents[2] / "alembic.ini"
    alembic_cfg = Config(str(config_path))
    alembic_cfg.set_main_option("script_location", "app/database/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", _sync_url(settings.database_url))
    command.upgrade(alembic_cfg, "head")
    _MIGRATIONS_RAN = True
