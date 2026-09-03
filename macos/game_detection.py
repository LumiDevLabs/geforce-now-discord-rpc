from __future__ import annotations

import logging

import psutil

from shared.constants import (
    APP_NAME,
    GFN_IGNORED_TITLES,
    GFN_PROCESS_NAMES,
    clean_game_name,
)

log = logging.getLogger(__name__)

# Set to True once we've warned about the missing Screen Recording permission so
# we don't spam the log on every poll.
_warned_no_titles = False


def _matches_gfn(name: str) -> bool:
    lowered = name.lower()
    if lowered in GFN_PROCESS_NAMES:
        return True
    return "geforce" in lowered and "now" in lowered


def _get_gfn_pids() -> list[int]:
    pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"] or ""
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if _matches_gfn(name):
            pids.append(proc.info["pid"])
    return pids


def _get_window_titles(pids: list[int]) -> list[str]:
    # kCGWindowName is only populated when Screen Recording permission is granted (macOS 10.15+).
    global _warned_no_titles

    try:
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGNullWindowID,
            kCGWindowListExcludeDesktopElements,
            kCGWindowListOptionOnScreenOnly,
        )
    except ImportError as exc:
        log.error("PyObjC Quartz framework unavailable: %s", exc)
        return []

    pid_set = set(pids)
    titled_windows: list[tuple[float, str]] = []
    owner_without_name = False

    options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID) or []

    for window in window_list:
        owner_pid = window.get("kCGWindowOwnerPID")
        if owner_pid not in pid_set:
            continue
        name = window.get("kCGWindowName")
        if name:
            bounds = window.get("kCGWindowBounds") or {}
            try:
                area = float(bounds.get("Width", 0)) * float(bounds.get("Height", 0))
            except (AttributeError, TypeError, ValueError):
                area = 0
            titled_windows.append((area, str(name)))
        else:
            owner_without_name = True

    if owner_without_name and not titled_windows:
        if not _warned_no_titles:
            log.warning(
                "GeForce NOW windows found but their titles are empty. Grant "
                "Screen Recording permission to %s in System Settings > Privacy "
                "& Security > Screen Recording, then restart the app.",
                APP_NAME,
            )
            _warned_no_titles = True
    else:
        _warned_no_titles = False

    titled_windows.sort(key=lambda item: item[0], reverse=True)
    return [title for _, title in titled_windows]


def get_active_gfn_game() -> str | None:
    pids = _get_gfn_pids()
    if not pids:
        return None

    log.debug("GeForce NOW PIDs: %s", pids)
    titles = _get_window_titles(pids)

    for title in titles:
        cleaned = clean_game_name(title)
        if cleaned and cleaned.lower() not in GFN_IGNORED_TITLES:
            return cleaned

    return None
