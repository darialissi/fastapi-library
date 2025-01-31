import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from schemas.book import BookBorrow, BookValidate

from application.schemas.book import BookUpdate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
class TestBook:

    async def test_add(
        self,
        async_client: AsyncClient,
        book_object: BookValidate,
        admin_token: str,
        reader_token: str,
    ):
        headers_reader = {"Authorization": reader_token}

        response: Response = await async_client.post(
            "/books", headers=headers_reader, json=book_object.model_dump()
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Добавить книгу может только администратор"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.post(
            "/books", headers=headers, json=book_object.model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED
        book: dict = response.json()

        assert book.get("id")
        assert book.get("title") == book_object.title
        assert book.get("description") == book_object.description
        assert book.get("date_of_pub") == book_object.date_of_pub
        assert book.get("genres") == book_object.genres
        assert book.get("available_count") == book_object.available_count

        response: Response = await async_client.post(
            "/books", headers=headers, json=book_object.model_dump()
        )

        assert (
            response.status_code == status.HTTP_409_CONFLICT
        ), "Книга с указанным title уже существует"

        response: Response = await async_client.get("/books")

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Получение списка доступных книг не требует аутентификации"
        books: list = response.json()

        assert book in books, "Книга должна быть в списке доступных"

    async def test_delete(
        self,
        async_client: AsyncClient,
        book_object: BookValidate,
        admin_token: str,
        reader_token: str,
    ):

        response: Response = await async_client.get("/books")
        books: list = response.json()

        filtered = list(filter(lambda d: d.get("title") == book_object.title, books))

        assert filtered, "Книга должна быть добавлена"

        book: dict = filtered[0]

        headers_reader = {"Authorization": reader_token}

        response: Response = await async_client.delete(
            f"/books/{book.get('id')}", headers=headers_reader
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Удалить книгу может только администратор"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.delete(
            f"/books/{book.get('id')}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK

        response: Response = await async_client.get("/books")

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Получение списка доступных книг не требует аутентификации"
        books: list = response.json()

        assert book not in books, "Книга не должна быть в списке доступных после удаления"

    async def test_update(
        self,
        async_client: AsyncClient,
        book_object: BookValidate,
        admin_token: str,
        reader_token: str,
        added_books: list[BookValidate],
    ):

        headers = {"Authorization": admin_token}

        response: Response = await async_client.post(
            "/books", headers=headers, json=book_object.model_dump()
        )

        book: dict = response.json()

        params = BookUpdate(title="New Edition", available_count=15)
        invalid_params = BookUpdate(title=added_books[0].title)

        headers_reader = {"Authorization": reader_token}

        response: Response = await async_client.patch(
            f"/books/{book.get('id')}",
            headers=headers_reader,
            params=params.model_dump(exclude_none=True),
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Обновить книгу может только администратор"

        response: Response = await async_client.patch(
            f"/books/{book.get('id')}",
            headers=headers,
            params=invalid_params.model_dump(exclude_none=True),
        )

        updated: dict = response.json()

        assert (
            response.status_code == status.HTTP_409_CONFLICT
        ), "Книга с указанным title уже существует"

        response: Response = await async_client.patch(
            f"/books/{book.get('id')}",
            headers=headers,
            params=params.model_dump(exclude_none=True),
        )

        updated: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert updated.get("title") == params.title
        assert updated.get("available_count") == params.available_count

    async def test_borrow(
        self,
        async_client: AsyncClient,
        admin_token: str,
        reader_token: str,
        added_books: list[BookValidate],
    ):
        headers_admin = {"Authorization": admin_token}

        data: BookBorrow = BookBorrow(title=added_books[0].title)
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers_admin, params=data.model_dump()
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Книгу может взять только Читатель"

        headers = {"Authorization": reader_token}

        data: BookBorrow = BookBorrow(title=added_books[0].title)
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=data.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK

        book: dict = response.json()

        assert book.get("title") == added_books[0].title
        assert (
            book.get("available_count") == added_books[0].available_count - 1
        ), "Количество доступных экземпляров должно уменьшиться"

        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=data.model_dump()
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Читатель не может иметь больше 1 экземпляра одной книги"

        not_existed: BookBorrow = BookBorrow(title="Unknown")
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=not_existed.model_dump()
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Книги не существует"

    async def test_borrow_limit(
        self,
        async_client: AsyncClient,
        reader_token: str,
        added_books: list[BookValidate],
    ):

        headers = {"Authorization": reader_token}

        cors = []
        for i, book in enumerate(added_books):
            data: BookBorrow = BookBorrow(title=book.title)
            cors.append(
                async_client.patch(
                    "/books/borrow", headers=headers, params=data.model_dump()
                )
            )
            if i == 5:
                break

        responses = await asyncio.gather(*cors)
        limit = list(filter(lambda r: r.status_code != status.HTTP_200_OK, responses))
        assert limit, "Читатель может взять не больше 5 книг"

    async def test_borrow_not_available(
        self,
        async_client: AsyncClient,
        reader_token: str,
        added_not_available_book: BookValidate,
    ):

        headers = {"Authorization": reader_token}

        data: BookBorrow = BookBorrow(title=added_not_available_book.title)
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=data.model_dump()
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Количество доступных экземпляров 0"

    async def test_return(
        self,
        async_client: AsyncClient,
        reader_token: str,
        borrowed_book: BookValidate,
    ):
        headers = {"Authorization": reader_token}

        data: BookBorrow = BookBorrow(title=borrowed_book.title)

        response: Response = await async_client.patch(
            "/books/return", headers=headers, params=data.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK

        book: dict = response.json()

        assert book.get("title") == borrowed_book.title
        assert (
            book.get("available_count") == borrowed_book.available_count
        ), "Количество доступных экземпляров должно увеличиться после возврата"

    async def test_reader_books(
        self,
        async_client: AsyncClient,
        reader_token: str,
        borrowed_book: BookValidate,
    ):

        headers = {"Authorization": reader_token}

        response: Response = await async_client.get("/users/me/books", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        book: dict = response.json()[-1]

        assert book.get("book_id")
        assert book.get("borrow_date")
        assert book.get("return_date")
