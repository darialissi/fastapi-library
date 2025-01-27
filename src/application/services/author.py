from advanced_alchemy import exceptions as aexc
from advanced_alchemy.extensions.fastapi import repository

from application.schemas.author import Author, AuthorUpdate
from presentation.exceptions import AuthorExceptions


class AuthorService:

    def __init__(self, repo: repository.SQLAlchemyAsyncRepository):
        self.author_repo = repo

    async def add_new_author(self, book_id: int, author: Author):
        author_dict = author.model_dump()
        author_dict.update({"book_id": book_id})

        author = await self.author_repo.add(self.author_repo.model_type(**author_dict))
        await self.author_repo.session.commit()

        return author

    async def get_author(self, **filters):
        author = await self.author_repo.get_one_or_none(**filters)
        return author

    async def get_authors(self, **filters):
        authors = await self.author_repo.list(**filters)
        return authors

    async def update_author(self, id: int, author: AuthorUpdate):
        author_dict = author.model_dump(exclude_none=True)
        author_dict.update({"id": id})

        author = await self.author_repo.update(self.author_repo.model_type(**author_dict))
        await self.author_repo.session.commit()

        return author

    async def delete_author(self, id: int):
        try:
            author = await self.author_repo.delete(item_id=id)
            await self.author_repo.session.commit()
        except aexc.NotFoundError:
            raise AuthorExceptions.NotFoundException()
        return author
