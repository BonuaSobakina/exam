#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
export PYTHONPATH=.
python -m ruff check app
cd "$ROOT/frontend"
if [[ -d node_modules ]]; then
  npm run lint
else
  echo "Skipping frontend eslint (node_modules missing). Run npm install in frontend/."
  exit 1
fi
