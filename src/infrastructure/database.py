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
    create_all=True,
)

alchemy = AdvancedAlchemy(config=sqlalchemy_config)


async def drop_all_tables() -> None:
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(sqlalchemy_config.metadata.drop_all)


redis_client = aioredis.from_url(settings.REDIS_URL)
