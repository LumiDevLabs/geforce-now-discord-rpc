"""Cross-platform helpers for opening files, showing dialogs, and loading secrets.

These wrap the platform-specific bits so the rest of the app stays free of
``sys.platform`` branches.  On Windows we use ``os.startfile`` and Tk dialogs;
on macOS we shell out to ``open`` and ``osascript`` (which avoids mixing Tk with
pystray's NSApplication on the main thread).
"""

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
    """Open a file, folder, or URL with the OS default handler."""
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
    """Show a native macOS dialog and return the clicked button (or None on cancel)."""
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


def notify(message: str, error: bool = False) -> None:
    """Show an informational or error dialog to the user."""
    if IS_MACOS:
        _osascript_dialog(message, buttons=["OK"], default="OK", error=error)
        return

    from tkinter import messagebox

    if error:
        messagebox.showerror(APP_NAME, message)
    else:
        messagebox.showinfo(APP_NAME, message)


def ask_yes_no(message: str) -> bool:
    """Ask a yes/no question and return True if the user chose yes."""
    if IS_MACOS:
        answer = _osascript_dialog(
            message, buttons=["No", "Yes"], default="Yes", error=False
        )
        return answer == "Yes"

    from tkinter import messagebox

    return bool(messagebox.askyesno(APP_NAME, message))


def load_secrets() -> None:
    """Populate ``os.environ`` from ``secrets.json`` for keys that aren't already set.

    macOS GUI/LaunchAgent apps do not inherit shell environment variables, so a
    JSON file in the app data directory is the user-friendly way to supply the
    Discord/SteamGridDB/imgbb credentials.  Existing OS environment variables
    take precedence, keeping the original Windows workflow intact.
    """
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
    """Create a template ``secrets.json`` if it doesn't exist yet."""
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
