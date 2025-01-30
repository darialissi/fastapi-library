import pytest
from fastapi import status
from httpx import AsyncClient, Response
from schemas.book import BookBorrow, BookValidate

from application.schemas.token import TokenSchema
from application.schemas.book import BookUpdate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
class TestBook:

    async def test_book(
        self,
        async_client: AsyncClient,
        book_object: BookValidate,
        register_and_login_admin: TokenSchema,
        register_and_login_reader: TokenSchema,
    ):
        headers_reader = {
            "Authorization": f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
        }
        response: Response = await async_client.post(
            "/books", headers=headers_reader, json=book_object.model_dump()
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Добавить книгу в систему может только администратор"

        headers = {
            "Authorization": f"{register_and_login_admin.token_type} {register_and_login_admin.access_token}"
        }
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

        response: Response = await async_client.get("/books")

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Получение списка доступных книг не требует аутентификации"
        books: list = response.json()

        assert book in books, "Книга должна быть в списке доступных"

        params = BookUpdate(title="Инноваторы. Новое издание.")
        response: Response = await async_client.patch(
            f"/books/{book.get('id')}",
            headers=headers,
            params=params.model_dump(exclude_none=True),
        )
        updated: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert updated.get("title") == params.title

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

    async def test_borrow_book(
        self,
        async_client: AsyncClient,
        register_and_login_admin: TokenSchema,
        register_and_login_reader: TokenSchema,
        added_books: list[BookValidate],
    ):
        headers_admin = {
            "Authorization": f"{register_and_login_admin.token_type} {register_and_login_admin.access_token}"
        }

        data: BookBorrow = BookBorrow(title=added_books[0].title)
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers_admin, params=data.model_dump()
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Книгу может взять только Читатель"

        headers = {
            "Authorization": f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
        }
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

        # SAWarning - commit не происходит, исключение отрабатывается верно
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=data.model_dump()
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Читатель не может иметь больше 1 экземпляра одной книги"

        not_existed: BookBorrow = BookBorrow(title="unknown")
        response: Response = await async_client.patch(
            "/books/borrow", headers=headers, params=not_existed.model_dump()
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), "Книга не существует в системе"

    async def test_return_book(
        self,
        async_client: AsyncClient,
        register_and_login_reader: TokenSchema,
        borrowed_book: BookValidate,
    ):
        headers = {
            "Authorization": f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
        }
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
        register_and_login_reader: TokenSchema,
        borrowed_book: BookValidate,
    ):

        headers = {
            "Authorization": f"{register_and_login_reader.token_type} {register_and_login_reader.access_token}"
        }

        response: Response = await async_client.get("/users/me/books", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        book: dict = response.json()[-1]

        assert book.get("book_id")
        assert book.get("borrow_date")
        assert book.get("return_date")
