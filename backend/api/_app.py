from fastapi import FastAPI

from ._routes import define_routes

_app: FastAPI | None = None


def build_app():
    global _app
    if not _app:
        _app = FastAPI()
        define_routes(_app)

    return _app
