from advanced_alchemy.extensions.fastapi import repository

from domain.models.author import AuthorModel


class AuthorRepo(repository.SQLAlchemyAsyncRepository[AuthorModel]):

    model_type = AuthorModel
