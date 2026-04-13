#!/usr/bin/env python3
"""Применить настройки, из‑за которых чаще всего падает Main в TeamCity.

1. Параметры Docker Hub (и опционально токен из DOCKERHUB_PASSWORD).
2. Шаги Command Line с cd в checkoutDir.
3. Ветки / VCS trigger для main и feature.

Запуск (с машины, где доступен UI TeamCity по сети):

  export TC_URL=http://127.0.0.1:8111   # или хост:8111
  export TC_USER=admin TC_PASSWORD=...
  export DOCKERHUB_PASSWORD=dckr_pat_...   # опционально; не коммитьте

  python3 teamcity/fix_main_build_RomanovSV.py

Агент TC в Docker не использует docker login с хоста — без env.DOCKERHUB_PASSWORD шаг push будет красным.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "teamcity/apply_dockerhub_teamcity_RomanovSV.py",
    "teamcity/seed_python_build_steps_RomanovSV.py",
    "teamcity/configure_branches_RomanovSV.py",
]


def main() -> None:
    if not os.environ.get("TC_USER") or not os.environ.get("TC_PASSWORD"):
        print("Нужны TC_USER и TC_PASSWORD.", file=sys.stderr)
        sys.exit(1)
    env = os.environ.copy()
    for rel in SCRIPTS:
        cmd = [sys.executable, str(ROOT / rel)]
        print("+", " ".join(cmd))
        r = subprocess.run(cmd, cwd=str(ROOT), env=env)
        if r.returncode != 0:
            sys.exit(r.returncode)
    print("Готово. Запустите MainProdRomanovSV в TeamCity (Run).")
    if not env.get("DOCKERHUB_PASSWORD", "").strip():
        print(
            "Подсказка: без DOCKERHUB_PASSWORD в окружении токен в TC не обновлялся — "
            "задайте env.DOCKERHUB_PASSWORD в проекте или повторите с DOCKERHUB_PASSWORD=..."
        )


if __name__ == "__main__":
    main()
