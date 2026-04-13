"""Один шаг Command Line для Feature на агенте с Docker socket на хосте.

`docker run -v $(pwd):/repo` ломается: демон на хосте не видит путь /opt/buildagent/work/... из контейнера.
`docker compose build` отдаёт контекст с клиента — работает. Линты гоняйте локально: ci/verify_all_RomanovSV.sh
"""
from __future__ import annotations

FEATURE_PIPELINE_SCRIPT = r"""#!/usr/bin/env bash
set -euo pipefail
cd "%teamcity.build.checkoutDir%"
docker compose build
echo "Feature build OK (compose only; lint/test: bash ci/verify_all_RomanovSV.sh локально)"
"""
