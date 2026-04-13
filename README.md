# ЖД-компания, билет №7 (RomanovSV)

FastAPI + PostgreSQL + React (Vite). Вход: номер билета + серия паспорта → JWT.

**Ветки:** `main` — без вагона; `feature/wagon-RomanovSV` — в ответе места есть `wagon_number`.

**Локально / Docker**

```bash
docker compose up --build
```

Фронт по умолчанию порт 80, иначе `FRONTEND_PORT=8080`. Prod: `docker-compose.prod.yml`.

**API:** `GET /api/departures`, `POST /api/auth/login`, `GET /api/me/seat` (Bearer).

**TeamCity:** `docker compose -f docker-compose.teamcity.yml up -d`
