import os
import sys
from pathlib import Path

APP_NAME = "GFN Discord RPC"
APP_VERSION = "1.2.0"
GITHUB_REPO = "LumiDevLabs/geforce-now-discord-rpc"
APP_RUN_VALUE = "GFNDiscordRPC"
BUNDLE_ID = "com.lumidevlabs.gfndiscordrpc"

# Built-in Discord application — users don't need to create their own.
DEFAULT_DISCORD_CLIENT_ID = "1504936563031805982"

IS_MACOS = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"


def _app_dir() -> Path:
    if IS_WINDOWS:
        return Path(os.getenv("APPDATA", Path.home())) / APP_NAME
    if IS_MACOS:
        return Path.home() / "Library" / "Application Support" / APP_NAME
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME


APP_DIR = _app_dir()
CONFIG_FILE = APP_DIR / "config.json"
CACHE_FILE = APP_DIR / "image_cache.json"
LOG_FILE = APP_DIR / "app.log"
SECRETS_FILE = APP_DIR / "secrets.json"

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# All three keys are optional — the app works out of the box without them.
# GFN_DISCORD_CLIENT_ID overrides the built-in application ID.
# GFN_STEAMGRIDDB_API_KEY + GFN_IMGBB_API_KEY enable per-game artwork; without
# them the default image is used.
SECRET_KEYS = (
    "GFN_DISCORD_CLIENT_ID",
    "GFN_STEAMGRIDDB_API_KEY",
    "GFN_IMGBB_API_KEY",
)

ACTIVITY_TYPES = ("PLAYING", "LISTENING", "WATCHING", "COMPETING")

DEFAULT_CONFIG = {
    "check_interval_seconds": 15,
    "default_image_url": "https://i.ibb.co/zWW3QqnT/default.png
    "activity_type": "PLAYING",
    "check_for_updates": True,
}

if IS_MACOS:
    # psutil reports the Mach-O executable name; the GeForce NOW app binary is
    # "GeForceNOW" inside "NVIDIA GeForce NOW.app".  Kept lowercase for matching.
    GFN_PROCESS_NAMES = frozenset({
        "geforcenow",
        "nvidia geforce now",
        "geforce now",
    })
else:
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


def clean_game_name(title: str) -> str:
    if not title:
        return ""
    cleaned = title.strip()
    lowered = cleaned.lower()
    for suffix in GFN_TITLE_SUFFIXES:
        if lowered.endswith(suffix):
            return cleaned[: -len(suffix)].strip()
    return cleaned


def resource_path(relative_path: str) -> Path:
    # _MEIPASS is set by PyInstaller onefile. For Nuitka standalone, __file__
    # resolves correctly. We also check the source root since this lives under shared/.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / relative_path

    module_dir = Path(__file__).resolve().parent
    candidates = [module_dir / relative_path, module_dir.parent / relative_path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]
