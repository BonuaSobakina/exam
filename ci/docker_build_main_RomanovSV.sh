#!/usr/bin/env bash
set -euo pipefail
# Build step for main branch — images tagged for Docker Hub push + deploy.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
: "${DOCKERHUB_USER:?Set DOCKERHUB_USER}"
: "${IMAGE_TAG:=latest}"
docker compose build
docker tag "railway_backend_romanovsv:build" "${DOCKERHUB_USER}/railway_backend_romanovsv:${IMAGE_TAG}"
docker tag "railway_frontend_romanovsv:build" "${DOCKERHUB_USER}/railway_frontend_romanovsv:${IMAGE_TAG}"
