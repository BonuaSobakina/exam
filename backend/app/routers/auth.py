from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_jwt import create_access_token
from app.database import get_session
from app.models import Ticket
from app.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)) -> LoginResponse:
    result = await session.execute(
        select(Ticket).where(
            Ticket.ticket_number == body.ticket_number.strip(),
            Ticket.passport_series == body.passport_series.strip(),
        )
    )
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная пара: номер билета и серия паспорта не найдены",
        )
    token = create_access_token(ticket.ticket_number)
    return LoginResponse(access_token=token)
