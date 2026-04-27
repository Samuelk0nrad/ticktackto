from collections.abc import Sequence

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload

from ..model import Game, GameStatus, Move, User


class GameCRUD:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create_game(self, creator_user_name: str, opponent_user_name: str | None = None) -> Game:
        with Session(self.engine, expire_on_commit=False) as session:
            creator = self._get_user_or_none(session, creator_user_name)
            if creator is None:
                raise ValueError("Creator user does not exist")

            if opponent_user_name is not None:
                if opponent_user_name == creator_user_name:
                    raise ValueError("Opponent must be different from creator")
                opponent = self._get_user_or_none(session, opponent_user_name)
                if opponent is None:
                    raise ValueError("Opponent user does not exist")
                status = GameStatus.IN_PROGRESS.value
            else:
                status = GameStatus.WAITING.value

            game = Game(
                player_x_id=creator_user_name,
                player_o_id=opponent_user_name,
                current_player=1,
                status=status,
                created_from=creator_user_name,
            )
            session.add(game)
            session.commit()
            stmt = select(Game).where(Game.id == game.id).options(selectinload(Game.moves))
            loaded_game = session.scalars(stmt).first()
            if loaded_game is None:
                raise LookupError("Game not found")
            return loaded_game

    def list_games(self) -> list[Game]:
        with Session(self.engine, expire_on_commit=False) as session:
            stmt = select(Game).options(selectinload(Game.moves)).order_by(Game.id)
            return list(session.scalars(stmt).all())

    def get_game(self, game_id: int) -> Game | None:
        with Session(self.engine, expire_on_commit=False) as session:
            stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.moves))
            return session.scalars(stmt).first()

    def make_move(self, game_id: int, user_name: str, position: int) -> Game:
        if position < 1 or position > 9:
            raise ValueError("Position must be between 1 and 9")

        with Session(self.engine, expire_on_commit=False) as session:
            stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.moves))
            game = session.scalars(stmt).first()
            if game is None:
                raise LookupError("Game not found")

            if game.status == GameStatus.FINISHED.value:
                raise ValueError("Game is already finished")

            if game.player_o_id is None and user_name != game.player_x_id:
                game.player_o_id = user_name
                game.status = GameStatus.IN_PROGRESS.value

            expected_player = self._current_player_user_name(game)
            if expected_player is None:
                raise ValueError("Second player has not joined yet")
            if expected_player != user_name:
                raise PermissionError("It is not your turn")

            board = self._build_board(game.moves, game.player_x_id, game.player_o_id)
            if board[position - 1] is not None:
                raise ValueError("Position already taken")

            position_x, position_y = self._position_to_coordinates(position)
            move = Move(
                game_id=game.id,
                player_id=user_name,
                positionx=position_x,
                positiony=position_y,
            )
            session.add(move)
            session.flush()

            symbol = "X" if user_name == game.player_x_id else "O"
            board[position - 1] = symbol

            if self._has_winning_line(board, symbol):
                game.status = GameStatus.FINISHED.value
                game.winner_id = user_name
            elif all(cell is not None for cell in board):
                game.status = GameStatus.FINISHED.value
                game.winner_id = None
            else:
                game.status = GameStatus.IN_PROGRESS.value
                game.current_player = 2 if game.current_player == 1 else 1

            session.commit()
            session.refresh(game)
            _ = game.moves
            return game

    def delete_finished_game(self, game_id: int) -> bool:
        with Session(self.engine, expire_on_commit=False) as session:
            game = session.get(Game, game_id)
            if game is None:
                raise LookupError("Game not found")
            if game.status != GameStatus.FINISHED.value:
                raise ValueError("Only finished games can be deleted")
            session.delete(game)
            session.commit()
            return True

    @staticmethod
    def _get_user_or_none(session: Session, user_name: str) -> User | None:
        stmt = select(User).where(User.user_name == user_name)
        return session.scalars(stmt).first()

    @staticmethod
    def _position_to_coordinates(position: int) -> tuple[int, int]:
        # Position mapping is 1-9 left-to-right, top-to-bottom.
        zero_based = position - 1
        return (zero_based % 3) + 1, (zero_based // 3) + 1

    @staticmethod
    def _coordinates_to_position(position_x: int, position_y: int) -> int:
        return (position_y - 1) * 3 + position_x

    @classmethod
    def _build_board(
        cls,
        moves: Sequence[Move],
        player_x_id: str,
        player_o_id: str | None,
    ) -> list[str | None]:
        board: list[str | None] = [None] * 9
        for move in moves:
            position = cls._coordinates_to_position(move.positionx, move.positiony)
            if move.player_id == player_x_id:
                board[position - 1] = "X"
            elif player_o_id is not None and move.player_id == player_o_id:
                board[position - 1] = "O"
        return board

    @staticmethod
    def _has_winning_line(board: Sequence[str | None], symbol: str) -> bool:
        lines = (
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        )
        return any(all(board[index] == symbol for index in line) for line in lines)

    @staticmethod
    def _current_player_user_name(game: Game) -> str | None:
        if game.current_player == 1:
            return game.player_x_id
        if game.current_player == 2:
            return game.player_o_id
        return None
