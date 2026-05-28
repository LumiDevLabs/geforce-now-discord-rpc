from __future__ import annotations

import logging
import os
import time

from cover import get_game_artwork

log = logging.getLogger(__name__)

DISCORD_CLIENT_ID = os.environ.get("GFN_DISCORD_CLIENT_ID", "")


def _resolve_activity_type(name: str):
    from pypresence.types import ActivityType

    return getattr(ActivityType, name.upper(), ActivityType.PLAYING)


class RpcManager:
    def __init__(self, config: dict):
        self.rpc = None
        self.connected = False
        self.current_game: str | None = None
        self.start_time: int | None = None
        self.config = config

    def update_config(self, config: dict) -> None:
        self.config = config

    def connect(self) -> bool:
        if self.connected:
            return True
        if not DISCORD_CLIENT_ID:
            log.warning("DISCORD_CLIENT_ID not set, cannot connect")
            return False

        try:
            from pypresence import Presence

            self.rpc = Presence(DISCORD_CLIENT_ID)
            self.rpc.connect()
            self.connected = True
            log.info("Connected to Discord")
            return True
        except Exception as exc:
            log.warning("Discord connection failed: %s", exc)
            self.connected = False
            self.rpc = None
            return False

    def disconnect(self) -> None:
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
            self.rpc = None
        if self.connected:
            log.info("Disconnected from Discord")
        self.connected = False

    def update_presence(self, game_name: str) -> None:
        if not self.connect():
            return

        if self.current_game != game_name:
            self.current_game = game_name
            self.start_time = int(time.time())
            log.info("Active game changed to '%s'", game_name)

        default_image = self.config.get("default_image_url", "")
        artwork = get_game_artwork(game_name, default_image=default_image)
        image_url = artwork["image_url"]

        activity_type = self.config.get("activity_type", "PLAYING")

        try:
            self.rpc.update(
                name=game_name,
                activity_type=_resolve_activity_type(activity_type),
                details=game_name,
                large_image=image_url or None,
                large_text=game_name if image_url else None,
                start=self.start_time,
            )
            log.info("Updated Discord presence: %s", game_name)
        except Exception as exc:
            log.warning("Discord presence update failed: %s", exc)
            self.connected = False

    def clear_presence(self) -> None:
        if self.connected and self.rpc:
            try:
                self.rpc.clear()
                log.info("Cleared Discord presence")
            except Exception:
                self.connected = False
        self.current_game = None
        self.start_time = None
