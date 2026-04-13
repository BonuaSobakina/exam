#!/usr/bin/env bash
set -euo pipefail
EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
PW="${DOCKERHUB_PASSWORD:-}"
if [[ -n "$PW" && "$PW" != "REPLACE_IN_TEAMCITY_UI" ]]; then
  : "${DOCKERHUB_USER:?Set DOCKERHUB_USER when DOCKERHUB_PASSWORD is set}"
  echo "$PW" | docker login -u "$DOCKERHUB_USER" --password-stdin
fi
docker push "${EXAM_IMAGE}:backend"
docker push "${EXAM_IMAGE}:frontend"
