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

**Проверка без TeamCity (как на агенте):** из корня `railway-app` выполнить `bash ci/verify_all_RomanovSV.sh` — прогоняет тот же pipeline, что Feature + сборка образов main. Сам сервер TC здесь не поднимается; если REST не пускает, попробуйте `TC_URL=http://хост:8111/httpAuth`.

**Docker Hub:** `romanovsv2/exam:backend` и `romanovsv2/exam:frontend`. Локально: `export EXAM_IMAGE=romanovsv2/exam`, `docker login`, затем `ci/docker_build_main_RomanovSV.sh` и `ci/docker_push_main_RomanovSV.sh`.

**TeamCity:** шаги — **Command Line** (`simpleRunner`), вызывают `ci/tc_*` и `ci/docker_*`. Обновить шаги (с любой машины с Python, где доступен REST сервера):

`TC_URL=http://ВАШ_ХОСТ:8111 TC_USER=… TC_PASSWORD=… python3 teamcity/seed_python_build_steps_RomanovSV.py`

Скрипт в конце печатает `type='simpleRunner'` по каждому шагу. **Если в логе сборки шаг подписан «(Python)» и ошибка `Python executable key must be not empty`** — для **Feature** сначала выполните (самый надёжный вариант — один шаг Command Line):

`TC_URL=http://ВАШ_ХОСТ:8111 TC_USER=… TC_PASSWORD=… python3 teamcity/fix_feature_build_RomanovSV.py`

Затем перезапустите сборку; в логе должен быть шаг **`Feature_pipeline_RomanovSV (Command Line)`**. Иначе общий сидер: `teamcity/seed_python_build_steps_RomanovSV.py` (Feature теперь тоже один pipeline-шаг).

Параметры Hub: `python3 teamcity/apply_dockerhub_teamcity_RomanovSV.py`. В проекте: `env.EXAM_IMAGE`, `env.DOCKERHUB_USER`, `env.DOCKERHUB_PASSWORD` (обязательно для push).

**Если feature-ветка не собирается:** в Git VCS root должна быть **Branch specification** (например `+:refs/heads/feature/*`), иначе TeamCity не видит ветки кроме default. Автонастройка: `TC_USER=… TC_PASSWORD=… python3 teamcity/configure_branches_RomanovSV.py` (ветки + фильтры Main/Feature + VCS trigger). Для **Run** у Feature-сборки выберите ветку `feature/...` в списке.

**Пустой Docker Hub:** образы пушит только конфигурация **Main** (`MainProdRomanovSV`), не Feature. Нужна успешная сборка **main** и заданный **`env.DOCKERHUB_PASSWORD`** (токен с правом push). Локально: `docker login` и скрипты `ci/docker_build_main_RomanovSV.sh` + `ci/docker_push_main_RomanovSV.sh`.
