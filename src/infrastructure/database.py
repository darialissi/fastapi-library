from advanced_alchemy.extensions.fastapi import (
    AdvancedAlchemy,
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
)
from redis import asyncio as aioredis

from config import settings

engine_config = EngineConfig()
session_config = AsyncSessionConfig(expire_on_commit=False)

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DATABASE_URL_asyncpg,
    engine_config=engine_config,
    session_config=session_config,
)


async def create_all_tables() -> None:
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(sqlalchemy_config.metadata.create_all)


async def drop_all_tables() -> None:
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(sqlalchemy_config.metadata.drop_all)


alchemy = AdvancedAlchemy(config=sqlalchemy_config)
get_async_session = alchemy.provide_async_session()


redis_client = aioredis.from_url(settings.REDIS_URL)


def get_redis_client():
    return redis_client
