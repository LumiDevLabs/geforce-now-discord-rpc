from __future__ import annotations

import ctypes
import logging
from ctypes import wintypes

import psutil

from constants import GFN_IGNORED_TITLES, GFN_PROCESS_NAMES, GFN_TITLE_SUFFIXES

log = logging.getLogger(__name__)

_user32 = ctypes.windll.user32

_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetWindowTextW = _user32.GetWindowTextW
_GetWindowTextLengthW = _user32.GetWindowTextLengthW
_IsWindowVisible = _user32.IsWindowVisible

_ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)
_user32.EnumWindows.argtypes = [_ENUM_WINDOWS_PROC, wintypes.LPARAM]
_user32.EnumWindows.restype = wintypes.BOOL


def clean_game_name(title: str) -> str:
    """Strip GeForce NOW suffixes from a window title."""
    if not title:
        return ""
    cleaned = title.strip()
    lowered = cleaned.lower()
    for suffix in GFN_TITLE_SUFFIXES:
        if lowered.endswith(suffix):
            return cleaned[: -len(suffix)].strip()
    return cleaned


def _get_gfn_pids() -> list[int]:
    """Find PIDs of running GeForce NOW processes."""
    pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = (proc.info["name"] or "").lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if name in GFN_PROCESS_NAMES:
            pids.append(proc.info["pid"])
    return pids


def _get_window_titles(pids: list[int]) -> list[str]:
    """Enumerate visible window titles belonging to the given PIDs."""
    pid_set = set(pids)
    titles: list[str] = []

    def callback(hwnd: int, _: int) -> bool:
        if not _IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        _GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value not in pid_set:
            return True
        length = _GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            _GetWindowTextW(hwnd, buf, length + 1)
            titles.append(buf.value)
        return True

    _user32.EnumWindows(_ENUM_WINDOWS_PROC(callback), 0)
    return titles


def get_active_gfn_game() -> str | None:
    """Detect the currently active GeForce NOW game, or None if not streaming."""
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
