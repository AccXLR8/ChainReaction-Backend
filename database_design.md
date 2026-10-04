# Database Design

This document captures the authoritative schema managed by Alembic. Every deployment runs `alembic upgrade head` automatically on startup so the database stays in sync.

---

## Global conventions

- **UUIDs** identify games and users. PostgreSQL’s native `uuid` type is used throughout.
- **Timestamps** are stored as `TIMESTAMP WITH TIME ZONE` and default to `NOW()` when possible.
- **Enums**: `GameStatus` persists as a PostgreSQL enum (`gamestatus`).
- **Cascade deletes**: participants, moves, and events cascade when a game is removed.

---

## Tables

### 1. `users`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | Unique identifier for the player/bot. |
| `username` | `varchar(64)` | Unique, not null | Display name shown to opponents. |
| `created_at` | `timestamptz` | default `now()` | Creation timestamp. |
| `updated_at` | `timestamptz` | default `now()` | Last update timestamp (updated via SQLAlchemy). |

### 2. `games`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | Game identifier. |
| `status` | `gamestatus enum` | default `WAITING` | Lifecycle state (waiting, ready, active, finished, etc.). |
| `player_1_id` | `uuid` | FK → `users.id` | Slot 0 occupant (nullable while waiting). |
| `player_2_id` | `uuid` | FK → `users.id` | Slot 1 occupant (nullable while waiting). |
| `winner_id` | `uuid` | FK → `users.id` | Winner when finished (nullable). |
| `loser_id` | `uuid` | FK → `users.id` | Loser when finished (nullable). |
| `board_width` | `int` | default 8 | Board columns. |
| `board_height` | `int` | default 8 | Board rows. |
| `initial_clock_ms` | `int` | default 300000 | Starting time per player. |
| `turn_number` | `int` | default 0 | Number of turns processed. |
| `current_player_slot` | `int` | null | Slot expected to move next. |
| `started_at` | `timestamptz` | null | When both players joined. |
| `finished_at` | `timestamptz` | null | Completion timestamp. |
| `finish_reason` | `varchar(32)` | null | Reason (matches `FinishReason`). |
| `created_at` | `timestamptz` | default `now()` | Creation timestamp. |
| `updated_at` | `timestamptz` | default `now()` | Updated automatically. |
| `latest_state` | `jsonb` | nullable | Serialized Chain Reaction engine snapshot. |

### 3. `game_participants`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `serial` | PK | Participant row id. |
| `game_id` | `uuid` | FK → `games.id` (cascade) | Owning game. |
| `user_id` | `uuid` | FK → `users.id` (cascade) | Player reference. |
| `player_slot` | `int` | not null, unique with `game_id` | Slot index (0 or 1). |
| `remaining_time_ms` | `int` | not null | Last known clock value for this participant. |
| `connected` | `bool` | default `true` | Whether WebSocket is connected. |
| `result` | `varchar(16)` | nullable | Outcome label (e.g., win/lose). |
| `joined_at` | `timestamptz` | default `now()` | When the player joined. |

### 4. `moves`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `serial` | PK | Move row id. |
| `game_id` | `uuid` | FK → `games.id` (cascade) | Owning game. |
| `player_slot` | `int` | not null | Which slot performed the move. |
| `cell` | `int` | not null | Flattened board index (row * width + col). |
| `sequence` | `int` | unique with `game_id` | Monotonic event sequence. |
| `turn_number` | `int` | not null | Turn counter from game record. |
| `client_move_id` | `varchar(64)` | unique per game (nullable) | Client-supplied id for idempotency. |
| `reaction` | `jsonb` | nullable | Reaction timeline returned by the engine. |
| `final_state` | `jsonb` | nullable | Engine state snapshot after the move. |
| `created_at` | `timestamptz` | default `now()` | Insert time. |
| `server_timestamp` | `timestamptz` | default `now()` | Server receipt time. |
| `time_remaining_ms` | `int` | not null | Player clock after completing the move. |

### 5. `game_events`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `serial` | PK | Event row id. |
| `game_id` | `uuid` | FK → `games.id` (cascade) | Owning game. |
| `sequence` | `int` | not null | Sequence number (mirrors moves). |
| `event_type` | `varchar(32)` | not null | e.g., `move`, `state_snapshot`, etc. |
| `payload` | `jsonb` | not null | Structured event data for replay/audit. |
| `created_at` | `timestamptz` | default `now()` | Insert time. |

---

## Relationships & invariants

- `games.player_1_id` and `player_2_id` reference `users`. Participants enforce the same assignment via unique `(game_id, player_slot)`.
- Moves/events cascade on game deletion to keep storage tidy.
- Clock data lives both in `games` (current state) and `game_participants` (per-player remaining time) to simplify queries and reconnection flows.
- Sequence numbers in `moves` and `game_events` remain consistent (both increment from 1 per game).

---

## Migration strategy

- Alembic config lives at `alembic.ini`, scripts in `app/database/migrations`.
- `app/database/migrations_runner.py` runs `alembic upgrade head` during FastAPI startup, ensuring schemas are created automatically when the service first connects to an externally managed database.
- Future schema changes should be generated with `alembic revision --autogenerate -m "<message>"` and committed alongside code changes.
