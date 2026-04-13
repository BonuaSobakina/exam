#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
export PYTHONPATH=.
python -m pytest -q
cd "$ROOT/frontend"
if [[ -d node_modules ]]; then
  npm run test
else
  echo "Skipping frontend tests (node_modules missing)."
  exit 1
fi
