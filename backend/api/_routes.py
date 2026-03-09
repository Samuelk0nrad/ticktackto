from fastapi import FastAPI


def define_routes(app: FastAPI) -> None:

    @app.get("/")
    def get_root():
        return {"/"}

    assert get_root
