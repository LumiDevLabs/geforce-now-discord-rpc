from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from shared.constants import APP_NAME, SECRETS_FILE, SECRET_KEYS

log = logging.getLogger(__name__)

IS_MACOS = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"


def open_path(path: str | Path) -> None:
    target = str(path)
    try:
        if IS_WINDOWS:
            os.startfile(target)  # type: ignore[attr-defined]
        elif IS_MACOS:
            subprocess.run(["open", target], check=False)
        else:
            subprocess.run(["xdg-open", target], check=False)
    except OSError as exc:
        log.warning("Failed to open %s: %s", target, exc)


def _osascript_dialog(message: str, buttons: list[str], default: str, error: bool) -> str | None:
    button_list = ", ".join(f'"{b}"' for b in buttons)
    icon = "stop" if error else "note"
    script = (
        f'display dialog {json.dumps(message)} '
        f'with title {json.dumps(APP_NAME)} '
        f'buttons {{{button_list}}} default button {json.dumps(default)} '
        f'with icon {icon}'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        log.warning("osascript dialog failed: %s", exc)
        return None

    if result.returncode != 0:
        return None

    # Output looks like: "button returned:Yes"
    out = result.stdout.strip()
    if "button returned:" in out:
        return out.split("button returned:", 1)[1].strip()
    return default


def _win_message_box(message: str, yes_no: bool, error: bool) -> bool:
    # MessageBoxW instead of Tkinter: safe to call from any thread. Tray callbacks
    # and the update checker run on background threads where Tk is not safe.
    import ctypes

    MB_OK = 0x0
    MB_YESNO = 0x4
    MB_ICONERROR = 0x10
    MB_ICONQUESTION = 0x20
    MB_ICONINFORMATION = 0x40
    MB_SETFOREGROUND = 0x10000
    MB_TOPMOST = 0x40000
    IDYES = 6

    flags = MB_SETFOREGROUND | MB_TOPMOST
    if yes_no:
        flags |= MB_YESNO | MB_ICONQUESTION
    elif error:
        flags |= MB_OK | MB_ICONERROR
    else:
        flags |= MB_OK | MB_ICONINFORMATION

    result = ctypes.windll.user32.MessageBoxW(None, str(message), APP_NAME, flags)
    return result == IDYES


def notify(message: str, error: bool = False) -> None:
    if IS_MACOS:
        _osascript_dialog(message, buttons=["OK"], default="OK", error=error)
        return

    if IS_WINDOWS:
        _win_message_box(message, yes_no=False, error=error)
        return

    from tkinter import messagebox

    if error:
        messagebox.showerror(APP_NAME, message)
    else:
        messagebox.showinfo(APP_NAME, message)


def ask_yes_no(message: str) -> bool:
    if IS_MACOS:
        answer = _osascript_dialog(
            message, buttons=["No", "Yes"], default="Yes", error=False
        )
        return answer == "Yes"

    if IS_WINDOWS:
        return _win_message_box(message, yes_no=True, error=False)

    from tkinter import messagebox

    return bool(messagebox.askyesno(APP_NAME, message))


def load_secrets() -> None:
    # macOS GUI/LaunchAgent apps don't inherit shell env vars, so secrets.json
    # is the primary credential path. Existing env vars always take precedence.
    if not SECRETS_FILE.exists():
        return

    try:
        with SECRETS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Failed to load secrets file %s: %s", SECRETS_FILE, exc)
        return

    if not isinstance(data, dict):
        log.warning("Secrets file %s is not a JSON object", SECRETS_FILE)
        return

    loaded = []
    for key in SECRET_KEYS:
        value = data.get(key)
        if value and not os.environ.get(key):
            os.environ[key] = str(value)
            loaded.append(key)

    if loaded:
        log.info("Loaded secrets from file: %s", ", ".join(loaded))


def ensure_secrets_file() -> None:
    if SECRETS_FILE.exists():
        return
    template = {key: "" for key in SECRET_KEYS}
    try:
        SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with SECRETS_FILE.open("w", encoding="utf-8") as f:
            json.dump(template, f, indent=4)
        log.info("Created secrets template at %s", SECRETS_FILE)
    except OSError as exc:
        log.warning("Failed to create secrets template: %s", exc)
