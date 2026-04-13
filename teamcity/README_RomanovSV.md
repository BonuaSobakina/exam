# TeamCity — конфигурации RomanovSV

После запуска [docker-compose.teamcity.yml](../docker-compose.teamcity.yml) откройте `http://<хост>:8111`, пройдите мастер.

## Уже создано через REST API (на этом стенде)

- **Проект:** `RailwayExamRomanovSV` (id: `RailwayExamRomanovSV`)
- **VCS roots:** `Git_Main_RomanovSV` (ветка `main`), `Git_Feature_RomanovSV` (маски `feature/*`, `fix/*`)
- **Сборки:** `Main_Prod_RomanovSV`, `Feature_Build_RomanovSV`
- **Триггер:** VCS trigger на обеих конфигурациях
- **Шаги:** Command Line + **Docker** (`python:3.12-bookworm`, `node:22-bookworm`) — линтеры, bandit, тесты, `docker compose build`; у main ещё push и deploy

Повторное создание с другой машины (после задания `TC_USER` / `TC_PASSWORD`):

```bash
export TC_URL=http://127.0.0.1:8111
export TC_USER=RomanovSV
export TC_PASSWORD='<пароль>'
export TC_GIT_URL='https://github.com/<you>/<repo>.git'   # опционально
python3 teamcity/bootstrap_tc_RomanovSV.py
```

Шаги сборки на другом сервере можно скопировать вручную из UI или донастроить скриптом.

### Что сделать вручную в UI

1. **Агент:** *Agents* → разрешить/авторизовать `agent_RomanovSV` (после первого коннекта).
2. **URL Git:** *Project Settings → VCS Roots* — укажи **реальный** публичный URL репозитория (сейчас шаблон `https://github.com/RomanovSV/railway-app-RomanovSV.git`).
3. **Docker Hub:** *Parameters* проекта — `env.DOCKERHUB_USER`, **`env.DOCKERHUB_PASSWORD`** (замени placeholder на настоящий пароль/токен), при необходимости `env.IMAGE_TAG`, `env.JWT_SECRET`, `env.DEPLOY_DIR`.
4. Запусти сборку *Run* на `Main_Prod_RomanovSV` после пуша в `main`.

## Имена (требование экзамена)

- Проект: например `RailwayExam_RomanovSV`.
- **Build configuration «main + prod»:** `Main_Prod_RomanovSV`.
- **Build configuration «feature»:** `Feature_Build_RomanovSV`.

## Общие шаги (обе конфигурации)

Используйте **Command Line** build steps с рабочей директорией `%teamcity.build.checkoutDir%` (или корень репозитория).

1. **Lint_RomanovSV** — установка зависимостей и линтеры:
   - Backend: `pip install -r backend/requirements.txt && bash ci/lint_backend_RomanovSV.sh` (или `PYTHONPATH=backend python -m ruff check backend/app`)
   - Frontend: `cd frontend && npm ci && npm run lint`
   - Либо одной командой: `bash ci/lint_RomanovSV.sh` (нужен `npm` и `npm install`/`npm ci` во frontend).
2. **SAST_RomanovSV** — `pip install -r backend/requirements.txt && cd backend && python -m bandit -r app`
3. **Test_RomanovSV** — `pip install -r backend/requirements.txt && cd backend && PYTHONPATH=. pytest -q && cd ../frontend && npm ci && npm run test`

Либо вызов скриптов из [ci/](../ci/) (предварительно `chmod +x ci/*.sh` в репозитории или `bash ci/...`).

## Main_Prod_RomanovSV

- **VCS:** ветка `main`.
- **Параметры (секреты):** `DOCKERHUB_USER`, `DOCKERHUB_PASSWORD` (password hidden), `JWT_SECRET`, при деплое по SSH — ключ или пароль.
- **Шаги после тестов:**
  4. **Docker_build_RomanovSV** — `docker compose build` и теги (см. `ci/docker_build_main_RomanovSV.sh`; задайте `DOCKERHUB_USER` и `IMAGE_TAG`).
  5. **Docker_push_RomanovSV** — `docker login` и `ci/docker_push_main_RomanovSV.sh`.
  6. **Deploy_RomanovSV** (на prod-хосте или по SSH) — скопируйте `docker-compose.prod.yml`, задайте `.env` с `JWT_SECRET`, затем `ci/deploy_prod_RomanovSV.sh` с `DEPLOY_DIR` на каталог с этими файлами.

Агент должен иметь доступ к Docker (в compose агенту смонтирован `docker.sock`).

## Feature_Build_RomanovSV

- **VCS:** фильтр веток `+:feature/*` и `+:fix/*` (или нужные маски).
- Те же шаги **Lint / SAST / Test**, затем **Docker_build_feature_RomanovSV** — только `docker compose build` (`ci/docker_build_feature_RomanovSV.sh`), **без** push и **без** deploy.

## Примечание

Образы TeamCity указаны с тегом версии; при необходимости обновите тег в `docker-compose.teamcity.yml` на актуальный с [Docker Hub JetBrains](https://hub.docker.com/r/jetbrains/teamcity-server).
