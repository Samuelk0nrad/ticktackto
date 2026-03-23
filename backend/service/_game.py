from sqlalchemy import Engine

from backend.crud._game import GameCRUD
from backend.schema._game import CreateMoveDTO

class GameService():
    def self(self, engine: Engine):
        self.crud = GameCRUD(engine=engine)

    def GetGameSate(self, gameId: int):
        gameState = self.crud.GetGameState(gameId)
        return gameState
