from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AuthorValidate(BaseModel):
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
        return date_of_birth.strftime("%Y-%m-%d")


class AuthorID(BaseModel):

    id: int
