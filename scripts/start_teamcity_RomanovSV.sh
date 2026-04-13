#!/usr/bin/env bash
# Запуск TeamCity (нужны права на Docker: группа docker или sudo).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE_FILE="$ROOT/docker-compose.teamcity.yml"
COMPOSE=(docker compose -f "$COMPOSE_FILE")
if docker info &>/dev/null; then
  "${COMPOSE[@]}" up -d
elif command -v sudo &>/dev/null && sudo -n docker info &>/dev/null; then
  sudo "${COMPOSE[@]}" up -d
elif command -v pkexec &>/dev/null; then
  echo "Запрос прав через pkexec (PolicyKit)…"
  pkexec docker compose -f "$COMPOSE_FILE" up -d
else
  echo "Нет доступа к Docker. Выполните в терминале (один раз), затем перелогиньтесь или newgrp docker:"
  echo "  sudo groupadd docker 2>/dev/null || true"
  echo "  sudo usermod -aG docker \"\$USER\""
  echo "  newgrp docker"
  echo "Или:"
  echo "  sudo docker compose -f \"$COMPOSE_FILE\" up -d"
  exit 1
fi
echo "TeamCity UI: http://localhost:8111 (или порт TEAMCITY_PORT)"
if docker info &>/dev/null; then
  "${COMPOSE[@]}" ps
else
  pkexec docker compose -f "$COMPOSE_FILE" ps 2>/dev/null || true
fi
