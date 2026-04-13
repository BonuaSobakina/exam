#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
docker run --rm -v "${ROOT}:/repo" -w /repo python:3.12-bookworm bash -lc \
  'pip install -q -r backend/requirements.txt && cd backend && PYTHONPATH=. pytest -q'
docker run --rm -v "${ROOT}:/repo" -w /repo/frontend node:22-bookworm bash -lc \
  'npm install && npm run test'
