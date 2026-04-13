#!/usr/bin/env bash
# Линты в контейнерах (для TeamCity-агента: только Docker + checkout).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
docker run --rm -v "${ROOT}:/repo" -w /repo python:3.12-bookworm bash -lc \
  'pip install -q -r backend/requirements.txt && cd backend && PYTHONPATH=. python -m ruff check app'
docker run --rm -v "${ROOT}:/repo" -w /repo/frontend node:22-bookworm bash -lc \
  'npm install && npm run lint'
