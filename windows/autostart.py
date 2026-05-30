from __future__ import annotations

import ctypes
import ctypes.wintypes
import logging
import os
import sys
import winreg
from pathlib import Path

from shared.constants import APP_RUN_VALUE, RUN_KEY

log = logging.getLogger(__name__)

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _get_process_exe(pid: int) -> Path | None:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = ctypes.wintypes.DWORD(1024)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return Path(buf.value).resolve()
    finally:
        kernel32.CloseHandle(handle)
    return None


def _get_executable_path() -> Path | None:
    # Nuitka onefile extracts to a random temp dir each launch, so
    # GetModuleFileNameW returns a stale path. Use NUITKA_ONEFILE_PARENT
    # to find the bootstrapper's real path instead.
    parent_pid = os.environ.get("NUITKA_ONEFILE_PARENT")
    if parent_pid is not None:
        try:
            path = _get_process_exe(int(parent_pid))
            if path:
                return path
        except (ValueError, OSError):
            pass

    if not getattr(sys, "frozen", False):
        return None

    buf = ctypes.create_unicode_buffer(1024)
    length = ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 1024)
    if length > 0:
        return Path(buf.value).resolve()

    return Path(sys.argv[0]).resolve()


def _startup_command() -> str:
    exe = _get_executable_path()
    if exe:
        return f'"{exe}"'
    return f'"{sys.executable}" "{Path(__file__).resolve().parent / "main.py"}"'


def is_autostart_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_RUN_VALUE)
    except FileNotFoundError:
        return False
    except OSError as exc:
        log.warning("Failed to read autostart key: %s", exc)
        return False

    return value == _startup_command()


def set_autostart(enabled: bool) -> bool:
    try:
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enabled:
                cmd = _startup_command()
                winreg.SetValueEx(key, APP_RUN_VALUE, 0, winreg.REG_SZ, cmd)
                log.info("Enabled auto-start: %s", cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_RUN_VALUE)
                except FileNotFoundError:
                    pass
                log.info("Disabled auto-start")
        return True
    except OSError as exc:
        log.warning("Failed to update auto-start: %s", exc)
        return False


def sync_autostart_command() -> None:
    # Repair the registry entry if it points to a stale path (e.g. old Nuitka temp).
    if _get_executable_path() is None:
        return

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_RUN_VALUE)
    except FileNotFoundError:
        return
    except OSError:
        return

    expected = _startup_command()
    if value != expected:
        set_autostart(True)
        log.info("Repaired auto-start from %r to %r", value, expected)
