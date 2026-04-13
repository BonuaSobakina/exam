from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Schedule
from app.schemas import DepartureOut

router = APIRouter(prefix="/api", tags=["departures"])


@router.get("/departures", response_model=list[DepartureOut])
async def list_departures(session: AsyncSession = Depends(get_session)) -> list[DepartureOut]:
    result = await session.execute(select(Schedule).order_by(Schedule.train_number))
    rows = result.scalars().all()
    return [
        DepartureOut(
            train_number=s.train_number,
            departure_station=s.departure_station,
            arrival_station=s.arrival_station,
            departure_time=s.departure_time.strftime("%H:%M"),
            arrival_time=s.arrival_time.strftime("%H:%M"),
        )
        for s in rows
    ]
