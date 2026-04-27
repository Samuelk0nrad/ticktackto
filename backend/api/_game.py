from fastapi import APIRouter, Depends, HTTPException, Response, status

from ._deps import get_authenticated_user, get_game_service
from ..model import User
from ..schema import GameCreateRequest, GameOut, MoveResult
from ..service import GameService


router = APIRouter(prefix="/games", tags=["games"])


@router.post(
    "",
    response_model=GameOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new game",
)
def create_game(
    payload: GameCreateRequest,
    service: GameService = Depends(get_game_service),
    user: User = Depends(get_authenticated_user),
) -> GameOut:
    try:
        return service.create_game(
            creator_user_name=user.user_name,
            opponent_user_name=payload.opponent_user_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[GameOut],
    summary="Retrieve all games",
)
def list_games(
    service: GameService = Depends(get_game_service),
    _: User = Depends(get_authenticated_user),
) -> list[GameOut]:
    return service.list_games()


@router.get(
    "/{game_id}",
    response_model=GameOut,
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


@router.put(
    "/{game_id}/move/{position}",
    response_model=MoveResult,
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


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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
