"""add admin role

Revision ID: f457989db25b
Revises: cc21db602ddc
Create Date: 2026-10-15 14:52:47.557426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f457989db25b'
down_revision: Union[str, Sequence[str], None] = 'cc21db602ddc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ADMIN'")


def downgrade() -> None:
    # Postgres cannot remove a single value from an enum type,
    # so rolling this back is intentionally a no-op.
    pass