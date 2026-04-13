#!/usr/bin/env bash
set -euo pipefail
EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
PW="${DOCKERHUB_PASSWORD:-}"
# В TeamCity без логина Hub всегда будет denied на push.
if [[ -n "${TEAMCITY_VERSION:-}" ]]; then
  if [[ -z "$PW" || "$PW" == "REPLACE_IN_TEAMCITY_UI" ]]; then
    echo "TeamCity: задайте в проекте секретный параметр env.DOCKERHUB_PASSWORD (Access Token Docker Hub)." >&2
    echo "Также должен быть env.DOCKERHUB_USER (например romanovsv2). Без этого push в ${EXAM_IMAGE} невозможен." >&2
    exit 1
  fi
fi
if [[ -n "$PW" && "$PW" != "REPLACE_IN_TEAMCITY_UI" ]]; then
  : "${DOCKERHUB_USER:?Set DOCKERHUB_USER when DOCKERHUB_PASSWORD is set}"
  # printf: корректно для токенов со спецсимволами; registry явно docker.io
  if ! printf '%s\n' "$PW" | docker login docker.io -u "$DOCKERHUB_USER" --password-stdin; then
    echo "docker login docker.io не удался (проверьте env.DOCKERHUB_USER и токен в env.DOCKERHUB_PASSWORD)." >&2
    exit 1
  fi
  echo "Docker Hub: login OK для пользователя ${DOCKERHUB_USER}" >&2
fi
push_one() {
  local tag=$1
  if ! docker push "$tag"; then
    echo >&2 "Push отклонён для $tag (denied: обычно токен без Write или неверный DOCKERHUB_USER)."
    echo >&2 "В Hub: Account → Security → Access Token с правами Read/Write; пользователь = владелец репозитория ${EXAM_IMAGE%%/*}."
    echo >&2 "В TeamCity: env.DOCKERHUB_USER должен совпадать с логином Hub, под которым создан токен."
    exit 1
  fi
}
push_one "${EXAM_IMAGE}:backend"
push_one "${EXAM_IMAGE}:frontend"
