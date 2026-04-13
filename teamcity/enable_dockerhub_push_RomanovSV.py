#!/usr/bin/env python3
"""Снять обход SKIP_* и при необходимости записать Write-PAT в проект TeamCity.

После создания в Docker Hub токена с Read & Write:

  DOCKERHUB_PASSWORD=dckr_pat_... TC_USER=... TC_PASSWORD=... \\
    python3 teamcity/enable_dockerhub_push_RomanovSV.py

Только снять SKIP (пароль уже выставлен в UI):

  TC_USER=... TC_PASSWORD=... python3 teamcity/enable_dockerhub_push_RomanovSV.py

Затем Run → MainProdRomanovSV — образы появятся на Hub.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

TC = os.environ.get("TC_URL", "http://127.0.0.1:8111").rstrip("/")
USER = os.environ.get("TC_USER", "")
PW_TC = os.environ.get("TC_PASSWORD", "")
PROJECT = "RailwayExamRomanovSV"


def auth() -> str:
    if not USER or not PW_TC:
        sys.exit("Нужны TC_USER и TC_PASSWORD")
    return "Basic " + base64.b64encode(f"{USER}:{PW_TC}".encode()).decode()


def delete_param(name: str) -> None:
    req = urllib.request.Request(
        f"{TC}/app/rest/projects/id:{PROJECT}/parameters/{name}",
        method="DELETE",
        headers={"Authorization": auth()},
    )
    try:
        urllib.request.urlopen(req, timeout=30)
        print("deleted", name)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("skip", name, "(нет)")
        else:
            print("DELETE", name, e.code, e.read()[:200])


def main() -> None:
    hub_pw = os.environ.get("DOCKERHUB_PASSWORD", "").strip()
    if hub_pw:
        body = json.dumps(
            {
                "name": "env.DOCKERHUB_PASSWORD",
                "value": hub_pw,
                "type": {"rawValue": "password"},
            }
        ).encode()
        req = urllib.request.Request(
            f"{TC}/app/rest/projects/id:{PROJECT}/parameters/env.DOCKERHUB_PASSWORD",
            data=body,
            method="PUT",
            headers={
                "Authorization": auth(),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        urllib.request.urlopen(req, timeout=30)
        print("env.DOCKERHUB_PASSWORD обновлён (Write PAT).")

    for n in ("env.SKIP_DOCKER_PUSH", "env.SKIP_DEPLOY_PROD"):
        delete_param(n)

    print("Готово: запустите Main в TeamCity или: python3 teamcity/trigger_main_build_RomanovSV.py")


if __name__ == "__main__":
    main()
