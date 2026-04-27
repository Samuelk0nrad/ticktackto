import os

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api import _app as app_module


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    db_file = Path(tmp_path, "test_api.db")
    config_file = Path(tmp_path, "config.json")
    config_file.write_text(json.dumps({"connection_string": f"sqlite:///{db_file}"}), encoding="utf-8")

    app_module._app = None

    os.environ["TICTACTOE_CONFIG_FILE"] = str(config_file)

    app = app_module.build_app()
    return TestClient(app)


def register_and_login(client: TestClient, user_name: str, password: str) -> str:
    register_response = client.post(
        "/auth/register",
        json={
            "user_name": user_name,
            "password": password,
            "name": user_name,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/token",
        json={"user_name": user_name, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_requires_authentication(client: TestClient) -> None:
    response = client.get("/games")
    assert response.status_code == 401


def test_create_list_get_and_move_game(client: TestClient) -> None:
    token_a = register_and_login(client, "user1", "secret123")
    token_b = register_and_login(client, "user2", "secret123")

    create_response = client.post(
        "/games",
        json={"opponent_user_name": "user2"},
        headers=auth_header(token_a),
    )
    assert create_response.status_code == 201
    created_game = create_response.json()
    assert created_game["player_x_id"] == "user1"
    assert created_game["player_o_id"] == "user2"

    game_id = created_game["id"]

    list_response = client.get("/games", headers=auth_header(token_a))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    details_response = client.get(f"/games/{game_id}", headers=auth_header(token_a))
    assert details_response.status_code == 200

    move_x = client.put(f"/games/{game_id}/move/1", headers=auth_header(token_a))
    assert move_x.status_code == 200

    move_o = client.put(f"/games/{game_id}/move/5", headers=auth_header(token_b))
    assert move_o.status_code == 200


def test_invalid_move_and_turn_handling(client: TestClient) -> None:
    token_a = register_and_login(client, "user1", "secret123")
    token_b = register_and_login(client, "user2", "secret123")

    create_response = client.post(
        "/games",
        json={"opponent_user_name": "user2"},
        headers=auth_header(token_a),
    )
    assert create_response.status_code == 201
    game_id = create_response.json()["id"]

    wrong_turn = client.put(f"/games/{game_id}/move/1", headers=auth_header(token_b))
    assert wrong_turn.status_code == 403

    valid_move = client.put(f"/games/{game_id}/move/1", headers=auth_header(token_a))
    assert valid_move.status_code == 200

    occupied_position = client.put(f"/games/{game_id}/move/1", headers=auth_header(token_b))
    assert occupied_position.status_code == 400
    assert occupied_position.json()["detail"] == "Position already taken"

    out_of_bounds = client.put(f"/games/{game_id}/move/10", headers=auth_header(token_b))
    assert out_of_bounds.status_code == 400


def test_win_and_delete_completed_game(client: TestClient) -> None:
    token_a = register_and_login(client, "eve", "secret123")
    token_b = register_and_login(client, "frank", "secret123")

    create_response = client.post(
        "/games",
        json={"opponent_user_name": "frank"},
        headers=auth_header(token_a),
    )
    game_id = create_response.json()["id"]

    # X wins with top row: 1,2,3
    assert client.put(f"/games/{game_id}/move/1", headers=auth_header(token_a)).status_code == 200
    assert client.put(f"/games/{game_id}/move/4", headers=auth_header(token_b)).status_code == 200
    assert client.put(f"/games/{game_id}/move/2", headers=auth_header(token_a)).status_code == 200
    assert client.put(f"/games/{game_id}/move/5", headers=auth_header(token_b)).status_code == 200

    final_move = client.put(f"/games/{game_id}/move/3", headers=auth_header(token_a))
    assert final_move.status_code == 200
    payload = final_move.json()["game"]
    assert payload["status"] == "finished"
    assert payload["winner_id"] == "eve"

    delete_response = client.delete(f"/games/{game_id}", headers=auth_header(token_a))
    assert delete_response.status_code == 204

    get_deleted = client.get(f"/games/{game_id}", headers=auth_header(token_a))
    assert get_deleted.status_code == 404
