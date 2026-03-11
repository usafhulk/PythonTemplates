"""
config_manager.py
=================
Configuration loader that reads settings from JSON, YAML (optional),
``.env`` / ``dotenv`` files, environment variables, or plain dicts.

Provides layered configuration with override priority:
  environment variables > explicit overrides > config file > defaults

Usage::

    from wingbrace.utilities import ConfigManager

    # Load from a JSON file
    cfg = ConfigManager.from_json("config/settings.json")
    db_host = cfg.get("database.host", default="localhost")

    # Load from environment variables (prefixed with APP_)
    cfg = ConfigManager.from_env(prefix="APP_")
    debug = cfg.get_bool("debug", default=False)

    # Layered: file + env overrides
    cfg = ConfigManager.from_json("config/settings.json").with_env_overrides(prefix="APP_")
"""

import json
import os
from typing import Any, Optional


class ConfigManager:
    """
    Read and access hierarchical configuration settings.

    Settings can be loaded from JSON files, environment variables,
    ``.env``-style files, or plain Python dicts.

    Nested keys are accessed with dot notation, e.g.
    ``cfg.get("database.host")``.

    Parameters
    ----------
    data:
        Initial configuration as a nested dictionary.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._config: dict[str, Any] = data or {}

    # ------------------------------------------------------------------
    # Class-level factories
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfigManager":
        """Create a ``ConfigManager`` from a plain dictionary."""
        return cls(data)

    @classmethod
    def from_json(cls, filepath: str) -> "ConfigManager":
        """
        Load configuration from a JSON file.

        Parameters
        ----------
        filepath:
            Path to the JSON configuration file.
        """
        with open(filepath, encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(data)

    @classmethod
    def from_yaml(cls, filepath: str) -> "ConfigManager":
        """
        Load configuration from a YAML file.

        Requires ``pyyaml`` (``pip install pyyaml``).

        Parameters
        ----------
        filepath:
            Path to the YAML configuration file.
        """
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "pyyaml is required to load YAML configs: pip install pyyaml"
            ) from exc
        with open(filepath, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return cls(data)

    @classmethod
    def from_env(cls, prefix: str = "", lowercase_keys: bool = True) -> "ConfigManager":
        """
        Build a ``ConfigManager`` from environment variables.

        Parameters
        ----------
        prefix:
            Only include variables whose names start with *prefix*.
            The prefix is stripped from the resulting keys.
        lowercase_keys:
            When ``True``, keys are lowercased (e.g. ``APP_DEBUG`` →
            ``debug``).
        """
        data: dict[str, Any] = {}
        for key, val in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
            clean_key = key[len(prefix):]
            if lowercase_keys:
                clean_key = clean_key.lower()
            data[clean_key] = val
        return cls(data)

    @classmethod
    def from_dotenv(cls, filepath: str = ".env") -> "ConfigManager":
        """
        Parse a ``.env``-style file into a ``ConfigManager``.

        Supports ``KEY=value`` lines, ``#`` comments, and quoted values.
        Does *not* require the ``python-dotenv`` package.

        Parameters
        ----------
        filepath:
            Path to the ``.env`` file.
        """
        data: dict[str, Any] = {}
        if not os.path.exists(filepath):
            return cls(data)
        with open(filepath, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                data[key] = val
        return cls(data)

    # ------------------------------------------------------------------
    # Layering
    # ------------------------------------------------------------------

    def with_env_overrides(
        self, prefix: str = "", lowercase_keys: bool = True
    ) -> "ConfigManager":
        """
        Return a new ``ConfigManager`` with environment variables layered
        on top of the current configuration.

        Environment variables take priority over existing values.
        """
        env_cfg = ConfigManager.from_env(prefix=prefix, lowercase_keys=lowercase_keys)
        merged = _deep_merge(self._config, env_cfg._config)
        return ConfigManager(merged)

    def merge(self, other: "ConfigManager") -> "ConfigManager":
        """
        Return a new ``ConfigManager`` with *other* merged on top.

        Values in *other* override matching keys in this instance.
        """
        merged = _deep_merge(self._config, other._config)
        return ConfigManager(merged)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot-notation.

        Parameters
        ----------
        key:
            Dot-separated key path, e.g. ``"database.host"``.
        value:
            Value to set.
        """
        parts = key.split(".")
        d = self._config
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value using dot-notation.

        Parameters
        ----------
        key:
            Dot-separated key path, e.g. ``"database.host"``.
        default:
            Returned when the key does not exist.
        """
        parts = key.split(".")
        d: Any = self._config
        for part in parts:
            if not isinstance(d, dict) or part not in d:
                return default
            d = d[part]
        return d

    def require(self, key: str) -> Any:
        """
        Like ``get`` but raises ``KeyError`` when the key is missing.

        Use for required configuration values that must be present.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Required config key {key!r} is missing.")
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Return *key* as an ``int``."""
        return int(self.get(key, default))

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Return *key* as a ``float``."""
        return float(self.get(key, default))

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Return *key* as a ``bool``.  Truthy strings: ``1, true, yes, on``."""
        val = self.get(key, default)
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("1", "true", "yes", "on")

    def get_list(self, key: str, default: list | None = None) -> list:
        """
        Return *key* as a list.

        If the stored value is a comma-separated string it is split
        automatically.
        """
        val = self.get(key, default or [])
        if isinstance(val, list):
            return val
        return [v.strip() for v in str(val).split(",") if v.strip()]

    def get_section(self, key: str) -> "ConfigManager":
        """
        Return a sub-section of the configuration as a new ``ConfigManager``.

        Parameters
        ----------
        key:
            Dot-separated key path to the sub-section.
        """
        section = self.get(key, {})
        return ConfigManager(section if isinstance(section, dict) else {})

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a copy of the raw configuration dictionary."""
        return dict(self._config)

    def to_json(self, filepath: str | None = None, indent: int = 2) -> str:
        """Serialise to JSON.  Optionally write to *filepath*."""
        output = json.dumps(self._config, indent=indent)
        if filepath:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(output)
        return output

    def __repr__(self) -> str:
        return f"ConfigManager({list(self._config.keys())})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base* (non-destructive)."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
