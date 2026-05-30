import os
import sys
from pathlib import Path

APP_NAME = "GFN Discord RPC"
APP_VERSION = "1.0.1"
GITHUB_REPO = "LumiDevLabs/geforce-now-discord-rpc"
APP_RUN_VALUE = "GFNDiscordRPC"
BUNDLE_ID = "com.lumidevlabs.gfndiscordrpc"

IS_MACOS = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"


def _app_dir() -> Path:
    """Per-user data directory for config, cache, logs, and secrets."""
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

SECRET_KEYS = (
    "GFN_DISCORD_CLIENT_ID",
    "GFN_STEAMGRIDDB_API_KEY",
    "GFN_IMGBB_API_KEY",
)

ACTIVITY_TYPES = ("PLAYING", "LISTENING", "WATCHING", "COMPETING")

DEFAULT_CONFIG = {
    "check_interval_seconds": 15,
    "default_image_url": "https://files.catbox.moe/61n0jc.png",
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
    """Strip GeForce NOW suffixes from a window title."""
    if not title:
        return ""
    cleaned = title.strip()
    lowered = cleaned.lower()
    for suffix in GFN_TITLE_SUFFIXES:
        if lowered.endswith(suffix):
            return cleaned[: -len(suffix)].strip()
    return cleaned


def resource_path(relative_path: str) -> Path:
    """Resolve a path relative to the app bundle (PyInstaller/Nuitka) or source root.

    For a Nuitka standalone build the data files live next to the compiled
    module, so ``__file__``'s parent resolves correctly.  ``_MEIPASS`` covers
    PyInstaller onefile.  We also check the source-tree root since this module
    now lives under ``shared/``.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / relative_path

    module_dir = Path(__file__).resolve().parent
    candidates = [module_dir / relative_path, module_dir.parent / relative_path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]
