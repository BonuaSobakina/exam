#!/usr/bin/env python3
"""Пересоздать шаги Main_Prod / Feature_Build как Command Line (simpleRunner).

Имя файла историческое: раньше шаги были Python runner — на агенте jetbrains/teamcity-agent
они дают «Python executable key must be not empty». Нужны шаги Command Line.

Переменные: TC_USER, TC_PASSWORD; при сервере не на localhost — TC_URL=http://хост:8111
"""
from __future__ import annotations

import sys
from pathlib import Path

_tc_dir = Path(__file__).resolve().parent
if str(_tc_dir) not in sys.path:
    sys.path.insert(0, str(_tc_dir))
from inline_feature_pipeline_RomanovSV import FEATURE_PIPELINE_SCRIPT

import base64
import json
import os
import sys
import urllib.request

TC = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
USER = os.environ.get("TC_USER", "")
PW = os.environ.get("TC_PASSWORD", "")


def auth() -> str:
    if not USER or not PW:
        sys.exit("Нужны TC_USER и TC_PASSWORD")
    return "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode()


def j(method: str, path: str, body: dict | None = None) -> None:
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": auth(), "Accept": "application/json"}
    if data:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{TC}{path}", data=data, method=method, headers=h)
    urllib.request.urlopen(r, timeout=300)


def get_steps(bt: str) -> list[dict]:
    req = urllib.request.Request(
        f"{TC}/app/rest/buildTypes/id:{bt}/steps",
        headers={"Authorization": auth(), "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read()).get("step", []) or []


def del_all_steps(bt: str) -> None:
    for s in get_steps(bt):
        j("DELETE", f"/app/rest/buildTypes/id:{bt}/steps/{s['id']}")


def add_cmd(bt: str, name: str, script: str) -> None:
    step = {
        "name": name,
        "type": "simpleRunner",
        "properties": {
            "property": [
                {"name": "script.content", "value": script},
                {"name": "use.custom.script", "value": "true"},
                {"name": "teamcity.step.mode", "value": "default"},
            ]
        },
    }
    j("POST", f"/app/rest/buildTypes/id:{bt}/steps", step)


# Явный checkout: у Command Line иногда рабочая директория не корень репозитория.
def _in_checkout(cmd: str) -> str:
    return 'cd "%teamcity.build.checkoutDir%" && ' + cmd


def main() -> None:
    for bt, steps in [
        (
            "MainProdRomanovSV",
            [
                # Без docker run -v: на агенте с socket хоста пути checkout недоступны демону (exit 125).
                # Полный lint/test: bash ci/verify_all_RomanovSV.sh локально или на агенте с bind /opt/buildagent/work (см. README).
                ("Docker_build_RomanovSV", _in_checkout("bash ci/docker_build_main_RomanovSV.sh")),
                ("Docker_push_RomanovSV", _in_checkout("bash ci/docker_push_main_RomanovSV.sh")),
                ("Deploy_prod_RomanovSV", _in_checkout("bash ci/deploy_prod_RomanovSV.sh")),
            ],
        ),
        (
            "FeatureBuildRomanovSV",
            [
                # Один Command Line — меньше шансов остаться на старых Python-шагах в UI.
                ("Feature_pipeline_RomanovSV", FEATURE_PIPELINE_SCRIPT),
            ],
        ),
    ]:
        del_all_steps(bt)
        for name, script in steps:
            add_cmd(bt, name, script)
        print(bt, len(steps), "steps OK")
        for s in get_steps(bt):
            print(f"  - {s.get('name')}: type={s.get('type')!r} (в логе сборки должно быть «Command Line», не «Python»)")


if __name__ == "__main__":
    main()
