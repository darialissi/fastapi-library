from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from infrastructure.database import create_all_tables, drop_all_tables

pytest_plugins = (
    "fixtures.user",
    "fixtures.book",
    "fixtures.author",
)


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
