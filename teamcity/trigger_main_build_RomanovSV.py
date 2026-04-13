#!/usr/bin/env python3
"""Поставить в очередь сборку MainProdRomanovSV (ветка main по умолчанию).

Авторизация (один из вариантов):
  export TC_USER=admin TC_PASSWORD=...
  export TC_URL=http://localhost:8111

или постоянный токен TeamCity (Profile → Access tokens):
  export TC_ACCESS_TOKEN=...
  export TC_URL=http://localhost:8111

Запуск из корня railway-app:
  python3 teamcity/trigger_main_build_RomanovSV.py

Опционально: BRANCH=main или BRANCH=refs/heads/main
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

TC_URL = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
BT_ID = "MainProdRomanovSV"
USER = os.environ.get("TC_USER", "")
PW = os.environ.get("TC_PASSWORD", "")
TOKEN = os.environ.get("TC_ACCESS_TOKEN", "").strip()
BRANCH = os.environ.get("BRANCH", "").strip()


def auth_header() -> str:
    if TOKEN:
        return f"Bearer {TOKEN}"
    if USER and PW:
        return "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode()
    print(
        "Нужны TC_ACCESS_TOKEN или пара TC_USER + TC_PASSWORD.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    payload: dict = {"buildType": {"id": BT_ID}}
    if BRANCH:
        payload["branchName"] = BRANCH
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{TC_URL}/app/rest/buildQueue",
        data=body,
        method="POST",
        headers={
            "Authorization": auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            print("HTTP", r.status)
            print(raw[:2000])
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, file=sys.stderr)
        print(e.read().decode()[:2000], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
