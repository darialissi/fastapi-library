from advanced_alchemy import exceptions as aexc
from advanced_alchemy.extensions.fastapi import repository
from sqlalchemy import exc

from application.schemas.book import Book, BookUpdate
from domain.models.book import BookModel
from domain.models.book_user import BookUserModel
from domain.models.user import UserModel
from presentation.exceptions import BookExceptions


class BookService:

    def __init__(self, book_repo: repository.SQLAlchemyAsyncRepository):
        self.book_repo = book_repo

    async def add_new_book(self, book: Book):
        book_dict = book.model_dump()

        book = await self.book_repo.add(self.book_repo.model_type(**book_dict))
        await self.book_repo.session.commit()

        return book

    async def get_book(self, **filters):
        book = await self.book_repo.get_one_or_none(**filters)
        return book

    async def get_all_books(self):
        books = await self.book_repo.list()
        return books

    async def update_book(self, id: int, book: BookUpdate):
        book_dict = book.model_dump(exclude_none=True)
        book_dict.update({"id": id})

        book = await self.book_repo.update(self.book_repo.model_type(**book_dict))
        await self.book_repo.session.commit()

        return book

    async def delete_book(self, id: int):
        try:
            book = await self.book_repo.delete(item_id=id)
            await self.book_repo.session.commit()
        except aexc.NotFoundError:
            raise BookExceptions.NotFoundException()
        return book

    async def get_book_with_users(self, **filters) -> tuple:
        book = await self.book_repo.get_one_or_none(**filters, load="selectin")
        if not book:
            return None, None
        users = await book.awaitable_attrs.users
        return book, users

    async def borrow_book(self, book: BookModel, user: UserModel, users: list):
        book.available_count -= 1
        users.append(BookUserModel(user=user))
        try:
            await self.book_repo.session.commit()
        except exc.IntegrityError:
            raise BookExceptions.ExistedUserException()
        return book

    async def return_book(self, book: BookModel, user: UserModel, users: list):
        book.available_count += 1
        user_model = list(filter(lambda x: x.user_id == user.id, users))[0]
        try:
            users.remove(user_model)
            await self.book_repo.session.commit()
        except ValueError:
            raise BookExceptions.NotFoundException()
        return book
