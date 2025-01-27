from fastapi import HTTPException, status


class HTTPExceptionBase(HTTPException):
    """
    Base class for all exceptions
    """

    __slots__ = ()

    status_code: status
    detail: str
    headers: dict = {}

    def __init__(self):
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=self.headers
        )
