from __future__ import annotations

import logging
import os
import threading
from tkinter import messagebox

from autostart import sync_autostart_command
from config import load_config
from constants import APP_DIR, APP_NAME, CONFIG_FILE, LOG_FILE
from discord_rpc import RpcManager
from game_detection import get_active_gfn_game

APP_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger(__name__)


def _check_env_vars() -> bool:
    """Warn and exit if required environment variables are missing."""
    missing = [
        name for name in ("GFN_DISCORD_CLIENT_ID", "GFN_STEAMGRIDDB_API_KEY", "GFN_IMGBB_API_KEY")
        if not os.environ.get(name)
    ]
    if not missing:
        return True

    names = "\n".join(f"  - {n}" for n in missing)
    messagebox.showerror(
        APP_NAME,
        f"Missing required system environment variables:\n\n"
        f"{names}\n\n"
        f"Set them in Windows (Win + S → search \"environment variables\" →\n"
        f"Edit environment variables for your account),\n"
        f"then restart the app.",
    )
    return False


class RpcService:
    """Background service that polls for GFN games and updates Discord presence."""

    def __init__(self) -> None:
        self.config = load_config()
        self._config_mtime = self._get_config_mtime()
        self._manager = RpcManager(self.config)
        self._stop = threading.Event()
        self._lock = threading.RLock()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        log.info("Starting background service")
        self._thread.start()

    def stop(self) -> None:
        log.info("Stopping background service")
        self._stop.set()
        with self._lock:
            self._manager.disconnect()

    def reload_config(self) -> None:
        with self._lock:
            self.config = load_config()
            self._config_mtime = self._get_config_mtime()
            self._manager.update_config(self.config)
        log.info("Config reloaded from editor")

    def _get_config_mtime(self) -> float | None:
        try:
            return CONFIG_FILE.stat().st_mtime
        except OSError:
            return None

    def _maybe_reload_config(self) -> None:
        mtime = self._get_config_mtime()
        if mtime != self._config_mtime:
            self.config = load_config()
            self._config_mtime = mtime
            self._manager.update_config(self.config)
            log.info("Config reloaded (file changed)")

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                with self._lock:
                    self._maybe_reload_config()
                    game = get_active_gfn_game()

                    if game:
                        self._manager.update_presence(game)
                    else:
                        if self._manager.current_game is not None:
                            self._manager.clear_presence()
                        if self._manager.connected:
                            self._manager.disconnect()

                interval = max(5, int(self.config.get("check_interval_seconds", 15)))
            except Exception as exc:
                log.exception("Service loop error: %s", exc)
                interval = 15

            self._stop.wait(interval)


def main() -> None:
    if not _check_env_vars():
        return

    sync_autostart_command()

    service = RpcService()

    from tray import TrayApp

    app = TrayApp(service)
    app.run()


if __name__ == "__main__":
    main()
