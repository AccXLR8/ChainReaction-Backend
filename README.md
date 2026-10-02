# Chain Reaction FastAPI Backend

This backend exposes HTTP and WebSocket APIs for the two-player Chain Reaction engine. It orchestrates matchmaking, clocks, persistence, and communication with the authoritative Rust engine.

## Features

- FastAPI application with modular routers
- Health, game, matchmaking, and user endpoints
- PyO3-powered Chain Reaction engine bindings (via the `chain_reaction` module) with a fake adapter fallback for tests
- Secure JWT authentication that protects HTTP + WebSocket traffic
- SQLAlchemy models for users, games, participants, moves, and events backed by Postgres
- Redis integration for matchmaking queues and distributed locks
- Azure Blob storage abstraction for replays
- Request ID & structured logging middleware
- Pydantic settings loaded from `.env`
- Real-time gameplay orchestration over WebSockets with persisted moves and clock state
- Dockerfile & pyproject

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

## Engine bindings

The backend loads the PyO3 module named by `ENGINE_MODULE` (defaults to `chain_reaction`). Build/install it with `maturin develop` from the `python-bindings` crate so the FastAPI app can import `chain_reaction` and call `new_game`/`apply_move`. If the module cannot be imported the service falls back to the deterministic fake adapter, so be sure to install the real engine in production.

## WebSocket gameplay flow

- Clients connect to `ws://<host>/ws/games/{game_id}?token=<JWT>` (or supply `Authorization: Bearer <JWT>`).
- The server authenticates the token, verifies the caller is a participant, and sends `connection_ack` + a `state_snapshot` payload.
- Supported client messages today: `ping`, `join_game` (request a fresh snapshot), and `move` (`{"cell": int, "client_move_id": str | null}`).
- Accepted moves persist inside Postgres, advance the authoritative engine state, and trigger broadcast messages: `move_accepted`, `state_snapshot`, and `game_finished` when applicable. Validation errors are returned as `move_rejected` with structured reasons.

## Environment Variables

See `.env.example` for required configuration: database, Redis, Azure storage, engine module, etc.

## Development Notes

- The rust engine binding is injected via `ENGINE_MODULE`. Implement a PyO3 wrapper exporting `apply_move` and update the adapter.
- Use Alembic to generate migrations for the SQLAlchemy models located in `app/database/models.py`.
- Redis keys are centralized under `app/redis/keys.py`.

## Architecture Overview

See `ARCHITECTURE.md` for component responsibilities, data flow, and deployment considerations.
