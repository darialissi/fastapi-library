import pytest
from httpx import AsyncClient, Response

from application.schemas.user import User


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
class TestUser:

    async def test_register_user(self, async_client: AsyncClient, user_object: User):
        response: Response = await async_client.post(
            "/users", json=user_object.model_dump()
        )

        assert response.status_code == 201
        user: dict = response.json()

        assert user.get("role") == user_object.role
        assert user.get("username") == user_object.username
        assert user.get("password") is None
        assert user.get("hashed_password") is None
