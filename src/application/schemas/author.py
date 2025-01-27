from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Author(BaseModel):
    """
    Схема модели Author, валидирует ввод
    """

    name: str = Field(min_length=5)
    bio: Optional[str]
    date_of_birth: date

    @field_validator("date_of_birth")
    def check_date_of_birth(cls, value):
        if datetime.now() - value < timedelta(weeks=52 * 14):
            raise ValueError("Автор должен быть старше 14 лет")
        return value

    model_config = ConfigDict(strict=True)


class AuthorReturn(BaseModel):
    """
    Общая схема модели Author, валидирует вывод
    """

    id: int
    bio: Optional[str]
    date_of_birth: date
    book_id: Optional[int]

    model_config = ConfigDict(from_attributes=True, strict=True)
