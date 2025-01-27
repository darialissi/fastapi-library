import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from application.schemas.author import Author, AuthorReturn
from application.schemas.book import Book, BookReturn, BookUpdate
from application.schemas.user import UserReturn
from application.services.author import AuthorService
from application.services.book import BookService
from application.services.user import UserService
from presentation.dependencies import (
    get_logger,
    provide_authors_service,
    provide_books_service,
    provide_users_service,
)
from presentation.exceptions import BookExceptions, UserExceptions

from .auth.controller import is_access_granted, is_reader

book_router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@book_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Добавление новой книги [права администратора]",
)
async def add_book(
    book: Book,
    books_service: Annotated[BookService, Depends(provide_books_service)],
    admin: Annotated[UserReturn, Depends(is_access_granted)],
) -> BookReturn:
    existed = await books_service.get_book(title=book.title)
    if existed:
        raise BookExceptions.ExistedException()

    resp = await books_service.add_new_book(book)
    return BookReturn.model_validate(resp)


@book_router.get("", summary="Получение актуального списка книг")
async def get_books(
    books_service: Annotated[BookService, Depends(provide_books_service)]
) -> list[BookReturn]:
    books = await books_service.get_all_books()
    return [BookReturn.model_validate(book) for book in books]


@book_router.patch(
    "/borrow",
    summary="Выдача книги читателю",
)
async def borrow_book(
    title: str,
    books_service: Annotated[BookService, Depends(provide_books_service)],
    user_service: Annotated[UserService, Depends(provide_users_service)],
    reader: Annotated[UserReturn, Depends(is_reader)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> BookReturn:

    book, users = await books_service.get_book_with_users(title=title)
    if not book:
        raise BookExceptions.NotFoundException()

    if book.available_count == 0:
        raise BookExceptions.CountLimitException()

    if len(users) == 5:
        raise UserExceptions.CountLimitException()

    user = await user_service.get_user(id=reader.id)
    resp = await books_service.borrow_book(book=book, user=user, users=users)

    logger.info(
        f"Borrowed book: {title=}. Reader: {reader.id=}. "
        f"Available book count: {resp.available_count}."
    )

    return BookReturn.model_validate(resp)


@book_router.patch(
    "/return",
    summary="Возврат книги читателем",
)
async def return_book(
    title: str,
    books_service: Annotated[BookService, Depends(provide_books_service)],
    user_service: Annotated[UserService, Depends(provide_users_service)],
    reader: Annotated[UserReturn, Depends(is_reader)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> BookReturn:

    book, users = await books_service.get_book_with_users(title=title)
    if not book:
        raise BookExceptions.NotFoundException()

    user = await user_service.get_user(id=reader.id)
    resp = await books_service.return_book(book=book, user=user, users=users)

    logger.info(
        f"Returned book: {title=}. Reader: {reader.id=}. "
        f"Available book count: {resp.available_count}."
    )

    return BookReturn.model_validate(resp)


@book_router.patch(
    "/{id}",
    summary="Изменение выбранных полей книги [права администратора]",
)
async def update_book(
    id: int,
    params: Annotated[BookUpdate, Depends()],
    books_service: Annotated[BookService, Depends(provide_books_service)],
    admin: Annotated[UserReturn, Depends(is_access_granted)],
) -> BookReturn:

    if params.title:
        if await books_service.get_book(title=params.title):
            raise BookExceptions.ExistedException()

    resp = await books_service.update_book(id=id, book=params)
    return BookReturn.model_validate(resp)


@book_router.delete(
    "/{id}",
    summary="Удаление книги по идентификатору [права администратора]",
)
async def delete_book(
    id: int,
    books_service: Annotated[BookService, Depends(provide_books_service)],
    admin: Annotated[UserReturn, Depends(is_access_granted)],
) -> BookReturn:

    resp = await books_service.delete_book(id=id)
    return BookReturn.model_validate(resp)


@book_router.post(
    "/{id}/authors",
    status_code=status.HTTP_201_CREATED,
    summary="Добавление нового автора книги [права администратора]",
)
async def add_author(
    id: int,
    author: Author,
    author_service: Annotated[AuthorService, Depends(provide_authors_service)],
    books_service: Annotated[BookService, Depends(provide_books_service)],
    admin: Annotated[UserReturn, Depends(is_access_granted)],
) -> AuthorReturn:

    existed = await books_service.get_book(id=id)
    if not existed:
        raise BookExceptions.NotFoundException()

    resp = await author_service.add_new_author(book_id=id, author=author)
    return AuthorReturn.model_validate(resp)


@book_router.get("/{id}/authors", summary="Получение авторов книги по идентификатору")
async def get_book_authors(
    id: int, author_service: Annotated[AuthorService, Depends(provide_authors_service)]
) -> list[AuthorReturn]:
    authors = await author_service.get_authors(book_id=id)
    return [AuthorReturn.model_validate(author) for author in authors]
