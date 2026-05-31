from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import pystray
from PIL import Image, ImageDraw

from windows.autostart import is_autostart_enabled, set_autostart
from shared.config import load_config, save_config
from shared.constants import (
    ACTIVITY_TYPES,
    APP_NAME,
    APP_VERSION,
    CONFIG_FILE,
    DEFAULT_CONFIG,
    LOG_FILE,
    SECRETS_FILE,
    resource_path,
)
from shared.platform_utils import ensure_secrets_file, notify, open_path
from shared.updater import check_for_update

log = logging.getLogger(__name__)


def _load_icon() -> Image.Image:
    icon_path = resource_path("assets/app.ico")
    if icon_path.exists():
        return Image.open(icon_path)

    img = Image.new("RGBA", (64, 64), "#101820")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill="#76b900")
    draw.text((15, 24), "GFN", fill="white")
    return img


class ConfigEditor:
    def __init__(self, on_saved: callable):
        self._on_saved = on_saved
        self._thread: threading.Thread | None = None

    def open(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._show, daemon=True)
        self._thread.start()

    def _show(self) -> None:
        config = load_config()

        root = tk.Tk()
        root.title(f"{APP_NAME} Settings")
        root.resizable(False, False)

        icon_path = resource_path("assets/app.ico")
        if icon_path.exists():
            try:
                root.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        labels = {
            "check_interval_seconds": "Check Interval (seconds)",
            "default_image_url": "Default Image URL",
            "activity_type": "Activity Type",
            "check_for_updates": "Check for Updates",
        }

        fields: dict[str, tk.Widget] = {}

        for row, key in enumerate(DEFAULT_CONFIG):
            ttk.Label(frame, text=labels.get(key, key)).grid(
                row=row, column=0, sticky="w", pady=4,
            )

            if key == "activity_type":
                widget = ttk.Combobox(
                    frame, values=ACTIVITY_TYPES, state="readonly", width=44,
                )
                widget.set(str(config.get(key, DEFAULT_CONFIG[key])).upper())
            elif key == "check_for_updates":
                var = tk.BooleanVar(value=bool(config.get(key, DEFAULT_CONFIG[key])))
                ttk.Checkbutton(frame, variable=var).grid(
                    row=row, column=1, sticky="w", pady=4, padx=(12, 0),
                )
                fields[key] = var
                continue
            else:
                widget = ttk.Entry(frame, width=47)
                widget.insert(0, str(config.get(key, DEFAULT_CONFIG[key])))

            widget.grid(row=row, column=1, sticky="ew", pady=4, padx=(12, 0))
            fields[key] = widget

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(
            row=len(DEFAULT_CONFIG), column=0, columnspan=2, sticky="e", pady=(14, 0),
        )

        def save() -> None:
            updated = {}
            for key, widget in fields.items():
                value = widget.get()
                if isinstance(value, str):
                    value = value.strip()
                if key == "check_interval_seconds":
                    try:
                        value = max(5, int(value))
                    except ValueError:
                        messagebox.showerror(APP_NAME, "Check interval must be a number.")
                        return
                if key == "check_for_updates":
                    value = bool(value)
                updated[key] = value

            save_config(updated)
            self._on_saved()
            messagebox.showinfo(APP_NAME, "Settings saved.")

        ttk.Button(
            btn_frame, text="Open JSON",
            command=lambda: open_path(CONFIG_FILE),
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btn_frame, text="Save", command=save).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btn_frame, text="Close", command=root.destroy).grid(row=0, column=2)

        root.mainloop()


class TrayApp:
    def __init__(self, service) -> None:
        self._service = service
        self._editor = ConfigEditor(on_saved=service.reload_config)
        self._icon = pystray.Icon(APP_NAME, _load_icon(), APP_NAME, self._menu())
        log.info("Starting %s %s", APP_NAME, APP_VERSION)

    def _menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Edit Settings", lambda *_: self._editor.open()),
            pystray.MenuItem("Open Config JSON", lambda *_: open_path(CONFIG_FILE)),
            pystray.MenuItem("Edit Secrets", self._on_edit_secrets),
            pystray.MenuItem("Open Logs", lambda *_: open_path(LOG_FILE)),
            pystray.MenuItem("Check for Updates", self._on_check_updates),
            pystray.MenuItem(
                "Start with Windows",
                self._on_toggle_autostart,
                checked=lambda _: is_autostart_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Close", self._on_close),
        )

    def _on_edit_secrets(self, *_) -> None:
        ensure_secrets_file()
        open_path(SECRETS_FILE)

    def _on_toggle_autostart(self, *_) -> None:
        if not set_autostart(not is_autostart_enabled()):
            notify("Could not update auto-start setting.", error=True)
        self._icon.update_menu()

    def _on_check_updates(self, *_) -> None:
        threading.Thread(
            target=check_for_update, args=(True,), daemon=True,
        ).start()

    def _on_close(self, *_) -> None:
        log.info("Closing tray app")
        self._service.stop()
        self._icon.stop()

    def run(self) -> None:
        self._service.start()

        config = self._service.config
        if config.get("check_for_updates", True):
            threading.Timer(2.0, check_for_update).start()

        self._icon.run()
