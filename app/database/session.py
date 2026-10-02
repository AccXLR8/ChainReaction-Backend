from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


class Database:
    _engine = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    async def connect(cls, database_url: str) -> None:
        if cls._engine is not None:
            return
        cls._engine = create_async_engine(database_url, echo=False, future=True)
        cls._session_factory = async_sessionmaker(cls._engine, expire_on_commit=False)

    @classmethod
    async def disconnect(cls) -> None:
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None

    @classmethod
    def is_connected(cls) -> bool:
        return cls._engine is not None

    @classmethod
    def session_factory(cls) -> async_sessionmaker[AsyncSession]:
        if cls._session_factory is None:
            raise RuntimeError("Database has not been initialized")
        return cls._session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = Database.session_factory()
    async with session_factory() as session:
        yield session
