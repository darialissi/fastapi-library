from .http.auth.controller import auth_router
from .http.author import author_router
from .http.book import book_router
from .http.user import user_router

all_routers = [auth_router, user_router, book_router, author_router]
