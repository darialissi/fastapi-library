import logging

from fastapi import Depends
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from application.services.author import AuthorService
from application.services.book import BookService
from application.services.token import TokenService
from application.services.user import UserService
from domain.repositories.author import AuthorRepo
from domain.repositories.book import BookRepo
from domain.repositories.token import TokenRepo
from domain.repositories.user import UserRepo
from infrastructure.database import get_async_session, get_redis_client


# Logging
async def get_logger():
    return logging.getLogger(__name__)


# Redis client
RedisClient = Annotated[aioredis.Redis, Depends(get_redis_client)]


# DB Session
DatabaseSession = Annotated[AsyncSession, Depends(get_async_session)]


# Services
async def provide_users_service(db_session: DatabaseSession):
    return UserService(UserRepo(session=db_session))


async def provide_books_service(db_session: DatabaseSession):
    return BookService(BookRepo(session=db_session))


async def provide_authors_service(db_session: DatabaseSession):
    return AuthorService(AuthorRepo(session=db_session))


async def provide_token_service(rd_client: RedisClient):
    return TokenService(TokenRepo(redis_client=rd_client))
