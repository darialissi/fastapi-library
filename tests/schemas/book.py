from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from domain.models.genre import GenreType


class BookValidate(BaseModel):
    """
    Общая валидация ввода
    """

    title: str = Field(min_length=1)
    description: str = Field(min_length=5)
    date_of_pub: date
    genres: list[GenreType]
    available_count: int = Field(ge=0, default=5)

    @field_validator("date_of_pub")
    def check_date_of_pub(cls, date_of_pub: date):
        if date_of_pub > datetime.now().date():
            raise ValueError(f"Невалидная дата публикации: {date_of_pub}")
        return date_of_pub.strftime("%Y-%m-%d")

    @field_validator("genres")
    def check_genres(cls, genres: list):
        if not genres:
            raise ValueError("Не указан ни один жанр")
        return genres


class BookBorrow(BaseModel):
    """
    Валидация ввода для /borrow и /return
    """

    title: str = Field(min_length=1)
