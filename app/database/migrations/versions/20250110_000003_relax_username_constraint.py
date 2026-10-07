"""Allow duplicate guest usernames

Revision ID: 20250110_000003
Revises: 20250106_000002
Create Date: 2025-01-10 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250110_000003"
down_revision: Union[str, None] = "20250106_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key")
    op.create_index(
        "ix_users_username_non_guest_unique",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("is_guest = false"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_username_non_guest_unique", table_name="users")
    op.create_unique_constraint("users_username_key", "users", ["username"])
