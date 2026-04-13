#!/usr/bin/env bash
set -euo pipefail
if [[ -z "${DEPLOY_DIR:-}" ]]; then
  echo "Deploy_prod_RomanovSV: DEPLOY_DIR unset, skipping."
  exit 0
fi
: "${JWT_SECRET:?Set JWT_SECRET when deploying}"
export EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
cd "$DEPLOY_DIR"
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
