import logging

import uvicorn
from fastapi import FastAPI

from infrastructure.database import alchemy, drop_all_tables
from presentation.controllers import all_routers

app = FastAPI(
    title="API Library",
    root_path="/api",
    on_shutdown=[drop_all_tables],
)

alchemy.init_app(app=app)

for router in all_routers:
    app.include_router(router)


if __name__ == "__main__":
    logging.basicConfig(
        filename="server.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
    )
