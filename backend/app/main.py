from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, departures, seat

app = FastAPI(title="Railway RomanovSV", version="1.0.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departures.router)
app.include_router(auth.router)
app.include_router(seat.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
