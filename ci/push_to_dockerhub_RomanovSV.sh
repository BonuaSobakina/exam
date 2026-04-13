#!/usr/bin/env bash
set -euo pipefail
# Сборка + push в romanovsv2/exam:backend и :frontend.
# Нужен Docker Hub PAT с правами Read & Write (не только Read).
#
# Вариант 1 — токен в окружении:
#   export DOCKERHUB_USER=romanovsv2
#   export DOCKERHUB_PASSWORD=dckr_pat_...
#   bash ci/push_to_dockerhub_RomanovSV.sh
#
# Вариант 2 — уже залогинены (docker login) с Write-токеном:
#   bash ci/push_to_dockerhub_RomanovSV.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
bash ci/docker_build_main_RomanovSV.sh
# Снять флаги TeamCity и обязательный пароль на агенте — локальный запуск
env -u TEAMCITY_VERSION -u SKIP_DOCKER_PUSH bash ci/docker_push_main_RomanovSV.sh
