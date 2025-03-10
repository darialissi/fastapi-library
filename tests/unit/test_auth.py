from datetime import timedelta

import pytest

from config import settings
from utils.auth.password import Password
from utils.auth.token import Token


@pytest.mark.unit
class TestPassword:

    @pytest.mark.parametrize(
        "password",
        [
            "12345abcde",
        ],
    )
    def test_hash(self, password: str):
        hashed = Password.hash_password(password)

        assert Password.is_valid_password(password, hashed)


@pytest.mark.unit
class TestToken:

    @pytest.mark.parametrize(
        "sub",
        [
            "user:1:admin",
            "user:2:reader",
        ],
    )
    def test_valid(self, sub: str):

        token = Token.encode_jwt(sub, settings.TOKEN_KEY_SECRET, timedelta(minutes=10))
        decoded = Token.decode_jwt(token, settings.TOKEN_KEY_SECRET)

        assert decoded.get("sub") == sub

    @pytest.mark.parametrize(
        "sub",
        [
            "user:1:admin",
            "user:2:reader",
        ],
    )
    def test_invalid(self, sub: str):

        token = Token.encode_jwt(sub, settings.TOKEN_KEY_SECRET, timedelta(seconds=0))
        decoded = Token.decode_jwt(token, settings.TOKEN_KEY_SECRET)

        assert isinstance(decoded, dict)
        assert decoded.get("sub") is None
