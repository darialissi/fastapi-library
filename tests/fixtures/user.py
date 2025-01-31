import pytest
from httpx import AsyncClient
from schemas.auth import OAuth2Form

from application.schemas.token import TokenSchema
from application.schemas.user import User
from domain.models.role import RoleType


@pytest.fixture
def user_object() -> User:
    return User(username="user_random", password="secret", role=RoleType.reader)


@pytest.fixture(scope="session")
async def register_and_login_admin(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_admin", password="secret", role=RoleType.admin)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        content="&".join(
            map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())
        ),  # Совместимость с OAuth2PasswordRequestForm
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return TokenSchema(**response.json())


@pytest.fixture(scope="session")
def admin_token(register_and_login_admin: TokenSchema) -> str:
    return (
        f"{register_and_login_admin.token_type} {register_and_login_admin.access_token}"
    )


@pytest.fixture(scope="session")
async def register_and_login_reader(async_client: AsyncClient) -> TokenSchema:
    creds = User(username="user_reader", password="secret", role=RoleType.reader)
    await async_client.post("/users", json=creds.model_dump())
    auth = OAuth2Form(username=creds.username, password=creds.password)
    response = await async_client.post(
        "/auth/token",
        content="&".join(
            map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())
        ),  # Совместимость с OAuth2PasswordRequestForm
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return TokenSchema(**response.json())


@pytest.fixture(scope="session")
def reader_token(register_and_login_reader: TokenSchema) -> str:
    return (
        f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
    )
