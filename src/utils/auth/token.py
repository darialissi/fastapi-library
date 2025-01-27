from datetime import datetime, timedelta, timezone

import jwt


class Token:

    @classmethod
    def encode_jwt(
        cls,
        sub: str,
        private_key: str,
        expire: timedelta,
    ) -> str:
        to_encode = {"sub": sub}
        now = datetime.now(timezone.utc)
        expire = now + expire
        to_encode.update(
            exp=expire,
            iat=now,
        )
        encoded = jwt.encode(
            to_encode,
            private_key,
            algorithm="HS256",
        )
        return encoded

    @classmethod
    def decode_jwt(
        cls,
        token: str,
        private_key: str,
    ) -> dict:
        try:
            return jwt.decode(token, private_key, algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError:
            return {}
