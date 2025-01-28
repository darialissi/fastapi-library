import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from application.schemas.book import BookUserReturn
from application.schemas.user import User, UserAuth, UserReturn, UserUpdate
from application.services.token import TokenService
from application.services.user import UserService
from domain.models.role import RoleType
from presentation.dependencies import (
    get_logger,
    provide_token_service,
    provide_users_service,
)
from presentation.exceptions import UserExceptions

from .auth.controller import get_current_user, is_access_granted, is_reader

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@user_router.post(
    "", status_code=status.HTTP_201_CREATED, summary="Добавление нового пользователя"
)
async def register_user(
    user: User,
    user_service: Annotated[UserService, Depends(provide_users_service)],
) -> UserReturn:
    existed = await user_service.get_user(username=user.username)
    if existed:
        raise UserExceptions.ExistedException()
    resp = await user_service.add_new_user(user)
    return UserReturn.model_validate(resp)


@user_router.get("/me", summary="Получение текущего пользователя")
async def get_auth_user(user: Annotated[UserAuth, Depends(get_current_user)]) -> UserAuth:
    return user


@user_router.delete("/me", summary="Удаление текущего пользователя")
async def delete_auth_user(
    token_service: Annotated[TokenService, Depends(provide_token_service)],
    user_service: Annotated[UserService, Depends(provide_users_service)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
    user: Annotated[UserAuth, Depends(get_current_user)],
) -> UserReturn:

    sub = f"user:{user.id}:{user.role}"

    await token_service.revoke_token(sub)
    logger.info(f"Revoked access token: {sub=}")

    resp = await user_service.delete_user(id=user.id)
    return UserReturn.model_validate(resp)


@user_router.patch("/me", summary="Обновление данных текущего пользователя")
async def update_auth_user(
    data: UserUpdate,
    user_service: Annotated[UserService, Depends(provide_users_service)],
    user: Annotated[UserAuth, Depends(get_current_user)],
) -> UserReturn:
    existed = await user_service.get_user(username=data.username)
    if existed and existed.id != user.id:
        raise UserExceptions.ExistedException()

    resp = await user_service.update_user(data, user_id=user.id)
    return UserReturn.model_validate(resp)


@user_router.get("/me/books", summary="Получение списка книг текущего пользователя")
async def get_reader_books(
    user_service: Annotated[UserService, Depends(provide_users_service)],
    reader: Annotated[UserAuth, Depends(is_reader)],
) -> list[BookUserReturn]:

    _, books = await user_service.get_user_with_books(id=reader.id)
    return [
        BookUserReturn(
            book_id=b.book_id, borrow_date=b.borrow_date, return_date=b.return_date
        )
        for b in books
    ]


@user_router.get(
    "/readers", summary="Получение данных всех читателей [права администратора]"
)
async def get_readers(
    user_service: Annotated[UserService, Depends(provide_users_service)],
    admin: Annotated[UserAuth, Depends(is_access_granted)],
) -> list[UserReturn]:
    readers = await user_service.get_users(role=RoleType.reader)
    return [UserReturn.model_validate(reader) for reader in readers]
