import asyncio
from datetime import date
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from schemas.auth import OAuth2Form
from schemas.book import BookBorrow, BookValidate

from application.schemas.token import TokenSchema
from application.schemas.user import User
from domain.models.genre import GenreType
from domain.models.role import RoleType
from infrastructure.database import create_all_tables, drop_all_tables


@pytest.fixture(scope="session")
async def app_init():
    from server import app

    await create_all_tables()

    yield app

    await drop_all_tables()


@pytest.fixture(scope="session")
async def async_client(app_init) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app_init, root_path="/api/v1"), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def user_object() -> User:
    return User(username="user_random", password="secret", role=RoleType.reader)


@pytest.fixture
def book_object() -> BookValidate:
    return BookValidate(
        title="Инноваторы",
        description="Как несколько гениев, хакеров и гиков совершили цифровую революцию",
        date_of_pub=date(2014, 10, 7).strftime("%Y-%m-%d"),
        genres=[GenreType.Biography],
        available_count=10,
    )


@pytest.fixture(scope="session")
async def register_and_login_admin(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_admin", password="secret", role=RoleType.admin)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        content="&".join(map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    return TokenSchema(**response.json())


@pytest.fixture(scope="session")
async def register_and_login_reader(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_reader", password="secret", role=RoleType.reader)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        content="&".join(map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    return TokenSchema(**response.json())


@pytest.fixture(scope="session")
def book_objects() -> list[BookValidate]:
    result = []
    for i in range(1, 11):
        data = BookValidate(
            title=f"Book-{i}",
            description=f"Description-{i}",
            date_of_pub=date(2010, 1, 1).strftime("%Y-%m-%d"),
            genres=[GenreType.Comics],
        )
        result.append(data)
    return result


@pytest.fixture(scope="session")
async def added_books(
    async_client: AsyncClient,
    book_objects: list[BookValidate],
    register_and_login_admin: TokenSchema,
) -> list[BookValidate]:
    headers = {
        "Authorization": f"{register_and_login_admin.token_type} {register_and_login_admin.access_token}"
    }
    cors = []
    for book_data in book_objects:
        cors.append(
            async_client.post("/books", headers=headers, json=book_data.model_dump())
        )
    await asyncio.gather(*cors)
    return book_objects


@pytest.fixture(scope="session")
async def borrowed_book(
    async_client: AsyncClient,
    added_books: list[BookValidate],
    register_and_login_reader: TokenSchema,
) -> BookValidate:
    headers = {
        "Authorization": f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
    }
    data: BookBorrow = BookBorrow(title=added_books[-1].title)
    await async_client.patch("/books/borrow", headers=headers, params=data.model_dump())
    return added_books[-1]
