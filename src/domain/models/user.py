from typing import List

from advanced_alchemy.extensions.fastapi import base
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .role import RoleType


class UserModel(base.BigIntBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleType] = mapped_column(
        Enum(RoleType, create_constraint=False, native_enum=False)
    )

    books: Mapped[List["BookUserModel"]] = relationship(back_populates="user")  # type: ignore # noqa: F821
