from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_jwt import decode_token
from app.database import get_session
from app.models import Ticket

security = HTTPBearer(auto_error=False)


async def get_current_ticket_id(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> int:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен авторизации",
        )
    ticket_number = decode_token(creds.credentials)
    if not ticket_number:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
        )
    result = await session.execute(select(Ticket).where(Ticket.ticket_number == ticket_number))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Билет не найден",
        )
    return ticket.id
