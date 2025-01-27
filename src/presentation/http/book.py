import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from application.schemas.book import Book, BookReturn
from application.schemas.user import UserReturn
from application.services.book import BookService
from application.services.user import UserService
from presentation.dependencies import (
    get_logger,
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
    "",
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
