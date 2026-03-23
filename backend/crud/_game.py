from sqlalchemy import Engine
from sqlalchemy.orm import Session
from backend.model import Game
from backend.schema._game import GameStateDTO, MoveDTO, PostionDTO

class GameCRUD:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def GetGameState(self, gameId) -> GameStateDTO:
        with Session(self.engine) as session:
            game = session.query(Game).filter(Game.id == gameId).one()
            movesDto = []
            for move in game.moves:
                movesDto.append(
                    MoveDTO(
                        player=move.player_id, 
                        postion=PostionDTO(x=move.positionx, y=move.positiony)
                    )
                )
            gameDto = GameStateDTO(
                moves=movesDto,
                player_o=game.player_x_id,
                player_x=game.player_x_id,
                current_player=game.current_player
            )
            return gameDto

