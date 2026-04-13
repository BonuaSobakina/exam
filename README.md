# Железнодорожная компания — экзамен, билет №7 (RomanovSV)

Монорепозиторий: **FastAPI** + **PostgreSQL** + **React (Vite)**. Аутентификация по паре «номер билета + серия паспорта», JWT.

## Запуск локально (без Docker)

1. PostgreSQL и переменные из [.env.example](.env.example) → `.env` в корне или только для backend.
2. Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://USER:PASS@localhost:5432/railway
export PYTHONPATH=.
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Frontend: `cd frontend && npm install && npm run dev` — прокси на API в [vite.config.ts](frontend/vite.config.ts).

## Docker (dev-сборка)

Из корня репозитория:

```bash
cp .env.example .env
# задайте JWT_SECRET в .env при необходимости
docker compose up --build
```

Приложение: **http://localhost** (порт задайте `FRONTEND_PORT` при конфликте с TeamCity `8111`).

## Docker Hub + prod

Сборка помечает образы именами `railway_backend_RomanovSV` и `railway_frontend_RomanovSV`. Для публикации:

```bash
export DOCKERHUB_USER=<ваш_логин>
export IMAGE_TAG=latest
bash ci/docker_build_main_RomanovSV.sh
docker login
bash ci/docker_push_main_RomanovSV.sh
```

На сервере положите [docker-compose.prod.yml](docker-compose.prod.yml) и `.env`:

```env
DOCKERHUB_USER=<логин>
IMAGE_TAG=latest
JWT_SECRET=<длинная_случайная_строка>
```

Запуск: `docker compose -f docker-compose.prod.yml up -d`.

## TeamCity

```bash
docker compose -f docker-compose.teamcity.yml up -d
```

Детали конфигураций сборки: [teamcity/README_RomanovSV.md](teamcity/README_RomanovSV.md).

## Ветки

- **`main`** — базовый функционал без поля «вагон» в ответе API.
- **`feature/wagon-RomanovSV`** — дополнение по билету: в ответе `/api/me/seat` добавляется `wagon_number`.

## CI-скрипты (RomanovSV)

| Скрипт | Назначение |
|--------|------------|
| [ci/lint_RomanovSV.sh](ci/lint_RomanovSV.sh) | ruff + eslint |
| [ci/sast_RomanovSV.sh](ci/sast_RomanovSV.sh) | bandit |
| [ci/test_RomanovSV.sh](ci/test_RomanovSV.sh) | pytest + vitest |
| [ci/docker_build_main_RomanovSV.sh](ci/docker_build_main_RomanovSV.sh) | build + теги для Hub |
| [ci/docker_push_main_RomanovSV.sh](ci/docker_push_main_RomanovSV.sh) | push образов |
| [ci/docker_build_feature_RomanovSV.sh](ci/docker_build_feature_RomanovSV.sh) | только build |
| [ci/deploy_prod_RomanovSV.sh](ci/deploy_prod_RomanovSV.sh) | prod pull + up |

## Публичный репозиторий

После создания репозитория на GitHub/GitLab добавьте remote и вставьте ссылку в отчёт:

```bash
git remote add origin <URL>
git push -u origin main
```

## API

- `GET /api/departures` — расписание (без авторизации).
- `POST /api/auth/login` — тело `{ "ticket_number", "passport_series" }` → `access_token`.
- `GET /api/me/seat` — заголовок `Authorization: Bearer <token>`.

Тестовые данные билетов см. миграцию `backend/alembic/versions/001_initial_romanovsv.py`.
