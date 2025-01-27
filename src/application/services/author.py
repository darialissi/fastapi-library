from advanced_alchemy.extensions.fastapi import repository


class AuthorService:

    def __init__(self, repo: repository.SQLAlchemyAsyncRepository):
        self.author_repo = repo
