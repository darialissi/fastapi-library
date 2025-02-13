import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from infrastructure.database import alchemy, create_all_tables, drop_all_tables
from presentation.controllers import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_all_tables()
    yield
    await drop_all_tables()


app = FastAPI(
    title="API Library",
    root_path="/api/v1",
    lifespan=lifespan,
)

for router in all_routers:
    app.include_router(router)


alchemy.init_app(app=app)


if __name__ == "__main__":
    logging.basicConfig(
        filename="server.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
    )
