#!/usr/bin/env bash
set -euo pipefail
# Зелёный Main без деплоя: env.SKIP_DEPLOY_PROD=true (например нет каталога на агенте).
if [[ "${SKIP_DEPLOY_PROD:-}" == "true" ]]; then
  echo "SKIP_DEPLOY_PROD=true — шаг deploy пропущен." >&2
  exit 0
fi
if [[ -z "${DEPLOY_DIR:-}" ]]; then
  echo "Deploy_prod_RomanovSV: DEPLOY_DIR unset, skipping."
  exit 0
fi
if [[ ! -d "$DEPLOY_DIR" ]]; then
  echo "Deploy_prod_RomanovSV: каталога нет на агенте ($DEPLOY_DIR), пропуск deploy." >&2
  exit 0
fi
: "${JWT_SECRET:?Set JWT_SECRET when deploying}"
export EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
cd "$DEPLOY_DIR"
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
