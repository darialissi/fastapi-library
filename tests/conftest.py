from typing import AsyncGenerator

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from httpx import ASGITransport, AsyncClient
from schemas.auth import OAuth2Form

from application.schemas.token import TokenSchema
from application.schemas.user import User
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


@pytest.fixture(scope="class")
async def register_and_login_admin(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_admin", password="secret", role=RoleType.admin)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        json=auth.model_dump(),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    print(response.json())
    return TokenSchema(**response.json())


@pytest.fixture(scope="class")
async def register_and_login_reader(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_reader", password="secret", role=RoleType.reader)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        json=auth.model_dump(),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    return TokenSchema(**response.json())
