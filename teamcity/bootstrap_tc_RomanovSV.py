#!/usr/bin/env python3
"""
Идемпотентное создание проекта TeamCity (RomanovSV) через REST API.
Учётные данные только из окружения: TC_URL, TC_USER, TC_PASSWORD
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

TC_URL = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
TC_USER = os.environ.get("TC_USER", "")
TC_PASSWORD = os.environ.get("TC_PASSWORD", "")

PROJECT_ID = "RailwayExamRomanovSV"
GIT_URL = os.environ.get(
    "TC_GIT_URL",
    "https://github.com/RomanovSV/railway-app-RomanovSV.git",
)


def auth_header() -> str:
    if not TC_USER or not TC_PASSWORD:
        print("Задайте TC_USER и TC_PASSWORD", file=sys.stderr)
        sys.exit(1)
    return "Basic " + base64.b64encode(f"{TC_USER}:{TC_PASSWORD}".encode()).decode()


def req(
    method: str,
    path: str,
    data: bytes | None = None,
    content_type: str | None = "application/json",
) -> tuple[int, bytes]:
    url = f"{TC_URL}{path}"
    headers = {"Authorization": auth_header(), "Accept": "application/json"}
    if content_type and data is not None:
        headers["Content-Type"] = content_type
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def post_json(path: str, obj: dict | list) -> tuple[int, bytes]:
    return req("POST", path, json.dumps(obj).encode(), "application/json")


def delete(path: str) -> tuple[int, bytes]:
    return req("DELETE", path, None, None)


def main() -> None:
    # Проект
    code, body = post_json(
        "/app/rest/projects",
        {
            "id": PROJECT_ID,
            "name": "RailwayExam_RomanovSV",
            "parentProject": {"locator": "id:_Root"},
        },
    )
    if code not in (200, 400) or (code == 400 and b"already exists" not in body):
        if code >= 400 and code != 400:
            print("project", code, body[:500])
            sys.exit(1)

    # VCS main + feature
    for payload in (
        {
            "name": "Git_Main_RomanovSV",
            "id": f"{PROJECT_ID}_GitMain",
            "vcsName": "jetbrains.git",
            "project": {"locator": f"id:{PROJECT_ID}"},
            "properties": {
                "property": [
                    {"name": "url", "value": GIT_URL},
                    {"name": "branch", "value": "refs/heads/main"},
                    {"name": "teamcity:branchSpec", "value": "+:refs/heads/main"},
                    {"name": "authMethod", "value": "ANONYMOUS"},
                    {"name": "agentCleanPolicy", "value": "ON_BRANCH_CHANGE"},
                    {"name": "agentCleanFilesPolicy", "value": "ALL_UNTRACKED"},
                ]
            },
        },
        {
            "name": "Git_Feature_RomanovSV",
            "id": f"{PROJECT_ID}_GitFeature",
            "vcsName": "jetbrains.git",
            "project": {"locator": f"id:{PROJECT_ID}"},
            "properties": {
                "property": [
                    {"name": "url", "value": GIT_URL},
                    {"name": "branch", "value": "refs/heads/feature/wagon-RomanovSV"},
                    {
                        "name": "teamcity:branchSpec",
                        "value": "+:refs/heads/feature/*\n+:refs/heads/fix/*",
                    },
                    {"name": "authMethod", "value": "ANONYMOUS"},
                    {"name": "agentCleanPolicy", "value": "ON_BRANCH_CHANGE"},
                    {"name": "agentCleanFilesPolicy", "value": "ALL_UNTRACKED"},
                ]
            },
        },
    ):
        c, b = post_json("/app/rest/vcs-roots", payload)
        if c >= 400 and b"already exists" not in b and b"duplicate" not in b.lower():
            if c != 400:
                print("vcs", c, b[:400])

    # Build types
    for bid, name in (
        ("MainProdRomanovSV", "Main_Prod_RomanovSV"),
        ("FeatureBuildRomanovSV", "Feature_Build_RomanovSV"),
    ):
        c, b = post_json(
            f"/app/rest/projects/id:{PROJECT_ID}/buildTypes",
            {"id": bid, "name": name, "projectId": PROJECT_ID},
        )
        if c >= 400 and b"already exists" not in b:
            if c != 400:
                print("bt", bid, c, b[:300])

    # VCS entries
    pairs = (
        ("MainProdRomanovSV", f"{PROJECT_ID}_GitMain"),
        ("FeatureBuildRomanovSV", f"{PROJECT_ID}_GitFeature"),
    )
    for bt, vid in pairs:
        post_json(
            f"/app/rest/buildTypes/id:{bt}/vcs-root-entries",
            {"vcs-root": {"id": vid}},
        )

    print("Bootstrap структуры готов. Шаги сборки добавьте через UI или обновите скрипт.")


if __name__ == "__main__":
    main()
