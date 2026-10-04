"""Add password hash and guest flag to users

Revision ID: 20250106_000002
Revises: 20250106_000001
Create Date: 2025-01-06 00:30:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250106_000002"
down_revision: Union[str, None] = "20250106_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("is_guest", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE users SET is_guest = FALSE WHERE is_guest IS NULL")


def downgrade() -> None:
    op.drop_column("users", "is_guest")
    op.drop_column("users", "password_hash")
