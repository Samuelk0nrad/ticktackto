import pytest
from sqlalchemy.orm import Session

from backend.crud import GameCRUD
from backend.engine import get_engine
from backend.model import Entity, GameStatus, User


def _create_user(engine, user_name: str, name: str) -> None:
    with Session(engine) as session:
        entity = Entity(name=name)
        user = User(user_name=user_name, password_hash="hash", entity=entity)
        session.add(entity)
        session.add(user)
        session.commit()


def test_game_crud_create_list_get() -> None:
    engine = get_engine()
    _create_user(engine, "alice", "Alice")
    _create_user(engine, "bob", "Bob")

    crud = GameCRUD(engine)
    created = crud.create_game(creator_user_name="alice", opponent_user_name="bob")

    assert created.player_x_id == "alice"
    assert created.player_o_id == "bob"
    assert created.status == GameStatus.IN_PROGRESS.value

    listed = crud.list_games()
    assert len(listed) == 1
    assert listed[0].id == created.id

    fetched = crud.get_game(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_game_crud_create_requires_existing_creator() -> None:
    engine = get_engine()
    crud = GameCRUD(engine)

    with pytest.raises(ValueError, match="Creator user does not exist"):
        crud.create_game(creator_user_name="ghost")


def test_game_crud_waiting_game_allows_join_on_first_o_move() -> None:
    engine = get_engine()
    _create_user(engine, "alice", "Alice")
    _create_user(engine, "bob", "Bob")

    crud = GameCRUD(engine)
    game = crud.create_game(creator_user_name="alice")

    assert game.status == GameStatus.WAITING.value
    assert game.player_o_id is None

    game_after_x = crud.make_move(game.id, user_name="alice", position=1)
    assert game_after_x.current_player == 2

    with pytest.raises(ValueError, match="Second player has not joined yet"):
        crud.make_move(game.id, user_name="alice", position=2)

    game_after_o = crud.make_move(game.id, user_name="bob", position=5)
    assert game_after_o.player_o_id == "bob"
    assert game_after_o.status == GameStatus.IN_PROGRESS.value


def test_game_crud_invalid_moves() -> None:
    engine = get_engine()
    _create_user(engine, "alice", "Alice")
    _create_user(engine, "bob", "Bob")

    crud = GameCRUD(engine)
    game = crud.create_game(creator_user_name="alice", opponent_user_name="bob")

    with pytest.raises(ValueError, match="Position must be between 1 and 9"):
        crud.make_move(game.id, user_name="alice", position=0)

    with pytest.raises(PermissionError, match="It is not your turn"):
        crud.make_move(game.id, user_name="bob", position=1)

    crud.make_move(game.id, user_name="alice", position=1)

    with pytest.raises(ValueError, match="Position already taken"):
        crud.make_move(game.id, user_name="bob", position=1)


def test_game_crud_finish_and_delete() -> None:
    engine = get_engine()
    _create_user(engine, "alice", "Alice")
    _create_user(engine, "bob", "Bob")

    crud = GameCRUD(engine)
    game = crud.create_game(creator_user_name="alice", opponent_user_name="bob")

    crud.make_move(game.id, user_name="alice", position=1)
    crud.make_move(game.id, user_name="bob", position=4)
    crud.make_move(game.id, user_name="alice", position=2)
    crud.make_move(game.id, user_name="bob", position=5)
    finished = crud.make_move(game.id, user_name="alice", position=3)

    assert finished.status == GameStatus.FINISHED.value
    assert finished.winner_id == "alice"

    assert crud.delete_finished_game(game.id) is True
    assert crud.get_game(game.id) is None


def test_game_crud_delete_requires_finished_game() -> None:
    engine = get_engine()
    _create_user(engine, "alice", "Alice")
    _create_user(engine, "bob", "Bob")

    crud = GameCRUD(engine)
    game = crud.create_game(creator_user_name="alice", opponent_user_name="bob")

    with pytest.raises(ValueError, match="Only finished games can be deleted"):
        crud.delete_finished_game(game.id)
