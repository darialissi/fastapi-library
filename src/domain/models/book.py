from datetime import date
from typing import List

import sqlalchemy.dialects.postgresql as pg
from advanced_alchemy.extensions.fastapi import base
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .genre import GenreType


class BookModel(base.BigIntBase):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    date_of_pub: Mapped[date] = mapped_column(nullable=False)
    available_count: Mapped[int] = mapped_column(nullable=False)
    genres: Mapped[list[GenreType]] = mapped_column(
        pg.ARRAY(Enum(GenreType, create_constraint=False, native_enum=False))
    )

    users: Mapped[List["BookUserModel"]] = relationship(back_populates="book")  # type: ignore # noqa: F821
    authors: Mapped[List["AuthorModel"]] = relationship(back_populates="book")  # type: ignore # noqa: F821
