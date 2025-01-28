from datetime import timedelta

from config import settings
from domain.repositories.token import TokenRepo
from utils.auth.token import Token


class TokenService:

    def __init__(
        self,
        token_repo: TokenRepo,
    ):
        self.token_repo = token_repo

    async def generate_token(self, user_id: int, user_role: str) -> str:
        sub = f"user:{user_id}:{user_role}"
        ex = timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        token = Token.encode_jwt(
            sub=sub,
            private_key=settings.TOKEN_KEY_SECRET,
            expire=ex,
        )
        await self.token_repo.add(key=sub, value=token, expire=ex)
        return sub, token

    async def get_valid_token_sub(self, token: str):
        payload: dict = Token.decode_jwt(
            token=token, private_key=settings.TOKEN_KEY_SECRET
        )
        sub = payload.get("sub")
        if not sub:
            return None
        valid_token = await self.token_repo.get(sub)
        if not valid_token:
            return None
        return sub

    async def revoke_token(self, sub: str):
        await self.token_repo.revoke(sub)
        return sub
