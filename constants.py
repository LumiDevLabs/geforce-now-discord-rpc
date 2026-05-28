import os
import sys
from pathlib import Path

APP_NAME = "GFN Discord RPC"
APP_VERSION = "1.0.0"
GITHUB_REPO = "LumiDevLabs/geforce-now-discord-rpc"
APP_RUN_VALUE = "GFNDiscordRPC"

APP_DIR = Path(os.getenv("APPDATA", Path.home())) / APP_NAME
CONFIG_FILE = APP_DIR / "config.json"
CACHE_FILE = APP_DIR / "image_cache.json"
LOG_FILE = APP_DIR / "app.log"

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

ACTIVITY_TYPES = ("PLAYING", "LISTENING", "WATCHING", "COMPETING")

DEFAULT_CONFIG = {
    "check_interval_seconds": 15,
    "default_image_url": "https://files.catbox.moe/61n0jc.png",
    "activity_type": "PLAYING",
    "check_for_updates": True,
}

GFN_PROCESS_NAMES = frozenset({"geforcenowstreamer.exe", "geforcenow.exe"})

GFN_IGNORED_TITLES = frozenset({
    "settings",
    "overlay",
    "main",
    "cefwindow",
    "geforce now",
    "geforce now streamer",
    "nvidia geforce now",
    "nvidia corporation",
    "geforcenow",
    "geforce-now",
    "crashexit",
    "system",
})

GFN_TITLE_SUFFIXES = (
    " bei geforce now",
    " on geforce now",
    " - geforce now",
    " geforce now",
)


def resource_path(relative_path: str) -> Path:
    """Resolve a path relative to the app bundle (PyInstaller/Nuitka) or source root."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path
