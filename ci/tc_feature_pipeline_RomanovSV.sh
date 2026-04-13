#!/usr/bin/env bash
# Один скрипт для Feature-сборки в TeamCity (один шаг Command Line).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
bash ci/tc_lint_RomanovSV.sh
bash ci/tc_sast_RomanovSV.sh
bash ci/tc_test_RomanovSV.sh
bash ci/docker_build_feature_RomanovSV.sh
