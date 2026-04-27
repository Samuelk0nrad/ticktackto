from sqlalchemy import Engine

from ..crud import GameCRUD
from ..model import Game
from ..schema import GameOut, MoveOut


class GameService:
    def __init__(self, engine: Engine) -> None:
        self.crud = GameCRUD(engine=engine)

    def create_game(self, creator_user_name: str, opponent_user_name: str | None) -> GameOut:
        game = self.crud.create_game(creator_user_name=creator_user_name, opponent_user_name=opponent_user_name)
        return self._to_out(game)

    def list_games(self) -> list[GameOut]:
        return [self._to_out(game) for game in self.crud.list_games()]

    def get_game(self, game_id: int) -> GameOut:
        game = self.crud.get_game(game_id)
        if game is None:
            raise LookupError("Game not found")
        return self._to_out(game)

    def make_move(self, game_id: int, user_name: str, position: int) -> GameOut:
        game = self.crud.make_move(game_id=game_id, user_name=user_name, position=position)
        return self._to_out(game)

    def delete_finished_game(self, game_id: int) -> bool:
        return self.crud.delete_finished_game(game_id)

    @staticmethod
    def _to_out(game: Game) -> GameOut:
        board = [None] * 9
        move_history: list[MoveOut] = []
        for move in game.moves:
            position = (move.positiony - 1) * 3 + move.positionx
            symbol = "X" if move.player_id == game.player_x_id else "O"
            board[position - 1] = symbol
            move_history.append(
                MoveOut(
                    id=move.id,
                    player_id=move.player_id,
                    position=position,
                    created_at=move.created_at,
                )
            )

        return GameOut(
            id=game.id,
            player_x_id=game.player_x_id,
            player_o_id=game.player_o_id,
            current_player=game.current_player,
            status=game.status,
            winner_id=game.winner_id,
            created_from=game.created_from,
            created_at=game.created_at,
            updated_at=game.updated_at,
            move_history=move_history,
            board=board,
        )
