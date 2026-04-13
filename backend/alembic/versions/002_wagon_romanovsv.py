"""add wagon_number to tickets RomanovSV

Revision ID: 002
Revises: 001
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("wagon_number", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE tickets SET wagon_number = 5 WHERE ticket_number = '1'"))
    op.execute(sa.text("UPDATE tickets SET wagon_number = 3 WHERE ticket_number = '2'"))
    op.execute(sa.text("UPDATE tickets SET wagon_number = 7 WHERE ticket_number = '3'"))
    op.alter_column("tickets", "wagon_number", nullable=False)


def downgrade() -> None:
    op.drop_column("tickets", "wagon_number")
