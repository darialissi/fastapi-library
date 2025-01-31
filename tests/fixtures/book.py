import asyncio
from datetime import date

import pytest
from httpx import AsyncClient
from schemas.book import BookBorrow, BookID, BookValidate

from domain.models.genre import GenreType


@pytest.fixture
def book_id_object() -> BookID:
    return BookID(id=1)


@pytest.fixture
def book_object() -> BookValidate:
    return BookValidate(
        title="Book-0",
        description=".....",
        date_of_pub=date(2005, 1, 1),
        genres=[GenreType.Biography],
        available_count=10,
    )


@pytest.fixture(scope="session")
def book_objects() -> list[BookValidate]:
    result = []
    for i in range(1, 11):
        data = BookValidate(
            title=f"Book-{i}",
            description=f"Description-{i}",
            date_of_pub=date(2010, 1, 1),
            genres=[GenreType.Comics],
        )
        result.append(data)
    return result


@pytest.fixture(scope="session")
async def added_books(
    async_client: AsyncClient,
    book_objects: list[BookValidate],
    admin_token: str,
) -> list[BookValidate]:
    headers = {"Authorization": admin_token}
    cors = []
    for book_data in book_objects:
        cors.append(
            async_client.post("/books", headers=headers, json=book_data.model_dump())
        )
    await asyncio.gather(*cors)
    return book_objects


@pytest.fixture(scope="session")
async def added_not_available_book(
    async_client: AsyncClient,
    admin_token: str,
) -> BookValidate:
    headers = {"Authorization": admin_token}
    not_available_book: BookValidate = BookValidate(
        title="Not available book",
        description=".....",
        date_of_pub=date(2015, 1, 1),
        genres=[GenreType.NonFiction],
        available_count=0,
    )
    await async_client.post(
        "/books", headers=headers, json=not_available_book.model_dump()
    )
    return not_available_book


@pytest.fixture(scope="session")
async def borrowed_book(
    async_client: AsyncClient,
    added_books: list[BookValidate],
    reader_token: str,
) -> BookValidate:
    headers = {"Authorization": reader_token}
    data: BookBorrow = BookBorrow(title=added_books[-1].title)
    await async_client.patch("/books/borrow", headers=headers, params=data.model_dump())
    return added_books[-1]
