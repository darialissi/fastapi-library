import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from application.schemas.token import TokenSchema
from application.schemas.user import UserAuth, UserReturn
from application.services.token import TokenService
from application.services.user import UserService
from presentation.dependencies import (
    get_logger,
    provide_token_service,
    provide_users_service,
)
from presentation.exceptions import AuthExceptions
from utils.auth.password import Password

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@auth_router.post("/token", summary="Получение access токена")
async def auth_user(
    token_service: Annotated[TokenService, Depends(provide_token_service)],
    user_service: Annotated[UserService, Depends(provide_users_service)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> TokenSchema:

    existed = await user_service.get_user(username=form_data.username)
    if not existed:
        raise AuthExceptions.InvalidCredentialsException()

    user: UserReturn = UserReturn.model_validate(existed)

    if not Password.is_valid_password(
        password=form_data.password, hashed_password=user.hashed_password
    ):
        raise AuthExceptions.InvalidCredentialsException()

    sub, access_token = await token_service.generate_token(user.id, user.role)
    logger.info(f"Issued access token: {sub=}")

    return TokenSchema(access_token=access_token)


async def get_current_user(
    token_service: Annotated[TokenService, Depends(provide_token_service)],
    token: Annotated[TokenSchema, Depends(oauth2_scheme)],
) -> UserAuth:
    """
    Получение текущего пользователя
    """

    if not token:
        raise AuthExceptions.AccessDeniedException()

    if not (sub := await token_service.get_valid_token_sub(token)):
        raise AuthExceptions.AccessDeniedException()

    _, user_id, role = sub.split(":")

    return UserAuth(id=user_id, role=role)


async def is_access_granted(
    user: Annotated[UserAuth, Depends(get_current_user)]
) -> UserAuth:
    """
    Проверка привилегированных прав
    """

    if user.role != "admin":
        raise AuthExceptions.AccessAdminException()

    return user


async def is_reader(user: Annotated[UserAuth, Depends(get_current_user)]) -> UserAuth:
    """
    Проверка прав читателя
    """

    if user.role != "reader":
        raise AuthExceptions.AccessReaderException()

    return user
