import pytest
from fastapi import status
from httpx import AsyncClient, Response
from schemas.author import AuthorID, AuthorValidate
from schemas.book import BookID, BookValidate

from application.schemas.author import AuthorReturn, AuthorUpdate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
class TestAuthor:

    async def test_add(
        self,
        async_client: AsyncClient,
        author_object: AuthorValidate,
        book_id_object: BookID,
        admin_token: str,
        reader_token: str,
        added_books: list[BookValidate],
    ):

        headers_reader = {"Authorization": reader_token}
        response: Response = await async_client.post(
            f"/books/{book_id_object.id}/authors",
            headers=headers_reader,
            json=author_object.model_dump(),
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Добавить автора может только администратор"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.post(
            f"/books/{book_id_object.id}/authors",
            headers=headers,
            json=author_object.model_dump(),
        )

        assert response.status_code == status.HTTP_201_CREATED
        author: dict = response.json()

        assert author.get("id")
        assert author.get("book_id") == book_id_object.id
        assert author.get("bio") == author_object.bio
        assert author.get("date_of_birth") == author_object.date_of_birth

        invalid: BookID = BookID(id=0)
        response: Response = await async_client.post(
            f"/books/{invalid.id}/authors",
            headers=headers,
            json=author_object.model_dump(),
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), "Несуществующий id книги"

    async def test_get(
        self,
        book_id_object: BookID,
        async_client: AsyncClient,
    ):

        response: Response = await async_client.get(f"/books/{book_id_object.id}/authors")

        assert response.status_code == status.HTTP_200_OK

        authors: list = response.json()

        assert authors, "Список авторов книги не должен быть пустым"

        response: Response = await async_client.get("/authors")

        assert response.status_code == status.HTTP_200_OK

        authors: list = response.json()

        assert any(
            filter(lambda d: d.get("book_id") == book_id_object.id, authors)
        ), "Список авторов должен содержать автора добавленной книги"

    async def test_update(
        self,
        async_client: AsyncClient,
        author_id_object: AuthorID,
        admin_token: str,
        reader_token: str,
    ):
        params = AuthorUpdate(bio="New bio information")

        headers_reader = {"Authorization": reader_token}

        response: Response = await async_client.patch(
            f"/authors/{author_id_object.id}",
            headers=headers_reader,
            params=params.model_dump(exclude_none=True),
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Изменить данные автора может только администратор"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.patch(
            f"/authors/{author_id_object.id}",
            headers=headers,
            params=params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        result: AuthorReturn = AuthorReturn(**response.json())

        assert result.id == author_id_object.id
        assert result.bio == params.bio

    async def test_delete(
        self,
        async_client: AsyncClient,
        book_id_object: BookID,
        author_id_object: AuthorID,
        admin_token: str,
        reader_token: str,
    ):

        headers_reader = {"Authorization": reader_token}

        response: Response = await async_client.delete(
            f"/authors/{author_id_object.id}", headers=headers_reader
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Удалить автора может только администратор"

        headers = {"Authorization": admin_token}

        response: Response = await async_client.delete(
            f"/authors/{author_id_object.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK

        deleted: AuthorReturn = AuthorReturn(**response.json())

        assert deleted.id == author_id_object.id

        response: Response = await async_client.get(f"/books/{book_id_object.id}/authors")

        assert response.status_code == status.HTTP_200_OK

        authors: list = response.json()

        assert (
            deleted not in authors
        ), "Список авторов книги не должен содержать удаленного автора"
