from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from backend.api._auth import authenticate_user, create_access_token, get_current_user, hash_password
from backend.model import Entity, Person, User
from backend.schema import (
    GameCreateRequest,
    GameOut,
    LoginRequest,
    MoveResult,
    RegisterRequest,
    TokenResponse,
)
from backend.service import GameService


def define_routes(app: FastAPI) -> None:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

    def get_engine() -> Engine:
        return app.state.engine

    def get_game_service(engine: Engine = Depends(get_engine)) -> GameService:
        return GameService(engine=engine)

    def get_authenticated_user(
        token: str = Depends(oauth2_scheme),
        engine: Engine = Depends(get_engine),
    ) -> User:
        return get_current_user(token=token, engine=engine)

    @app.get("/", tags=["health"], summary="Health check")
    def get_root() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/auth/register",
        response_model=TokenResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["auth"],
        summary="Register a new user",
    )
    def register_user(payload: RegisterRequest, engine: Engine = Depends(get_engine)) -> TokenResponse:
        with Session(engine) as session:
            existing = session.scalars(select(User).where(User.user_name == payload.user_name)).first()
            if existing is not None:
                raise HTTPException(status_code=409, detail="Username already exists")

            if payload.first_name:
                entity = Person(name=payload.name, first_name=payload.first_name)
            else:
                entity = Entity(name=payload.name)

            user = User(
                user_name=payload.user_name,
                password_hash=hash_password(payload.password),
                entity=entity,
            )
            session.add(entity)
            session.add(user)
            session.commit()

        token = create_access_token(subject=payload.user_name)
        return TokenResponse(access_token=token)

    @app.post(
        "/auth/token",
        response_model=TokenResponse,
        tags=["auth"],
        summary="Log in and receive JWT token",
    )
    def login(payload: LoginRequest, engine: Engine = Depends(get_engine)) -> TokenResponse:
        user = authenticate_user(engine=engine, user_name=payload.user_name, password=payload.password)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_access_token(subject=user.user_name)
        return TokenResponse(access_token=token)

    @app.post(
        "/games",
        response_model=GameOut,
        status_code=status.HTTP_201_CREATED,
        tags=["games"],
        summary="Create a new game",
    )
    def create_game(
        payload: GameCreateRequest,
        service: GameService = Depends(get_game_service),
        user: User = Depends(get_authenticated_user),
    ) -> GameOut:
        print(f"Creating game: {payload} for user: {user.user_name}")
        try:
            return service.create_game(
                creator_user_name=user.user_name,
                opponent_user_name=payload.opponent_user_name,
            )
        except ValueError as exc:
            print(f"Error creating game: {exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/games",
        response_model=list[GameOut],
        tags=["games"],
        summary="Retrieve all games",
    )
    def list_games(
        service: GameService = Depends(get_game_service),
        _: User = Depends(get_authenticated_user),
    ) -> list[GameOut]:
        return service.list_games()

    @app.get(
        "/games/{game_id}",
        response_model=GameOut,
        tags=["games"],
        summary="Retrieve one game with move history",
    )
    def get_game(
        game_id: int,
        service: GameService = Depends(get_game_service),
        _: User = Depends(get_authenticated_user),
    ) -> GameOut:
        try:
            return service.get_game(game_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.put(
        "/games/{game_id}/move/{position}",
        response_model=MoveResult,
        tags=["games"],
        summary="Make a move at position 1-9",
    )
    def make_move(
        game_id: int,
        position: int,
        service: GameService = Depends(get_game_service),
        user: User = Depends(get_authenticated_user),
    ) -> MoveResult:
        try:
            game = service.make_move(game_id=game_id, user_name=user.user_name, position=position)
            return MoveResult(game=game, message="Move accepted")
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.delete(
        "/games/{game_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["games"],
        summary="Delete a completed game",
    )
    def delete_finished_game(
        game_id: int,
        service: GameService = Depends(get_game_service),
        _: User = Depends(get_authenticated_user),
    ) -> Response:
        try:
            service.delete_finished_game(game_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)
