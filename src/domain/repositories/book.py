from advanced_alchemy.extensions.fastapi import repository

from domain.models.book import BookModel


class BookRepo(repository.SQLAlchemyAsyncRepository[BookModel]):

    model_type = BookModel
