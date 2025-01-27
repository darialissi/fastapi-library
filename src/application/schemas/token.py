from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    """
    Схема Token, валидирует вывод
    """

    access_token: str = Field(min_length=10)
    token_type: str = Field(default="bearer")
