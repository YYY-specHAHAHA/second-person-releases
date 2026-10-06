#!/usr/bin/env python3
"""Check the deployed second-person site and the exact public APK bytes."""

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE = "https://second.translens.cn/second-person/"
RELEASES = "https://github.com/YYY-specHAHAHA/second-person-releases/releases/download/"
HEADERS = {"User-Agent": "second-person-public-healthcheck/1.0"}
MAX_APK_BYTES = 100 * 1024 * 1024


def get(url: str, limit: int) -> bytes:
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=30) as response:
        if response.geturl().split(":", 1)[0] != "https":
            raise RuntimeError(f"Non-HTTPS redirect: {url}")
        data = response.read(limit + 1)
        if len(data) > limit:
            raise RuntimeError(f"Response too large: {url}")
        return data


def check() -> None:
    root = Path(__file__).resolve().parents[1]
    expected_path = root / "site" / "second-person" / "latest.json"
    page = get(BASE, 512_000).decode("utf-8")
    privacy = get(BASE + "privacy/", 512_000).decode("utf-8")
    css = get(BASE + "site.css", 512_000)
    if not css or "第二人称" not in page:
        raise RuntimeError("Public page or CSS is incomplete")
    if "Charry yang" not in privacy or "dosomethinginteresting@outlook.com" not in privacy:
        raise RuntimeError("Privacy contact or operator is missing")

    if not expected_path.exists():
        if "正式版准备中" not in page or "下载 Android APK" in page:
            raise RuntimeError("Preview page unexpectedly offers a download")
        try:
            get(BASE + "latest.json", 64_000)
        except HTTPError as error:
            if error.code != 404:
                raise
        else:
            raise RuntimeError("Preview unexpectedly exposes latest.json")
        print("OK: HTTPS page, privacy and preview download gate")
        return

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    live = json.loads(get(BASE + "latest.json", 64_000))
    if live != expected or live.get("available") is not True:
        raise RuntimeError("Live version manifest differs from published repository")
    name = live.get("version_name")
    digest = live.get("apk_sha256")
    if not isinstance(name, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?", name):
        raise RuntimeError("Invalid release version")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise RuntimeError("Invalid APK SHA-256")
    apk_url = f"{RELEASES}v{name}/second-person-{name}.apk"
    if f'href="{apk_url}"' not in page or "政策草案" in privacy:
        raise RuntimeError("Live download button or final privacy page is missing")
    apk = get(apk_url, MAX_APK_BYTES)
    if hashlib.sha256(apk).hexdigest() != digest:
        raise RuntimeError("Public APK SHA-256 mismatch")
    print(f"OK: release {name}, {len(apk)} bytes, SHA-256 verified")


if __name__ == "__main__":
    try:
        check()
    except Exception as error:
        print(f"PUBLIC RELEASE CHECK FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
