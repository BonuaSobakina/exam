#!/usr/bin/env bash
set -euo pipefail
# Feature/fix branch: build images only (no push to Docker Hub).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose build
echo "Docker_build_RomanovSV: images built successfully (no deploy)."
