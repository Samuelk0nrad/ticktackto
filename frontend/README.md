# Tic Tac Toe Frontend

React frontend for the FastAPI Tic Tac Toe backend.

## Run locally

Start the backend from the repository root:

```bash
uvicorn backend.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/auth`, `/games`, and `/health` to `http://127.0.0.1:8000`.
