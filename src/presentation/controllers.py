from .http.auth.controller import auth_router
from .http.book import book_router
from .http.user import user_router

# router_posts.include_router(router_categories)
# router_posts.include_router(router_comments)

all_routers = [auth_router, user_router, book_router]
