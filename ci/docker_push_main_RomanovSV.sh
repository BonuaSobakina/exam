#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
: "${DOCKERHUB_USER:?Set DOCKERHUB_USER}"
: "${IMAGE_TAG:=latest}"
docker push "${DOCKERHUB_USER}/railway_backend_romanovsv:${IMAGE_TAG}"
docker push "${DOCKERHUB_USER}/railway_frontend_romanovsv:${IMAGE_TAG}"
