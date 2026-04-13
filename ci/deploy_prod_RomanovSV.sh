#!/usr/bin/env bash
set -euo pipefail
# Run on prod host: directory must contain docker-compose.prod.yml and .env with JWT_SECRET.
: "${DEPLOY_DIR:?Set DEPLOY_DIR}"
: "${DOCKERHUB_USER:?Set DOCKERHUB_USER}"
: "${IMAGE_TAG:=latest}"
cd "$DEPLOY_DIR"
export DOCKERHUB_USER IMAGE_TAG
export JWT_SECRET="${JWT_SECRET:?Set JWT_SECRET}"
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
