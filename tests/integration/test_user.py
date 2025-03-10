import pytest
from fastapi import status
from httpx import AsyncClient, Response
from schemas.auth import OAuth2Form

from application.schemas.token import TokenSchema
from application.schemas.user import User, UserUpdate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
class TestUser:

    async def test_register(self, async_client: AsyncClient, user_object: User):
        response: Response = await async_client.post(
            "/users", json=user_object.model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED

        user: dict = response.json()

        assert user.get("id")
        assert user.get("role") == user_object.role
        assert user.get("username") == user_object.username
        assert user.get("password") is None
        assert user.get("hashed_password") is None

        response: Response = await async_client.post(
            "/users", json=user_object.model_dump()
        )

        assert (
            response.status_code == status.HTTP_409_CONFLICT
        ), "Username зарегистрирован за другим пользователем"

    async def test_auth(self, async_client: AsyncClient, user_object: User):
        response: Response = await async_client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        auth = OAuth2Form(username=user_object.username, password=user_object.password)
        response: Response = await async_client.post(
            "/auth/token",
            content="&".join(
                map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())
            ),  # Совместимость с OAuth2PasswordRequestForm
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_200_OK
        token: dict = response.json()

        assert token.get("token_type")
        assert token.get("access_token")

        headers = {
            "Authorization": f"{token.get('token_type')} {token.get('access_token')}"
        }

        response: Response = await async_client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        user: dict = response.json()

        assert user.get("id")
        assert user.get("role")

    async def test_update(
        self, async_client: AsyncClient, user_object: User, register_and_login_reader
    ):

        auth = OAuth2Form(username=user_object.username, password=user_object.password)
        response: Response = await async_client.post(
            "/auth/token",
            content="&".join(
                map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())
            ),  # Совместимость с OAuth2PasswordRequestForm
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token: TokenSchema = TokenSchema(**response.json())
        headers = {"Authorization": f"{token.token_type} {token.access_token}"}

        existed: UserUpdate = UserUpdate(
            username="user_reader", password=user_object.password
        )
        response: Response = await async_client.patch(
            "/users/me", headers=headers, json=existed.model_dump()
        )

        assert (
            response.status_code == status.HTTP_409_CONFLICT
        ), "Пользователь с существующим username"

        valid: UserUpdate = UserUpdate(
            username="user_new_name", password=user_object.password
        )
        response: Response = await async_client.patch(
            "/users/me", headers=headers, json=valid.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK

        user: dict = response.json()

        assert user.get("username") == valid.username

    async def test_delete(self, async_client: AsyncClient, user_object: User):
        await async_client.post("/users", json=user_object.model_dump())

        auth = OAuth2Form(username=user_object.username, password=user_object.password)
        response: Response = await async_client.post(
            "/auth/token",
            content="&".join(
                map(lambda i: f"{i[0]}={i[1]}", auth.model_dump().items())
            ),  # Совместимость с OAuth2PasswordRequestForm
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token: TokenSchema = TokenSchema(**response.json())
        headers = {"Authorization": f"{token.token_type} {token.access_token}"}

        response: Response = await async_client.delete("/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK

        response: Response = await async_client.get("/users/me", headers=headers)

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Удаленный пользователь и отозванный токен"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
@pytest.mark.admin
class TestAdmin:

    async def test_me(
        self,
        async_client: AsyncClient,
        admin_token: str,
    ):
        headers = {"Authorization": admin_token}

        response: Response = await async_client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        user: dict = response.json()

        assert user.get("role") == "admin"

    async def test_get_readers(
        self,
        async_client: AsyncClient,
        admin_token: str,
        reader_token: str,
    ):
        response: Response = await async_client.get("/users/readers")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        headers = {"Authorization": reader_token}

        response: Response = await async_client.get("/users/readers", headers=headers)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Просмотр списка читателей доступен только администратору"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.get("/users/readers", headers=headers)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
@pytest.mark.reader
class TestReader:

    async def test_me(self, async_client: AsyncClient, reader_token: str):
        headers = {"Authorization": reader_token}

        response: Response = await async_client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        user: dict = response.json()

        assert user.get("role") == "reader"
