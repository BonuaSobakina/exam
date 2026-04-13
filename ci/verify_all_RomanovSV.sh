#!/usr/bin/env bash
# Всё то же, что делает TeamCity локально (без UI TC). Запуск из корня репозитория.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "=== Feature pipeline (lint, sast, test, docker compose build) ==="
bash ci/tc_feature_pipeline_RomanovSV.sh
echo "=== Main: compose build + теги Hub ==="
EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}" bash ci/docker_build_main_RomanovSV.sh
echo "=== OK: локальная проверка как в TeamCity пройдена ==="
