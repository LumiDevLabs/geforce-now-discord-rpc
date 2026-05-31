from __future__ import annotations

import logging
import os
import sys
import threading

from shared.config import load_config
from shared.constants import (
    APP_DIR,
    APP_NAME,
    APP_RUN_VALUE,
    CONFIG_FILE,
    IS_MACOS,
    IS_WINDOWS,
    LOG_FILE,
)
from shared.discord_rpc import RpcManager
from shared.platform_utils import load_secrets, notify

if IS_WINDOWS:
    from windows import autostart, game_detection, tray
elif IS_MACOS:
    from macos import autostart, game_detection, tray
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

APP_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger(__name__)

_MUTEX_NAME = f"Global\\{APP_RUN_VALUE}_SingleInstance"
_mutex_handle: int | None = None
_lock_file = None


def _acquire_single_instance() -> bool:
    # Windows uses a named mutex; macOS/Linux use an exclusive flock on a lock
    # file. The handle is intentionally kept alive for the lifetime of the process.
    global _mutex_handle, _lock_file

    if IS_WINDOWS:
        import ctypes

        ERROR_ALREADY_EXISTS = 183
        handle = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            ctypes.windll.kernel32.CloseHandle(handle)
            return False
        _mutex_handle = handle
        return True

    import fcntl

    lock_path = APP_DIR / "instance.lock"
    handle = open(lock_path, "w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return False
    _lock_file = handle
    return True


class RpcService:
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
                    game = game_detection.get_active_gfn_game()

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
    load_secrets()

    if not _acquire_single_instance():
        location = "menu bar" if IS_MACOS else "system tray"
        notify(f"{APP_NAME} is already running in the {location}.")
        return

    autostart.sync_autostart_command()

    service = RpcService()
    app = tray.TrayApp(service)
    app.run()


if __name__ == "__main__":
    main()
