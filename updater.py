from __future__ import annotations

import logging
import os
from tkinter import messagebox

import requests

from constants import APP_NAME, APP_VERSION, GITHUB_REPO

log = logging.getLogger(__name__)


def _parse_version(version: str) -> tuple[int, ...]:
    cleaned = version.strip().lstrip("vV").split("-", 1)[0].split("+", 1)[0]
    parts = []
    for segment in cleaned.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            parts.append(0)
    return tuple((parts + [0, 0, 0])[:3])


def _is_newer(latest: str, current: str) -> bool:
    return _parse_version(latest) > _parse_version(current)


def check_for_update(notify_if_current: bool = False) -> None:
    if not GITHUB_REPO:
        if notify_if_current:
            messagebox.showinfo(APP_NAME, "Updates are not configured for this build.")
        return

    try:
        resp = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            timeout=10,
        )
        resp.raise_for_status()
        release = resp.json()
    except requests.RequestException as exc:
        log.warning("Update check failed: %s", exc)
        if notify_if_current:
            messagebox.showerror(APP_NAME, f"Could not check for updates:\n{exc}")
        return

    latest = release.get("tag_name", "")
    release_url = release.get("html_url", f"https://github.com/{GITHUB_REPO}/releases/latest")

    log.info("Update check: current=%s latest=%s", APP_VERSION, latest)

    if latest and _is_newer(latest, APP_VERSION):
        if messagebox.askyesno(
            APP_NAME, f"Version {latest} is available.\nOpen the download page?"
        ):
            os.startfile(release_url)
        return

    if notify_if_current:
        messagebox.showinfo(APP_NAME, f"You are up to date (v{APP_VERSION}).")
