import os

from fastapi import FastAPI

from ..engine import get_engine

from ._routes import define_routes

_app: FastAPI | None = None


def build_app():
    global _app
    if not _app:
        _app = FastAPI()
        config_file = os.getenv("TICTACTOE_CONFIG_FILE", "")
        _app.state.engine = get_engine(config_file)
        define_routes(_app)

    return _app
