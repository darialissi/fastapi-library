from datetime import date

import pytest
from schemas.author import AuthorID, AuthorValidate


@pytest.fixture
def author_id_object() -> AuthorID:
    return AuthorID(id=1)


@pytest.fixture
def author_object() -> AuthorValidate:
    return AuthorValidate(
        name="Author-0",
        date_of_birth=date(2000, 1, 1),
    )


@pytest.fixture(scope="session")
def author_objects() -> list[AuthorValidate]:
    result = []
    for i in range(1, 5):
        data = AuthorValidate(
            name=f"Author-{i}",
            date_of_birth=date(1990, 1, 1),
        )
        result.append(data)
    return result
