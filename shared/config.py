from __future__ import annotations

import json
import logging

from shared.constants import APP_DIR, CONFIG_FILE, DEFAULT_CONFIG

log = logging.getLogger(__name__)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        log.info("Created default config at %s", CONFIG_FILE)
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log.exception("Failed to load config, falling back to defaults: %s", exc)
        return DEFAULT_CONFIG.copy()

    changed = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
            changed = True

    if changed:
        save_config(config)
        log.info("Backfilled missing config keys")

    return config


def save_config(config: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    log.info("Saved config to %s", CONFIG_FILE)
