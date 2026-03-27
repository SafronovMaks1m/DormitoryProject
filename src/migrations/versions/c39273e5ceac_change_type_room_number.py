"""Change type room_number

Revision ID: c39273e5ceac
Revises: 63e77034b964
Create Date: 2026-03-24 21:57:59.386582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c39273e5ceac'
down_revision: Union[str, Sequence[str], None] = '63e77034b964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'users',
        'room_number',
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="room_number::integer"  # <- вот это добавили
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'users',
        'room_number',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="room_number::varchar"
    )