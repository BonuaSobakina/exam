from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    departure_station: Mapped[str] = mapped_column(String(255), nullable=False)
    arrival_station: Mapped[str] = mapped_column(String(255), nullable=False)
    departure_time: Mapped[object] = mapped_column(Time, nullable=False)
    arrival_time: Mapped[object] = mapped_column(Time, nullable=False)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)
    passport_series: Mapped[str] = mapped_column(String(32), nullable=False)
    train_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
