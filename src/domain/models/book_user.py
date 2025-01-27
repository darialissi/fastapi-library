from datetime import datetime, timedelta

from advanced_alchemy.extensions.fastapi import base
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

BORROW_DAYS = 5


class BookUserModel(base.DefaultBase):
    __tablename__ = "books_users"

    borrow_date: Mapped[datetime] = mapped_column(server_default=func.now())
    return_date: Mapped[datetime] = mapped_column(
        server_default=func.now() + timedelta(days=BORROW_DAYS)
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    book: Mapped["BookModel"] = relationship(back_populates="users")  # type: ignore # noqa: F821
    user: Mapped["UserModel"] = relationship(back_populates="books")  # type: ignore # noqa: F821
