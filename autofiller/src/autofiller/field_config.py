"""Load and cache field configuration from field_config.json."""

import json

from autofiller.config import Config


_field_config_cache: dict | None = None


def get_field_config() -> dict:
    """
    Load field configuration from field_config.json.

    Caches the result to avoid reading the file multiple times.
    Falls back to empty dict if file is missing or invalid.

    Returns:
        Dict with keys: 'field_values' and 'selectors' (may be empty)
    """
    global _field_config_cache

    if _field_config_cache is not None:
        return _field_config_cache

    default_config = {"field_values": {}, "selectors": {}}

    try:
        if Config.FIELD_CONFIG_FILE.exists():
            with open(Config.FIELD_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                _field_config_cache = {
                    "field_values": config.get("field_values", {}),
                    "selectors": config.get("selectors", {}),
                }
                return _field_config_cache
    except (json.JSONDecodeError, IOError) as e:  # noqa: BLE001
        print(f"Warning: Could not load field_config.json: {e}. Using defaults.")

    _field_config_cache = default_config
    return _field_config_cache
