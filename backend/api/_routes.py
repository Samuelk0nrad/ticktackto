from fastapi import FastAPI

from ._auth_routes import router as auth_router
from ._game import router as game_router
from ._health_routes import router as health_router


def define_routes(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(game_router)
