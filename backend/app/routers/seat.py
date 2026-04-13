from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.deps import get_current_ticket_id
from app.models import Ticket
from app.schemas import SeatOut

router = APIRouter(prefix="/api/me", tags=["seat"])


@router.get("/seat", response_model=SeatOut)
async def my_seat(
    ticket_id: Annotated[int, Depends(get_current_ticket_id)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SeatOut:
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one()
    return SeatOut(
        ticket_number=ticket.ticket_number,
        full_name=ticket.full_name,
        train_number=ticket.train_number,
        seat_number=ticket.seat_number,
        wagon_number=ticket.wagon_number,
    )
