# TeamCity — конфигурации RomanovSV

После запуска [docker-compose.teamcity.yml](../docker-compose.teamcity.yml) откройте `http://<хост>:8111`, пройдите мастер, создайте проект из Git.

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
