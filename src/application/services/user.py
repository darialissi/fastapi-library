from advanced_alchemy.extensions.fastapi import repository

from application.schemas.user import User, UserUpdate
from utils.auth.password import Password


class UserService:

    def __init__(self, repo: repository.SQLAlchemyAsyncRepository):
        self.user_repo = repo

    async def add_new_user(self, user: User):
        user_dict = user.model_dump()
        password = user_dict.pop("password")
        user_dict.update({"hashed_password": Password.hash_password(password)})
        user = await self.user_repo.add(self.user_repo.model_type(**user_dict))
        await self.user_repo.session.commit()
        return user

    async def get_user(self, **filters):
        user = await self.user_repo.get_one_or_none(**filters)
        return user

    async def get_users(self, **filters):
        users = await self.user_repo.list(**filters)
        return users

    async def update_user(self, user: UserUpdate, user_id: int):
        user_dict = user.model_dump()
        password = user_dict.pop("password")
        user_dict.update(
            {"id": user_id, "hashed_password": Password.hash_password(password)}
        )
        user = await self.user_repo.update(self.user_repo.model_type(**user_dict))
        await self.user_repo.session.commit()
        return user

    async def delete_user(self, id: int):
        user = await self.user_repo.delete(item_id=id)
        await self.user_repo.session.commit()
        return user

    async def get_user_with_books(self, **filters) -> tuple:
        user = await self.user_repo.get_one_or_none(**filters, load="selectin")
        if not user:
            return None, None
        books = await user.awaitable_attrs.books
        return user, books
