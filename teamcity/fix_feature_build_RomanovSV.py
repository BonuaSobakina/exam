#!/usr/bin/env python3
"""Только Feature-сборка: удалить все шаги и создать ОДИН Command Line (simpleRunner).

Снимает «Python executable key» — в TC не должно остаться python-runner.

  TC_URL=http://хост:8111 TC_USER=… TC_PASSWORD=… python3 teamcity/fix_feature_build_RomanovSV.py

Опционально: TC_FEATURE_BT=id (если не задан — ищется конфигурация с Feature + Romanov в id/name)."""
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
import urllib.error
import urllib.request

TC = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
USER = os.environ.get("TC_USER", "")
PW = os.environ.get("TC_PASSWORD", "")
PROJECT = "RailwayExamRomanovSV"


def auth() -> str:
    if not USER or not PW:
        sys.exit("Нужны TC_USER и TC_PASSWORD")
    return "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode()


def req(method: str, path: str, body: dict | None = None) -> tuple[int, bytes]:
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": auth(), "Accept": "application/json"}
    if data:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{TC}{path}", data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def get_json(method: str, path: str, body: dict | None = None) -> dict | list:
    code, raw = req(method, path, body)
    if code >= 400:
        sys.exit(f"{method} {path} -> HTTP {code}: {raw[:800]!r}")
    if not raw:
        return {}
    return json.loads(raw)


def find_feature_bt_id() -> str:
    explicit = os.environ.get("TC_FEATURE_BT", "").strip()
    if explicit:
        return explicit
    data = get_json("GET", f"/app/rest/buildTypes?locator=project:(id:{PROJECT})")
    bts = data.get("buildType", []) if isinstance(data, dict) else []
    for bt in bts:
        if bt.get("id") == "FeatureBuildRomanovSV":
            print("Используется buildType id=FeatureBuildRomanovSV")
            return "FeatureBuildRomanovSV"
    hits: list[tuple[str, str]] = []
    for bt in bts:
        bid = (bt.get("id") or "").lower()
        bname = (bt.get("name") or "").lower()
        if "feature" in bid or "feature" in bname:
            if "romanov" in bid or "romanov" in bname or "wagon" in bid:
                hits.append((bt.get("id", ""), bt.get("name", "")))
            elif not hits:
                hits.append((bt.get("id", ""), bt.get("name", "")))
    if not hits:
        print("Конфигурации проекта:", [(b.get("id"), b.get("name")) for b in bts])
        sys.exit(
            "Не найдена Feature-сборка. Задайте TC_FEATURE_BT=id_из_UI "
            "(Build Configuration → Settings → Configuration ID)."
        )
    bt_id, name = hits[0]
    print(f"Используется buildType id={bt_id!r} name={name!r} (TC_FEATURE_BT переопределяет)")
    return bt_id


def get_steps(bt: str) -> list[dict]:
    data = get_json("GET", f"/app/rest/buildTypes/id:{bt}/steps")
    return data.get("step", []) or []


def del_step(bt: str, sid: str) -> None:
    code, raw = req("DELETE", f"/app/rest/buildTypes/id:{bt}/steps/{sid}")
    if code >= 400:
        sys.exit(f"DELETE step {sid} -> HTTP {code}: {raw[:600]!r}")


def add_simple_runner(bt: str, name: str, script: str) -> None:
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
    code, raw = req("POST", f"/app/rest/buildTypes/id:{bt}/steps", step)
    if code >= 400:
        sys.exit(f"POST step -> HTTP {code}: {raw[:800]!r}")


def warn_template(bt: str) -> None:
    try:
        info = get_json("GET", f"/app/rest/buildTypes/id:{bt}?fields=template,templateFlag,name,id")
    except SystemExit:
        return
    if not isinstance(info, dict):
        return
    tpl = info.get("template")
    if tpl and isinstance(tpl, dict) and tpl.get("id"):
        print(
            "ВНИМАНИЕ: конфигурация привязана к шаблону "
            f"{tpl.get('id')!r}. Наследованные шаги REST может не удалять. "
            "В UI: Actions → Edit Settings → отвязать от шаблона или править шаблон."
        )


def main() -> None:
    bt = find_feature_bt_id()
    warn_template(bt)

    steps_before = get_steps(bt)
    for s in steps_before:
        if s.get("type") == "python-runner":
            print(f"Удаляю python-runner: {s.get('name')!r} id={s.get('id')}")
        if s.get("inherited"):
            print(f"Шаг inherited={s.get('name')!r} — если DELETE не сработает, отвяжите шаблон.")
        del_step(bt, s["id"])

    add_simple_runner(bt, "Feature_pipeline_RomanovSV", FEATURE_PIPELINE_SCRIPT)

    steps_after = get_steps(bt)
    if len(steps_after) != 1:
        sys.exit(f"Ожидался 1 шаг, получено {len(steps_after)}: {steps_after!r}")
    t = steps_after[0].get("type")
    if t != "simpleRunner":
        sys.exit(
            f"TeamCity вернул type={t!r}, нужен simpleRunner. "
            f"Проверьте версию TC и права пользователя {USER!r}."
        )
    print("OK: один шаг Command Line (simpleRunner). В логе: «Feature_pipeline_RomanovSV (Command Line)».")


if __name__ == "__main__":
    main()
