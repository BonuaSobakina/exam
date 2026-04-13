#!/usr/bin/env python3
"""TeamCity: VCS root — отслеживание feature-веток; фильтры веток и VCS-триггеры для Main vs Feature.

Без branch specification в Git VCS root TeamCity видит только default branch — сборки
по feature/wagon-RomanovSV не появляются.

Запуск: TC_USER=... TC_PASSWORD=... python3 teamcity/configure_branches_RomanovSV.py

Опционально: TC_URL, VCS_ROOT_ID (если не задан — обновляются все Git-корни проекта)."""
from __future__ import annotations

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
BT_MAIN = "MainProdRomanovSV"
BT_FEATURE = "FeatureBuildRomanovSV"

# Только для VCS root с Feature в id (не трогаем Git_Main — иначе ломается default main).
BRANCH_SPEC = "+:refs/heads/feature/*"
# Main — main/master и default (логическое имя в TC может отличаться).
FILTER_MAIN = "+:main\n+:<default>\n+:master"
FILTER_FEATURE = ""


def auth_header() -> str:
    if not USER or not PW:
        sys.exit("Нужны TC_USER и TC_PASSWORD")
    return "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode()


def req_json(method: str, path: str, body: dict | None = None) -> dict | list | None:
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": auth_header(), "Accept": "application/json"}
    if data:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{TC}{path}", data=data, method=method, headers=h)
    with urllib.request.urlopen(r, timeout=120) as resp:
        raw = resp.read()
    if not raw:
        return None
    return json.loads(raw)


def req_text(
    method: str,
    path: str,
    body: str,
    content_type: str = "text/plain",
    accept: str = "*/*",
) -> None:
    r = urllib.request.Request(
        f"{TC}{path}",
        data=body.encode(),
        method=method,
        headers={
            "Authorization": auth_header(),
            "Content-Type": content_type,
            "Accept": accept,
        },
    )
    urllib.request.urlopen(r, timeout=60)


def get_props_list(entity: dict) -> list[dict]:
    props = entity.get("properties")
    if not props:
        return []
    return props.get("property", []) or []


def set_property(props: list[dict], name: str, value: str) -> None:
    for p in props:
        if p.get("name") == name:
            p["value"] = value
            return
    props.append({"name": name, "value": value})


def list_project_git_roots() -> list[str]:
    override = os.environ.get("VCS_ROOT_ID", "").strip()
    if override:
        return [override]
    roots: list = []
    for loc in (f"project:(id:{PROJECT})", f"affectedProject:(id:{PROJECT})"):
        try:
            data = req_json("GET", f"/app/rest/vcs-roots?locator={loc}")
        except urllib.error.HTTPError as e:
            print("Ошибка списка VCS roots", loc, e.code)
            continue
        roots = data.get("vcs-root", []) if isinstance(data, dict) else []
        if roots:
            break
    out: list[str] = []
    for vr in roots:
        vid = vr.get("id")
        if not vid:
            continue
        full = req_json("GET", f"/app/rest/vcs-roots/id:{vid}")
        if not isinstance(full, dict):
            continue
        if full.get("vcsName") == "jetbrains.git" or "git" in (full.get("name") or "").lower():
            out.append(vid)
    if not out:
        for vr in roots:
            if vr.get("id"):
                out.append(vr["id"])
    return out


def patch_vcs_branch_spec(root_id: str) -> None:
    """См. Manage VCS Roots REST: PUT .../vcs-roots/id:R/properties/branchSpec (text/plain)."""
    old = ""
    try:
        r = urllib.request.Request(
            f"{TC}/app/rest/vcs-roots/id:{root_id}/properties/branchSpec",
            headers={"Authorization": auth_header(), "Accept": "text/plain"},
        )
        with urllib.request.urlopen(r, timeout=30) as resp:
            old = resp.read().decode().strip()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print("GET branchSpec", root_id, e.code)

    path = f"/app/rest/vcs-roots/id:{root_id}/properties/branchSpec"
    try:
        req_text("PUT", path, BRANCH_SPEC)
        print(f"VCS root {root_id}: branchSpec was {old!r} -> {BRANCH_SPEC!r}")
    except urllib.error.HTTPError as e:
        alt = f"/app/rest/vcs-roots/id:{root_id}/properties/teamcity%3AbranchSpec"
        if e.code == 404:
            try:
                req_text("PUT", alt, BRANCH_SPEC)
                print(f"VCS root {root_id}: teamcity:branchSpec set -> {BRANCH_SPEC!r}")
            except urllib.error.HTTPError as e2:
                print(
                    f"VCS root {root_id}: не выставить branchSpec ({e.code}/{e2.code}). "
                    "Вручную: VCS root → Branch specification → +:refs/heads/feature/*"
                )
        else:
            print(f"PUT {path} failed", e.code, e.read()[:400])
            raise


def put_branch_filter(bt: str, filt: str) -> None:
    candidates = (
        f"/app/rest/buildTypes/id:{bt}/settings/branchFilter",
        f"/app/rest/buildTypes/id:{bt}/settings/teamcity.branchFilter",
    )
    last_err: urllib.error.HTTPError | None = None
    for path in candidates:
        try:
            req_text("PUT", path, filt)
            print(f"buildType {bt} {path.split('/')[-1]} = {filt!r}")
            return
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 404:
                continue
            print("branchFilter PUT failed", bt, path, e.code, e.read()[:400])
            raise
    print(
        f"buildType {bt}: нет endpoint для branchFilter ({last_err and last_err.code}). "
        "Задайте вручную: Version Control Settings → Branch filter."
    )


def patch_vcs_triggers(bt: str, trigger_branch_filter: str) -> None:
    try:
        data = req_json("GET", f"/app/rest/buildTypes/id:{bt}/triggers")
    except urllib.error.HTTPError as e:
        print("GET triggers", bt, e.code)
        return
    triggers = data.get("trigger", []) if isinstance(data, dict) else []
    for t in triggers:
        if t.get("type") != "vcsTrigger":
            continue
        tid = t.get("id")
        if not tid:
            continue
        props = get_props_list(t)
        set_property(props, "branchFilter", trigger_branch_filter)
        t["properties"] = {"property": props, "count": len(props)}
        for drop in ("href",):
            t.pop(drop, None)
        try:
            req_json("PUT", f"/app/rest/buildTypes/id:{bt}/triggers/{tid}", t)
            print(f"  trigger {tid} branchFilter -> {trigger_branch_filter!r}")
        except urllib.error.HTTPError as e:
            print("  PUT trigger", tid, e.code, e.read()[:400])


def warn_if_no_vcs(bt: str) -> None:
    try:
        data = req_json("GET", f"/app/rest/buildTypes/id:{bt}/vcs-root-entries")
    except urllib.error.HTTPError as e:
        print(f"{bt}: не прочитать vcs-root-entries ({e.code})")
        return
    entries = data.get("vcs-root-entry", []) if isinstance(data, dict) else []
    if not entries:
        print(
            f"ВНИМАНИЕ: {bt} без прикреплённого VCS root — "
            "Administration → Build Configuration → Version Control Settings → Attach."
        )


def main() -> None:
    roots = list_project_git_roots()
    if not roots:
        sys.exit(f"Не найдены VCS roots в проекте {PROJECT}. Проверьте id проекта в TeamCity.")
    for rid in roots:
        if "feature" in rid.lower():
            patch_vcs_branch_spec(rid)
        else:
            print(f"VCS root {rid}: пропуск branchSpec (корень main / общий)")

    put_branch_filter(BT_MAIN, FILTER_MAIN)
    if FILTER_FEATURE.strip():
        put_branch_filter(BT_FEATURE, FILTER_FEATURE)
    else:
        try:
            req_text("PUT", f"/app/rest/buildTypes/id:{BT_FEATURE}/settings/branchFilter", "")
            print(f"buildType {BT_FEATURE} branchFilter очищен (все ветки из VCS root)")
        except urllib.error.HTTPError as e:
            print("очистка branchFilter Feature:", e.code)

    patch_vcs_triggers(BT_MAIN, "+:main\n+:<default>\n+:master")
    patch_vcs_triggers(BT_FEATURE, "+:feature/*")

    warn_if_no_vcs(BT_MAIN)
    warn_if_no_vcs(BT_FEATURE)

    print("Готово. В UI: Run — выберите ветку feature/... для Feature-сборки.")


if __name__ == "__main__":
    main()
