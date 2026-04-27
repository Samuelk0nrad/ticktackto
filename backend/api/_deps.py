from fastapi import Depends, Request
from sqlalchemy import Engine

from ._auth import get_current_user, oauth2_scheme
from ..model import User
from ..service import GameService


def get_engine(request: Request) -> Engine:
    return request.app.state.engine


def get_game_service(engine: Engine = Depends(get_engine)) -> GameService:
    return GameService(engine=engine)


def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    engine: Engine = Depends(get_engine),
) -> User:
    return get_current_user(token=token, engine=engine)
