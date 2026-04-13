import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_departures_public(client: AsyncClient) -> None:
    r = await client.get("/api/departures")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["train_number"] == 1


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient) -> None:
    r = await client.post(
        "/api/auth/login",
        json={"ticket_number": "99", "passport_series": "0000"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_and_seat(client: AsyncClient) -> None:
    r = await client.post(
        "/api/auth/login",
        json={"ticket_number": "1", "passport_series": "4518"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r2 = await client.get("/api/me/seat", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["seat_number"] == 15
    assert body["train_number"] == 2
    assert body.get("wagon_number") == 5


@pytest.mark.asyncio
async def test_seat_without_token(client: AsyncClient) -> None:
    r = await client.get("/api/me/seat")
    assert r.status_code == 401
