from __future__ import annotations

import logging
import threading

import pystray
from PIL import Image, ImageDraw

from macos.autostart import is_autostart_enabled, set_autostart
from shared.constants import (
    APP_NAME,
    APP_VERSION,
    CONFIG_FILE,
    LOG_FILE,
    SECRETS_FILE,
    resource_path,
)
from shared.platform_utils import ensure_secrets_file, notify, open_path
from shared.updater import check_for_update

log = logging.getLogger(__name__)


def _load_icon() -> Image.Image:
    icon_path = resource_path("assets/app.png")
    if icon_path.exists():
        return Image.open(icon_path)

    img = Image.new("RGBA", (64, 64), "#101820")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill="#76b900")
    draw.text((15, 24), "GFN", fill="white")
    return img


class TrayApp:
    # Settings are edited by opening config.json in the default editor.
    # Avoids running Tkinter off the main thread, which is unsafe with pystray's NSApplication.

    def __init__(self, service) -> None:
        self._service = service
        self._icon = pystray.Icon(APP_NAME, _load_icon(), APP_NAME, self._menu())
        log.info("Starting %s %s", APP_NAME, APP_VERSION)

    def _menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Edit Settings", lambda *_: open_path(CONFIG_FILE)),
            pystray.MenuItem("Edit Secrets", self._on_edit_secrets),
            pystray.MenuItem("Open Logs", lambda *_: open_path(LOG_FILE)),
            pystray.MenuItem("Check for Updates", self._on_check_updates),
            pystray.MenuItem(
                "Start at Login",
                self._on_toggle_autostart,
                checked=lambda _: is_autostart_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_close),
        )

    def _on_edit_secrets(self, *_) -> None:
        ensure_secrets_file()
        open_path(SECRETS_FILE)

    def _on_toggle_autostart(self, *_) -> None:
        if not set_autostart(not is_autostart_enabled()):
            notify("Could not update the Start at Login setting.", error=True)
        self._icon.update_menu()

    def _on_check_updates(self, *_) -> None:
        threading.Thread(target=check_for_update, args=(True,), daemon=True).start()

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
