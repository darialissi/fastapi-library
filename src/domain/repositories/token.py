from datetime import timedelta
from typing import Optional

from redis import asyncio as aioredis


class TokenRepo:

    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def add(
        self,
        key: str,
        value: str,
        expire: timedelta,
    ):
        return await self.redis_client.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[bytes]:
        return await self.redis_client.get(key)

    async def revoke(self, key: str):
        return await self.redis_client.delete(key)
