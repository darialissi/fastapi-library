from advanced_alchemy.extensions.fastapi import repository

from domain.models.user import UserModel


class UserRepo(repository.SQLAlchemyAsyncRepository[UserModel]):

    model_type = UserModel
