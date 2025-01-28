from typing import Annotated

from fastapi import APIRouter, Depends

from application.schemas.author import AuthorReturn, AuthorUpdate
from application.schemas.user import UserAuth
from application.services.author import AuthorService
from presentation.dependencies import provide_authors_service

from .auth.controller import is_access_granted

author_router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
)


@author_router.get("", summary="Получение актуального списка авторов")
async def get_authors(
    author_service: Annotated[AuthorService, Depends(provide_authors_service)],
) -> list[AuthorReturn]:
    authors = await author_service.get_authors()
    return [AuthorReturn.model_validate(author) for author in authors]


@author_router.patch(
    "/{id}",
    summary="Изменение выбранных полей автора [права администратора]",
)
async def update_author(
    id: int,
    params: Annotated[AuthorUpdate, Depends()],
    author_service: Annotated[AuthorService, Depends(provide_authors_service)],
    admin: Annotated[UserAuth, Depends(is_access_granted)],
) -> AuthorReturn:

    resp = await author_service.update_author(id=id, author=params)
    return AuthorReturn.model_validate(resp)


@author_router.delete(
    "/{id}",
    summary="Удаление автора по идентификатору [права администратора]",
)
async def delete_author(
    id: int,
    author_service: Annotated[AuthorService, Depends(provide_authors_service)],
    admin: Annotated[UserAuth, Depends(is_access_granted)],
) -> AuthorReturn:

    resp = await author_service.delete_author(id=id)
    return AuthorReturn.model_validate(resp)
