from typing import List
from pydantic import BaseModel

class PostionDTO(BaseModel):
    x: int
    y: int

class MoveDTO(BaseModel):
    player: str
    postion: PostionDTO

class CreateMoveDTO(BaseModel):
    gameId: int
    player: str
    postion: PostionDTO

class GameStateDTO(BaseModel):
    moves: List[MoveDTO]
    player_x: str
    player_o: str
    current_player: int
