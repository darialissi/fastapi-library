from pydantic import BaseModel, ConfigDict, Field

from domain.models.role import RoleType


class UserAuth(BaseModel):
    """
    Схема для аутентификации/авторизации
    """

    id: int
    role: str


class User(BaseModel):
    """
    Схема модели User, валидирует ввод
    """

    username: str = Field(min_length=5)
    password: str = Field(min_length=5)
    role: RoleType

    model_config = ConfigDict(use_enum_values=True)


class UserReturn(BaseModel):
    """
    Общая схема модели User, валидирует вывод
    """

    id: int
    username: str
    hashed_password: str = Field(exclude=True)
    role: RoleType

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class UserUpdate(BaseModel):
    """
    Схема модели User, валидирует ввод при обновлении
    """

    username: str = Field(min_length=5)
    password: str = Field(min_length=5)
