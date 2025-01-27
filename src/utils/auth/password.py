import bcrypt


class Password:

    @classmethod
    def hash_password(
        cls,
        password: str,
    ) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode()

    @classmethod
    def is_valid_password(
        cls,
        password: str,
        hashed_password: str,
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password.encode(),
        )
