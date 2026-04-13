#!/usr/bin/env bash
set -euo pipefail
EXAM_IMAGE="${EXAM_IMAGE:-romanovsv2/exam}"
# Временно зелёный Main без push (например токен Hub только Read): env.SKIP_DOCKER_PUSH=true в TeamCity.
if [[ "${SKIP_DOCKER_PUSH:-}" == "true" ]]; then
  echo "SKIP_DOCKER_PUSH=true — push в Hub пропущен (соберите Write-токен и снимите флаг)." >&2
  exit 0
fi
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
    echo >&2 "Push отклонён для $tag. Если выше было «insufficient scopes» — PAT только Read; нужен токен с Read & Write."
    echo >&2 "Временный обход: в TeamCity env.SKIP_DOCKER_PUSH=true (зелёная сборка без push)."
    echo >&2 "Hub: Account Settings → Security → New Access Token; TC: env.DOCKERHUB_USER + env.DOCKERHUB_PASSWORD."
    exit 1
  fi
}
push_one "${EXAM_IMAGE}:backend"
push_one "${EXAM_IMAGE}:frontend"
