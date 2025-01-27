from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.models.genre import GenreType


class Book(BaseModel):
    """
    Схема модели Book, валидирует ввод
    """

    title: str = Field(min_length=1)
    description: str = Field(min_length=5)
    date_of_pub: date
    genres: list[GenreType]
    available_count: int = Field(ge=0, default=5)

    @field_validator("date_of_pub")
    def check_date_of_pub(cls, date_of_pub):
        if date_of_pub > datetime.now().date():
            raise ValueError(f"Невалидная дата публикации: {date_of_pub}")
        return date_of_pub

    @field_validator("genres")
    def check_genres(cls, genres):
        if not genres:
            raise ValueError("Не указан ни один жанр")
        return genres

    model_config = ConfigDict(use_enum_values=True)


class BookUpdate(BaseModel):
    """
    Схема модели Book, валидирует ввод при обновлении
    """

    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(min_length=5, default=None)
    available_count: Optional[int] = Field(ge=0, default=None)


class BookReturn(BaseModel):
    """
    Общая схема модели Book, валидирует вывод
    """

    id: int
    title: str
    description: Optional[str]
    date_of_pub: date
    genres: list[GenreType]
    available_count: int = Field(ge=0)

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class BookUserReturn(BaseModel):
    """
    Схема модели Book, валидирует вывод с дополнительными полями (relationship)
    """

    book_id: int

    borrow_date: datetime
    return_date: datetime

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )
