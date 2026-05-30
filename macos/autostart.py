from __future__ import annotations

import logging
import plistlib
import subprocess
import sys
from pathlib import Path

from shared.constants import BUNDLE_ID

log = logging.getLogger(__name__)

PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{BUNDLE_ID}.plist"


def _program_arguments() -> list[str]:
    exe = Path(sys.executable).resolve()
    if ".app/Contents/MacOS" in str(exe) or getattr(sys, "frozen", False):
        return [str(exe)]
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    return [str(exe), str(main_py)]


def _expected_plist() -> dict:
    return {
        "Label": BUNDLE_ID,
        "ProgramArguments": _program_arguments(),
        "RunAtLoad": True,
        "ProcessType": "Interactive",
    }


def _read_plist() -> dict | None:
    if not PLIST_PATH.exists():
        return None
    try:
        with PLIST_PATH.open("rb") as f:
            return plistlib.load(f)
    except (OSError, plistlib.InvalidFileException) as exc:
        log.warning("Failed to read LaunchAgent plist: %s", exc)
        return None


def _launchctl(*args: str) -> bool:
    try:
        result = subprocess.run(
            ["launchctl", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        log.warning("launchctl %s failed: %s", " ".join(args), exc)
        return False
    if result.returncode != 0:
        log.debug("launchctl %s -> %s: %s", " ".join(args), result.returncode, result.stderr.strip())
    return result.returncode == 0


def is_autostart_enabled() -> bool:
    data = _read_plist()
    if not data:
        return False
    return data.get("ProgramArguments") == _program_arguments()


def set_autostart(enabled: bool) -> bool:
    try:
        if enabled:
            PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
            with PLIST_PATH.open("wb") as f:
                plistlib.dump(_expected_plist(), f)
            # Reload so changes take effect immediately.
            _launchctl("unload", str(PLIST_PATH))
            ok = _launchctl("load", "-w", str(PLIST_PATH))
            log.info("Enabled auto-start via LaunchAgent: %s", PLIST_PATH)
            return ok
        else:
            if PLIST_PATH.exists():
                _launchctl("unload", "-w", str(PLIST_PATH))
                try:
                    PLIST_PATH.unlink()
                except OSError as exc:
                    log.warning("Failed to remove plist: %s", exc)
                    return False
            log.info("Disabled auto-start")
            return True
    except OSError as exc:
        log.warning("Failed to update auto-start: %s", exc)
        return False


def sync_autostart_command() -> None:
    # Repair the plist if it points to a stale executable path after an update.
    data = _read_plist()
    if not data:
        return
    if data.get("ProgramArguments") != _program_arguments():
        log.info("Repairing stale LaunchAgent path")
        set_autostart(True)
