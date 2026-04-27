from datetime import datetime

from pydantic import BaseModel, Field


class MoveOut(BaseModel):
    id: int
    player_id: str
    position: int = Field(ge=1, le=9)
    created_at: datetime


class GameCreateRequest(BaseModel):
    opponent_user_name: str | None = Field(default=None, description="Optional second player")


class GameOut(BaseModel):
    id: int
    player_x_id: str
    player_o_id: str | None
    current_player: int = Field(ge=1, le=2)
    status: str
    winner_id: str | None
    created_from: str
    created_at: datetime
    updated_at: datetime
    move_history: list[MoveOut]
    board: list[str | None] = Field(min_length=9, max_length=9)


class MoveResult(BaseModel):
    game: GameOut
    message: str
