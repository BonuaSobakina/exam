#!/usr/bin/env bash
set -euo pipefail
# Сборка и теги под Docker Hub: ${EXAM_IMAGE}:backend и :frontend (напр. romanovsv2/exam)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
docker compose build
docker tag "railway_backend_romanovsv:build" "${EXAM_IMAGE}:backend"
docker tag "railway_frontend_romanovsv:build" "${EXAM_IMAGE}:frontend"
