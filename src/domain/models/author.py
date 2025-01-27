from datetime import date

from advanced_alchemy.extensions.fastapi import base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AuthorModel(base.BigIntBase):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str]
    date_of_birth: Mapped[date] = mapped_column(nullable=False)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    book: Mapped["BookModel"] = relationship(back_populates="authors")  # type: ignore # noqa: F821
