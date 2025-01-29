from datetime import timedelta

import pytest

from config import settings
from utils.auth.password import Password
from utils.auth.token import Token


@pytest.mark.unit
class TestAuth:

    @pytest.mark.parametrize(
        "password",
        [
            "12345abcde",
        ],
    )
    def test_hash(self, password: str):
        hashed = Password.hash_password(password)

        assert Password.is_valid_password(password, hashed)

    @pytest.mark.parametrize(
        "sub",
        [
            "user:1:admin",
        ],
    )
    def test_jwt(self, sub: str):

        token = Token.encode_jwt(sub, settings.TOKEN_KEY_SECRET, timedelta(minutes=10))
        decoded = Token.decode_jwt(token, settings.TOKEN_KEY_SECRET)

        assert decoded.get("sub") == sub

        token = Token.encode_jwt(sub, settings.TOKEN_KEY_SECRET, timedelta(seconds=0))
        decoded = Token.decode_jwt(token, settings.TOKEN_KEY_SECRET)

        assert isinstance(decoded, dict)
        assert decoded.get("sub") is None
