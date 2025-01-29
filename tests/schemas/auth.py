from pydantic import BaseModel


class OAuth2Form(BaseModel):

    grant_type: str = "password"
    username: str
    password: str
    scope: str = ""
    client_id: str = ""
    client_secret: str = ""
