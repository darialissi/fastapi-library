from pydantic import BaseModel


class OAuth2Form(BaseModel):
    """
    Валидация при аутентификации
    """

    grant_type: str = "password"
    username: str
    password: str
    scope: str = ""
    client_id: str = "default"
    client_secret: str = "default"
