import { useEffect, useMemo, useState } from "react";

const TOKEN_KEY = "ticktacktoe_token";
const USER_KEY = "ticktacktoe_user";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");
  const [currentUser, setCurrentUser] = useState(() => localStorage.getItem(USER_KEY) || "");
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({
    user_name: "",
    password: "",
    name: "",
    first_name: ""
  });
  const [games, setGames] = useState([]);
  const [selectedGameId, setSelectedGameId] = useState(null);
  const [opponentName, setOpponentName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedGame = useMemo(
    () => games.find((game) => game.id === selectedGameId) || games[0] || null,
    [games, selectedGameId]
  );

  useEffect(() => {
    if (token) {
      loadGames(token);
    }
  }, [token]);

  async function request(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(path, {
      ...options,
      headers
    });

    if (response.status === 204) {
      return null;
    }

    const text = await response.text();
    const payload = text ? tryParseJson(text) : null;
    if (!response.ok) {
      if (response.status === 401 && !path.startsWith("/auth")) {
        clearSession("Session expired. Please sign in again.");
      }
      throw new Error(payload?.detail || text || "Request failed");
    }
    return payload;
  }

  async function handleAuth(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const payload =
        authMode === "register"
          ? {
            user_name: authForm.user_name,
            password: authForm.password,
            name: authForm.name || authForm.user_name,
            first_name: authForm.first_name || null
          }
          : {
            user_name: authForm.user_name,
            password: authForm.password
          };

      const result = await request(authMode === "register" ? "/auth/register" : "/auth/token", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      localStorage.setItem(TOKEN_KEY, result.access_token);
      localStorage.setItem(USER_KEY, authForm.user_name);
      setToken(result.access_token);
      setCurrentUser(authForm.user_name);
      setMessage(authMode === "register" ? "Account created." : "Signed in.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadGames(activeToken = token) {
    if (!activeToken) {
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const response = await fetch("/games", {
        headers: {
          Authorization: `Bearer ${activeToken}`
        }
      });
      const text = await response.text();
      const payload = text ? tryParseJson(text) : null;
      if (!response.ok) {
        if (response.status === 401) {
          clearSession("Session expired. Please sign in again.");
          return;
        }
        throw new Error(payload?.detail || text || "Could not load games");
      }
      setGames(payload);
      setSelectedGameId((current) => current || payload[0]?.id || null);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function createGame(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const game = await request("/games", {
        method: "POST",
        body: JSON.stringify({
          opponent_user_name: opponentName.trim() || null
        })
      });
      setGames((current) => [game, ...current]);
      setSelectedGameId(game.id);
      setOpponentName("");
      setMessage("Game created.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function makeMove(position) {
    if (!selectedGame || selectedGame.board[position - 1] || !canCurrentUserMove(selectedGame, currentUser)) {
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const result = await request(`/games/${selectedGame.id}/move/${position}`, {
        method: "PUT"
      });
      setGames((current) => current.map((game) => (game.id === result.game.id ? result.game : game)));
      setMessage(result.message);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteGame(gameId) {
    setLoading(true);
    setMessage("");
    try {
      await request(`/games/${gameId}`, { method: "DELETE" });
      setGames((current) => current.filter((game) => game.id !== gameId));
      setSelectedGameId(null);
      setMessage("Game deleted.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function clearSession(nextMessage = "") {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken("");
    setCurrentUser("");
    setGames([]);
    setSelectedGameId(null);
    setMessage(nextMessage);
  }

  function logout() {
    clearSession();
    setMessage("");
  }

  return (
    <main className="app">
      <section className="shell">
        <header className="topbar">
          {token ? (
            <div className="user-box">
              <span>{currentUser}</span>
              <button className="secondary" onClick={logout} type="button">
                Sign out
              </button>
            </div>
          ) : null}
        </header>

        {!token ? (
          <AuthPanel
            authForm={authForm}
            authMode={authMode}
            loading={loading}
            message={message}
            setAuthForm={setAuthForm}
            setAuthMode={setAuthMode}
            onSubmit={handleAuth}
          />
        ) : (
          <div className="workspace">
            <aside className="sidebar">
              <form className="panel" onSubmit={createGame}>
                <h2>New game</h2>
                <label>
                  Opponent username
                  <input
                    value={opponentName}
                    onChange={(event) => setOpponentName(event.target.value)}
                    placeholder="Optional"
                  />
                </label>
                <button disabled={loading} type="submit">
                  Create game
                </button>
              </form>

              <section className="panel games-panel">
                <div className="panel-heading">
                  <h2>Games</h2>
                  <button className="secondary small" disabled={loading} onClick={() => loadGames()} type="button">
                    Refresh
                  </button>
                </div>
                <div className="game-list">
                  {games.length === 0 ? (
                    <p className="muted">No games yet.</p>
                  ) : (
                    games.map((game) => (
                      <button
                        className={game.id === selectedGame?.id ? "game-row selected" : "game-row"}
                        key={game.id}
                        onClick={() => setSelectedGameId(game.id)}
                        type="button"
                      >
                        <span>Game #{game.id}</span>
                        <strong>{formatStatus(game)}</strong>
                      </button>
                    ))
                  )}
                </div>
              </section>
            </aside>

            <section className="board-panel">
              {message ? <div className="message">{message}</div> : null}
              {selectedGame ? (
                <>
                  <GameSummary game={selectedGame} currentUser={currentUser} />
                  <div className="board" aria-label={`Game ${selectedGame.id} board`}>
                    {selectedGame.board.map((cell, index) => (
                      <button
                        aria-label={`Position ${index + 1}`}
                        className={`cell ${cell ? "filled" : ""}`}
                        disabled={loading || Boolean(cell) || !canCurrentUserMove(selectedGame, currentUser)}
                        key={`${selectedGame.id}-${index}`}
                        onClick={() => makeMove(index + 1)}
                        type="button"
                      >
                        {cell || ""}
                      </button>
                    ))}
                  </div>
                  <div className="actions">
                    <button className="secondary" disabled={loading} onClick={() => loadGames()} type="button">
                      Reload game
                    </button>
                    <button
                      className="danger"
                      disabled={loading || selectedGame.status !== "finished"}
                      onClick={() => deleteGame(selectedGame.id)}
                      type="button"
                    >
                      Delete finished game
                    </button>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h2>Create a game to start playing.</h2>
                </div>
              )}
            </section>
          </div>
        )}
      </section>
    </main>
  );
}

function AuthPanel({ authForm, authMode, loading, message, setAuthForm, setAuthMode, onSubmit }) {
  function updateField(field, value) {
    setAuthForm((current) => ({
      ...current,
      [field]: value
    }));
  }

  return (
    <form className="auth-card" onSubmit={onSubmit}>
      <div className="tabs" role="tablist">
        <button
          className={authMode === "login" ? "active" : ""}
          onClick={() => setAuthMode("login")}
          type="button"
        >
          Sign in
        </button>
        <button
          className={authMode === "register" ? "active" : ""}
          onClick={() => setAuthMode("register")}
          type="button"
        >
          Register
        </button>
      </div>

      <label>
        Username
        <input
          autoComplete="username"
          minLength={3}
          onChange={(event) => updateField("user_name", event.target.value)}
          required
          value={authForm.user_name}
        />
      </label>
      <label>
        Password
        <input
          autoComplete={authMode === "register" ? "new-password" : "current-password"}
          minLength={6}
          onChange={(event) => updateField("password", event.target.value)}
          required
          type="password"
          value={authForm.password}
        />
      </label>
      {authMode === "register" ? (
        <>
          <label>
            Name
            <input onChange={(event) => updateField("name", event.target.value)} value={authForm.name} />
          </label>
          <label>
            First name
            <input onChange={(event) => updateField("first_name", event.target.value)} value={authForm.first_name} />
          </label>
        </>
      ) : null}
      <button disabled={loading} type="submit">
        {authMode === "register" ? "Create account" : "Sign in"}
      </button>
      {message ? <div className="message">{message}</div> : null}
    </form>
  );
}

function GameSummary({ game, currentUser }) {
  const nextPlayer = game.current_player === 1 ? game.player_x_id : game.player_o_id || "Waiting for opponent";
  const userSymbol = currentUser === game.player_x_id ? "X" : currentUser === game.player_o_id ? "O" : "-";

  return (
    <div className="summary">
      <div>
        <span>Game</span>
        <strong>#{game.id}</strong>
      </div>
      <div>
        <span>You</span>
        <strong>{userSymbol}</strong>
      </div>
      <div>
        <span>Status</span>
        <strong>{formatStatus(game)}</strong>
      </div>
      <div>
        <span>Next</span>
        <strong>{isPlayableGame(game) ? nextPlayer : "-"}</strong>
      </div>
      <div>
        <span>Winner</span>
        <strong>{game.winner_id || "-"}</strong>
      </div>
    </div>
  );
}

function formatStatus(game) {
  if (game.status === "finished" && game.winner_id) {
    return `${game.winner_id} won`;
  }
  if (game.status === "finished") {
    return "Draw";
  }
  if (game.status === "in_progress") {
    return "In progress";
  }
  if (game.status === "waiting") {
    return "Waiting";
  }
  return game.status;
}

function isPlayableGame(game) {
  return game.status === "waiting" || game.status === "in_progress";
}

function canCurrentUserMove(game, currentUser) {
  if (!isPlayableGame(game)) {
    return false;
  }
  if (game.current_player === 1) {
    return currentUser === game.player_x_id;
  }
  if (game.current_player === 2) {
    return currentUser === game.player_o_id || (game.player_o_id === null && currentUser !== game.player_x_id);
  }
  return false;
}

function tryParseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export default App;
