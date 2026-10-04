# Deployment Guide

This document summarizes everything required to run the Chain Reaction backend with the PyO3 engine bindings, whether locally, in containers, or in production.

---

## 1. Prerequisites

| Requirement | Notes |
| --- | --- |
| **Python 3.11** | Only needed if you run outside Docker. |
| **Rust toolchain** | Required once to compile the PyO3 bindings. Installed automatically in the Docker image via `rustup`. |
| **Docker (optional)** | Recommended path: build the provided `Dockerfile` and run the container. |
| **PostgreSQL 14+** | All persistent game data lives here. Use `asyncpg` DSN. |
| **Redis 6+** | Matchmaking queues, distributed locks, connection metadata. |
| **Azure Blob Storage** | Needed for future replay storage (you may stub with Azurite locally). |
| **JWT issuer** | The backend trusts HS256 tokens signed with `SECRET_KEY`. |

---

## 2. Environment variables

Create a `.env` file (or set env vars in your orchestrator) containing at least:

```
APP_ENV=production
SECRET_KEY=<hs256-signing-key>
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/chainreaction
REDIS_URL=redis://redis:6379/0
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_BLOB_CONTAINER=replays
ENGINE_MODULE=chain_reaction
ALLOWED_ORIGINS=["https://your-frontend"]
```

Optional overrides: board size (`BOARD_WIDTH`, `BOARD_HEIGHT`), clock duration (`GAME_CLOCK_SECONDS`), websocket heartbeat interval, etc. See `app/config/settings.py` for the full list.

---

## 3. Engine installation

The backend loads the PyO3 bindings from the `chain_reaction` module. Two options:

1. **Docker build (recommended)** – handled automatically by the provided `Dockerfile` (installs `maturin`, clones the repo, builds the wheel).
2. **Manual install** – if running locally/CI: `pip install maturin` and then `pip install "git+https://github.com/AccXLR8/ChainReaction-Package#subdirectory=python-bindings"` inside your venv.

Ensure this runs in every environment where the backend starts.

---

## 4. Docker workflow

```bash
# Build image (override branch/commit via CHAIN_REACTION_REF if needed)
docker build \
  --build-arg CHAIN_REACTION_REF=main \
  -t chain-reaction-backend .

# Run the app, mounting env vars
docker run --env-file .env -p 8080:8080 chain-reaction-backend
```

The image installs system deps, Rust, the engine package, backend code, and starts `uvicorn app.main:app --host 0.0.0.0 --port 8080`.

---

## 5. Supporting services

Spin up Postgres + Redis before starting the backend. Example using Docker Compose snippet:

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chainreaction
      POSTGRES_USER: chainreaction
      POSTGRES_PASSWORD: chainreaction
    ports: ["5432:5432"]

  redis:
    image: redis:7
    ports: ["6379:6379"]
```

Point `DATABASE_URL` / `REDIS_URL` to those containers. For Azure Blob storage in dev, you can run Azurite and supply its connection string.

---

## 6. Database migration

Alembic migrations live under `app/database/migrations`. The FastAPI lifespan automatically runs `alembic upgrade head` on startup (see `app/database/migrations_runner.py`), so pointing the service to a new database will create/upgrade the schema instantly. For manual control or CI steps run:

```bash
alembic upgrade head  # uses alembic.ini
```

---

## 7. Health checks & endpoints

- **HTTP**: `/api/health` (liveness) and `/api/health/ready` (checks DB + Redis connections).
- **Gameplay REST**: `/api/games` (create/join/get/history, authenticated with `Authorization: Bearer <JWT>`).
- **WebSocket**: `ws://<host>/ws/games/{game_id}?token=<JWT>` for real-time play. Messages follow `ServerMessageType` / `ClientMessageType` enums in `app/websocket/protocol.py`.

---

## 8. Deployment checklist

1. Build and push the Docker image (or install deps manually).
2. Provision environment secrets + `.env` for each runtime.
3. Ensure Postgres/Redis/Azure services are reachable and credentials provided.
4. Run database migrations / schema creation.
5. Start the backend container and point your load balancer to port 8080.
6. Verify:
   - `GET /api/health` returns `{"status":"ok"}`.
   - `GET /api/health/ready` returns status `ok` with both `database` and `redis` ready.
   - Authenticated clients can connect to the WebSocket endpoint and exchange `ping`/`move` messages.

Following these steps yields a fully operational backend with authoritative engine orchestration, persisted state, and secure gameplay over WebSockets.
