#!/usr/bin/env python3
"""TeamCity: параметры env.EXAM_IMAGE, env.DOCKERHUB_USER, опционально env.DOCKERHUB_PASSWORD.

   Шаги сборки — teamcity/seed_python_build_steps_RomanovSV.py (simpleRunner + ci/*.sh).

   Запуск:
     TC_USER=... TC_PASSWORD=... python3 teamcity/apply_dockerhub_teamcity_RomanovSV.py

   Чтобы записать токен Hub в проект (тип password, не светится в логах):
     DOCKERHUB_PASSWORD=dckr_pat_... TC_USER=... TC_PASSWORD=... python3 ...
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

TC_URL = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
USER = os.environ.get("TC_USER", "")
PASSWORD = os.environ.get("TC_PASSWORD", "")
PROJECT = "RailwayExamRomanovSV"


def auth_header() -> str:
    if not USER or not PASSWORD:
        print("Нужны TC_USER и TC_PASSWORD", file=sys.stderr)
        sys.exit(1)
    return "Basic " + base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()


def post_or_put_param(name: str, value: str) -> None:
    req = urllib.request.Request(
        f"{TC_URL}/app/rest/projects/id:{PROJECT}/parameters/{name}",
        data=value.encode(),
        method="PUT",
        headers={"Authorization": auth_header(), "Content-Type": "text/plain"},
    )
    try:
        urllib.request.urlopen(req, timeout=30)
        print("param", name, "OK")
        return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print("param", name, "PUT err", e.code, e.read()[:200])
            return
    body = json.dumps({"name": name, "value": value}).encode()
    req2 = urllib.request.Request(
        f"{TC_URL}/app/rest/projects/id:{PROJECT}/parameters",
        data=body,
        method="POST",
        headers={
            "Authorization": auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    urllib.request.urlopen(req2, timeout=30)
    print("param", name, "POST OK")


def set_password_param(name: str, value: str) -> None:
    """Секретный параметр (тип password) для push с агента TC (docker login не из хоста)."""
    body = json.dumps(
        {"name": name, "value": value, "type": {"rawValue": "password"}}
    ).encode()
    headers = {
        "Authorization": auth_header(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    put_url = f"{TC_URL}/app/rest/projects/id:{PROJECT}/parameters/{name}"
    req = urllib.request.Request(put_url, data=body, method="PUT", headers=headers)
    try:
        urllib.request.urlopen(req, timeout=30)
        print("param", name, "password PUT OK")
        return
    except urllib.error.HTTPError as e:
        err = e.read()[:300] if e.fp else b""
        if e.code != 404:
            print("param", name, "password PUT err", e.code, err)
            return
    post = urllib.request.Request(
        f"{TC_URL}/app/rest/projects/id:{PROJECT}/parameters",
        data=body,
        method="POST",
        headers=headers,
    )
    urllib.request.urlopen(post, timeout=30)
    print("param", name, "password POST OK")


def main() -> None:
    post_or_put_param("env.EXAM_IMAGE", "romanovsv2/exam")
    post_or_put_param("env.DOCKERHUB_USER", "romanovsv2")
    hub_pw = os.environ.get("DOCKERHUB_PASSWORD", "").strip()
    if hub_pw:
        set_password_param("env.DOCKERHUB_PASSWORD", hub_pw)
        print("env.DOCKERHUB_PASSWORD записан в проект (тип password).")
    else:
        print(
            "Без DOCKERHUB_PASSWORD: задайте env.DOCKERHUB_PASSWORD в UI проекта "
            "или повторите скрипт с DOCKERHUB_PASSWORD=... в окружении."
        )
    print("Шаги сборки: python3 teamcity/seed_python_build_steps_RomanovSV.py")


if __name__ == "__main__":
    main()
