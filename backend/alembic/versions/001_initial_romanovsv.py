"""initial schedules and tickets RomanovSV

Revision ID: 001
Revises:
Create Date: 2026-04-13

"""

from datetime import time
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("train_number", sa.Integer(), nullable=False),
        sa.Column("departure_station", sa.String(length=255), nullable=False),
        sa.Column("arrival_station", sa.String(length=255), nullable=False),
        sa.Column("departure_time", sa.Time(), nullable=False),
        sa.Column("arrival_time", sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("train_number"),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_number", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("passport_series", sa.String(length=32), nullable=False),
        sa.Column("train_number", sa.Integer(), nullable=False),
        sa.Column("seat_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_number"),
    )

    schedules = sa.table(
        "schedules",
        sa.column("train_number", sa.Integer),
        sa.column("departure_station", sa.String),
        sa.column("arrival_station", sa.String),
        sa.column("departure_time", sa.Time),
        sa.column("arrival_time", sa.Time),
    )
    op.bulk_insert(
        schedules,
        [
            {
                "train_number": 1,
                "departure_station": "Москва, Ярославский вокзал",
                "arrival_station": "Петушки",
                "departure_time": time(15, 17),
                "arrival_time": time(18, 22),
            },
            {
                "train_number": 2,
                "departure_station": "Москва, Ленинградский вокзал",
                "arrival_station": "Санкт-Петербург",
                "departure_time": time(15, 30),
                "arrival_time": time(20, 15),
            },
            {
                "train_number": 3,
                "departure_station": "Ярославль",
                "arrival_station": "Москва, Ярославский вокзал",
                "departure_time": time(16, 10),
                "arrival_time": time(20, 10),
            },
            {
                "train_number": 4,
                "departure_station": "Подольск",
                "arrival_station": "Нахабино",
                "departure_time": time(19, 2),
                "arrival_time": time(21, 12),
            },
        ],
    )

    tickets = sa.table(
        "tickets",
        sa.column("ticket_number", sa.String),
        sa.column("full_name", sa.String),
        sa.column("passport_series", sa.String),
        sa.column("train_number", sa.Integer),
        sa.column("seat_number", sa.Integer),
    )
    op.bulk_insert(
        tickets,
        [
            {
                "ticket_number": "1",
                "full_name": "Сложнов Егор Алексеевич",
                "passport_series": "4518",
                "train_number": 2,
                "seat_number": 15,
            },
            {
                "ticket_number": "2",
                "full_name": "Панченков Илья Сергеевич",
                "passport_series": "3917",
                "train_number": 1,
                "seat_number": 13,
            },
            {
                "ticket_number": "3",
                "full_name": "Венедикт Васильевич Ерофеев",
                "passport_series": "3879",
                "train_number": 1,
                "seat_number": 11,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("tickets")
    op.drop_table("schedules")
