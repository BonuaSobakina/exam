import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-for-pytest-romanovsv"
os.environ["CORS_ORIGINS"] = "http://test"

from collections.abc import AsyncGenerator
from datetime import time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app
from app.models import Schedule, Ticket

engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
async def prepare_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        session.add_all(
            [
                Schedule(
                    train_number=1,
                    departure_station="Москва, Ярославский вокзал",
                    arrival_station="Петушки",
                    departure_time=time(15, 17),
                    arrival_time=time(18, 22),
                ),
                Ticket(
                    ticket_number="1",
                    full_name="Сложнов Егор Алексеевич",
                    passport_series="4518",
                    train_number=2,
                    seat_number=15,
                    wagon_number=5,
                ),
            ]
        )
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
