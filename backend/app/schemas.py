from pydantic import BaseModel, Field


class DepartureOut(BaseModel):
    train_number: int
    departure_station: str
    arrival_station: str
    departure_time: str
    arrival_time: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    ticket_number: str = Field(..., min_length=1, max_length=64)
    passport_series: str = Field(..., min_length=1, max_length=32)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SeatOut(BaseModel):
    ticket_number: str
    full_name: str
    train_number: int
    seat_number: int

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
