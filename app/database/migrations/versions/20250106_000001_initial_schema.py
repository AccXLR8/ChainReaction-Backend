"""Initial schema

Revision ID: 20250106_000001
Revises: 
Create Date: 2025-01-06 00:00:01.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250106_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


GAME_STATUS_ENUM = sa.Enum(
    "WAITING",
    "READY",
    "ACTIVE",
    "FINISHED",
    "ABANDONED",
    "EXPIRED",
    "CANCELLED",
    name="gamestatus",
)


def upgrade() -> None:
    GAME_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "games",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("status", GAME_STATUS_ENUM, nullable=False, server_default="WAITING"),
        sa.Column("player_1_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("player_2_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("winner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("loser_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("board_width", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("board_height", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("initial_clock_ms", sa.Integer(), nullable=False, server_default="300000"),
        sa.Column("turn_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_player_slot", sa.Integer()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("finish_reason", sa.String(length=32)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("latest_state", sa.JSON(), nullable=True),
    )

    op.create_table(
        "game_participants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_slot", sa.Integer(), nullable=False),
        sa.Column("remaining_time_ms", sa.Integer(), nullable=False),
        sa.Column("connected", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("result", sa.String(length=16)),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("game_id", "player_slot", name="uq_participant_game_slot"),
    )

    op.create_table(
        "moves",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_slot", sa.Integer(), nullable=False),
        sa.Column("cell", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("client_move_id", sa.String(length=64)),
        sa.Column("reaction", sa.JSON()),
        sa.Column("final_state", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("server_timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("time_remaining_ms", sa.Integer(), nullable=False),
        sa.UniqueConstraint("game_id", "sequence", name="uq_moves_game_sequence"),
        sa.Index("ix_moves_game_client", "game_id", "client_move_id", unique=True, postgresql_where=sa.text("client_move_id IS NOT NULL")),
    )

    op.create_table(
        "game_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("game_events")
    op.drop_table("moves")
    op.drop_table("game_participants")
    op.drop_table("games")
    op.drop_table("users")
    GAME_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
