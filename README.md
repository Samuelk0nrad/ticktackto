# TicTacToe FastAPI REST API

This project provides an authenticated REST API for TicTacToe using FastAPI and SQLAlchemy.

## Features

- User registration and login with JWT bearer tokens
- Create and manage TicTacToe games
- Make moves using board positions `1-9`
- Win detection for rows, columns, and diagonals
- Draw detection for full boards without a winner
- Clear error handling for invalid moves and invalid turns
- OpenAPI docs via Swagger UI

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- PostgreSQL-compatible SQLAlchemy setup
- JWT (`python-jose`)
- Password hashing (`passlib`, `pbkdf2_sha256`)
- pytest + FastAPI TestClient

## Project Structure

- `backend/api`: route handlers and auth utilities
- `backend/model`: SQLAlchemy models
- `backend/crud`: persistence and rule-aware DB operations
- `backend/service`: service-layer orchestration and DTO mapping
- `backend/schema`: request/response schemas
- `test/api`: API endpoint tests

## Authentication Model

- Users must authenticate to access game endpoints.
- Register with `POST /auth/register`.
- Log in with `POST /auth/token` to receive an `access_token`.
- Send bearer token in header:

```http
Authorization: Bearer <token>
```

## Game State Rules

- Board positions map as:

```text
1 | 2 | 3
4 | 5 | 6
7 | 8 | 9
```

- Player X is the game creator.
- Optional opponent can be set at creation time.
- If no opponent is set, the first different user who plays joins as player O.
- Invalid operations return clear HTTP errors, for example:
	- `Position must be between 1 and 9`
	- `Position already taken`
	- `It is not your turn`

## API Endpoints

### Auth

- `POST /auth/register`: Create a user and receive a token.
- `POST /auth/token`: Authenticate and receive a token.

### Games

- `POST /games`: Create a new game.
- `GET /games`: List all games, including move history and status.
- `PUT /games/{game_id}/move/{position}`: Make a move at position `1-9`.
- `GET /games/{game_id}`: Get full game details.
- `DELETE /games/{game_id}`: Delete a finished game.

## Local Development

Install dependencies in your environment and run the API:

```bash
TICTACTOE_CONFIG_FILE=local_sqlite_config.json uv run uvicorn backend.main:app
```

```bash
$env:TICTACTOE_CONFIG_FILE="local_sqlite_config.json"; uv run uvicorn backend.main:app
```
Open docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Testing

Run tests:

```bash
python -m pytest -q
```

Current status: `20 passed`.

## Notes

- Database connection is loaded via `backend.config.Config`.
- Default connection is in-memory SQLite, and you can provide a config file with a custom connection string.
