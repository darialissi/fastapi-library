from fastapi import status

from utils.exceptions import HTTPExceptionBase


class AuthExceptions:

    class InvalidCredentialsException(HTTPExceptionBase):
        status_code = status.HTTP_401_UNAUTHORIZED
        detail = "Недействительные аутентификационные данные"
        headers = {"WWW-Authenticate": "Bearer"}

    class AccessAdminException(HTTPExceptionBase):
        status_code = status.HTTP_403_FORBIDDEN
        detail = "Необходимы права администратора"

    class AccessReaderException(HTTPExceptionBase):
        status_code = status.HTTP_403_FORBIDDEN
        detail = "Необходимы права читателя"


class AuthorExceptions:

    class ExistedException(HTTPExceptionBase):
        status_code = status.HTTP_409_CONFLICT
        detail = "Автор уже существует в системе"

    class NotFoundException(HTTPExceptionBase):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Автор не найден"


class BookExceptions:

    class ExistedException(HTTPExceptionBase):
        status_code = status.HTTP_409_CONFLICT
        detail = "Книга уже существует в системе"

    class NotFoundException(HTTPExceptionBase):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Книга не найдена"

    class CountLimitException(HTTPExceptionBase):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Количество экземпляров ограничено"

    class ExistedUserException(HTTPExceptionBase):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Читатель может иметь только 1 экземпляр"


class UserExceptions:

    class ExistedException(HTTPExceptionBase):
        status_code = status.HTTP_409_CONFLICT
        detail = "Пользователь уже существует в системе"

    class NotFoundException(HTTPExceptionBase):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Пользователь не найден"

    class CountLimitException(HTTPExceptionBase):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Пользователь может взять не более 5 книг"
