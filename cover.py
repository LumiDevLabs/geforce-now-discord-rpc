from __future__ import annotations

import base64
import io
import json
import logging
import os
import re

import requests
from PIL import Image

from constants import CACHE_FILE, DEFAULT_CONFIG

log = logging.getLogger(__name__)

STEAMGRIDDB_API_KEY = os.environ.get("GFN_STEAMGRIDDB_API_KEY", "")
STEAMGRIDDB_BASE = "https://www.steamgriddb.com/api/v2"

IMGBB_API_KEY = os.environ.get("GFN_IMGBB_API_KEY", "")
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

DISCORD_SUPPORTED = frozenset({"png", "jpg", "jpeg", "gif", "webp"})

_EDITION_PATTERN = re.compile(
    r"\s*[-–—:]?\s*("
    r"enhanced\s+edition"
    r"|definitive\s+edition"
    r"|game\s+of\s+the\s+year\s+edition"
    r"|goty\s+edition"
    r"|deluxe\s+edition"
    r"|ultimate\s+edition"
    r"|complete\s+edition"
    r"|gold\s+edition"
    r"|premium\s+edition"
    r"|special\s+edition"
    r"|anniversary\s+edition"
    r"|legendary\s+edition"
    r"|royal\s+edition"
    r"|standard\s+edition"
    r"|digital\s+edition"
    r"|collector'?s?\s+edition"
    r"|limited\s+edition"
    r"|director'?s?\s+cut"
    r"|final\s+cut"
    r"|remastered"
    r"|remake"
    r"|hd\s+remaster"
    r"|next[\s-]gen\s+(?:update|edition|version)"
    r")\s*$",
    re.IGNORECASE,
)

_TRAILING_YEAR = re.compile(r"\s*\(\d{4}\)\s*$")


def _normalize_game_name(name: str) -> str:
    """Strip edition/version suffixes so the API search matches the base game."""
    cleaned = _EDITION_PATTERN.sub("", name)
    cleaned = _TRAILING_YEAR.sub("", cleaned)
    return cleaned.strip() or name


def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        log.info("Loaded image cache (%d entries)", len(data))
        return data
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Failed to load image cache: %s", exc)
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4)
    except OSError as exc:
        log.warning("Failed to save image cache: %s", exc)


_cache: dict | None = None


def _get_cache() -> dict:
    global _cache
    if _cache is None:
        _cache = _load_cache()
    return _cache


def _url_extension(url: str) -> str:
    """Extract the file extension from a URL, lowercased, without the dot."""
    path = url.split("?")[0].split("#")[0]
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return ext


def _to_png_bytes(raw: bytes) -> bytes:
    """Convert any Pillow-readable image bytes to PNG bytes."""
    img = Image.open(io.BytesIO(raw))
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _upload_to_imgbb(image_bytes: bytes, name: str) -> str | None:
    """Upload raw image bytes to imgbb and return the permanent display URL."""
    if not IMGBB_API_KEY:
        log.warning("GFN_IMGBB_API_KEY not set, skipping imgbb upload")
        return None

    b64 = base64.b64encode(image_bytes).decode()
    try:
        resp = requests.post(
            IMGBB_UPLOAD_URL,
            data={"key": IMGBB_API_KEY, "name": name, "image": b64},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.warning("imgbb upload failed for '%s': %s", name, exc)
        return None

    url = data.get("data", {}).get("display_url")
    if url:
        log.info("Uploaded '%s' to imgbb: %s", name, url)
    else:
        log.warning("imgbb response missing display_url for '%s': %s", name, data)
    return url or None


def _download_and_upload(source_url: str, game_name: str) -> str | None:
    """Download an image from source_url, convert to PNG if needed, upload to imgbb."""
    try:
        resp = requests.get(source_url, timeout=15)
        resp.raise_for_status()
        raw = resp.content
    except requests.RequestException as exc:
        log.warning("Failed to download image for '%s': %s", game_name, exc)
        return None

    ext = _url_extension(source_url)
    if ext not in DISCORD_SUPPORTED:
        log.info("Converting '%s' image from %s to PNG", game_name, ext or "unknown")
        try:
            raw = _to_png_bytes(raw)
        except Exception as exc:
            log.warning("Image conversion failed for '%s': %s", game_name, exc)
            return None

    return _upload_to_imgbb(raw, game_name)


def _search_steamgriddb(game_name: str) -> int | None:
    """Return the SteamGridDB game ID for the best autocomplete match."""
    headers = {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}
    try:
        resp = requests.get(
            f"{STEAMGRIDDB_BASE}/search/autocomplete/{game_name}",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.warning("SteamGridDB search failed for '%s': %s", game_name, exc)
        return None

    if not data.get("success") or not data.get("data"):
        log.info("No SteamGridDB results for '%s'", game_name)
        return None

    return data["data"][0].get("id")


def _fetch_steamgriddb_url(game_id: int, endpoint: str) -> str | None:
    """Return the first image URL from a SteamGridDB endpoint for a game."""
    headers = {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}
    try:
        resp = requests.get(
            f"{STEAMGRIDDB_BASE}/{endpoint}/game/{game_id}",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.warning("SteamGridDB %s fetch failed for game %s: %s", endpoint, game_id, exc)
        return None

    if data.get("success") and data.get("data"):
        return data["data"][0].get("url")
    return None


def _try_steamgriddb_endpoints(game_id: int, game_name: str) -> str | None:
    """Try each image endpoint for a game ID and return the first successful imgbb URL."""
    for endpoint in ("icons", "grids", "heroes", "logos"):
        source_url = _fetch_steamgriddb_url(game_id, endpoint)
        if not source_url:
            continue

        log.info("Found %s image for '%s', uploading to imgbb...", endpoint, game_name)
        permanent_url = _download_and_upload(source_url, game_name)
        if permanent_url:
            return permanent_url

        log.warning("imgbb upload failed for %s image, trying next endpoint", endpoint)
    return None


def _resolve_image_url(game_name: str) -> str | None:
    """
    Find the best image for a game, upload it to imgbb, and return the permanent URL.

    Tries the normalized (base) game name first for better search accuracy,
    then falls back to the full title if the names differ.
    """
    if not STEAMGRIDDB_API_KEY:
        log.warning("GFN_STEAMGRIDDB_API_KEY not set, skipping artwork lookup")
        return None

    normalized = _normalize_game_name(game_name)
    names_to_try = [normalized]
    if normalized != game_name:
        log.info("Normalized '%s' → '%s' for artwork lookup", game_name, normalized)
        names_to_try.append(game_name)

    for search_name in names_to_try:
        game_id = _search_steamgriddb(search_name)
        if not game_id:
            continue
        result = _try_steamgriddb_endpoints(game_id, game_name)
        if result:
            return result

    return None


def get_game_artwork(game_name: str, default_image: str | None = None) -> dict:
    """Return {"image_url": ..., "store_url": ...} for a game, using cache."""
    cache = _get_cache()

    cached = cache.get(game_name)
    if isinstance(cached, dict):
        log.debug("Cache hit for '%s'", game_name)
        return cached

    log.info("Looking up artwork for '%s'", game_name)
    image_url = _resolve_image_url(game_name)
    fallback = default_image or DEFAULT_CONFIG["default_image_url"]

    result = {
        "image_url": image_url or fallback,
        "store_url": None,
    }

    cache[game_name] = result
    _save_cache(cache)
    return result
