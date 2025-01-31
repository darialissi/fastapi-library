from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Author(BaseModel):
    """
    Схема модели Author, валидирует ввод
    """

    name: str = Field(min_length=5)
    bio: Optional[str] = Field(default="")
    date_of_birth: date

    @field_validator("date_of_birth")
    def check_date_of_birth(cls, date_of_birth):
        if datetime.now().date() - date_of_birth < timedelta(weeks=52 * 14):
            raise ValueError("Автор должен быть старше 14 лет")
        return date_of_birth


class AuthorUpdate(BaseModel):
    """
    Схема модели Author, валидирует ввод при обновлении
    """

    bio: Optional[str] = Field(default=None)


class AuthorReturn(BaseModel):
    """
    Общая схема модели Author, валидирует вывод
    """

    id: int
    name: str
    bio: Optional[str] = Field(default="")
    date_of_birth: date
    book_id: int

    model_config = ConfigDict(from_attributes=True)
