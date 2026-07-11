"""
Layered configuration.

Precedence (lowest to highest):

    dataclass defaults  <  config file  <  environment (OSINT_*)  <  explicit overrides (CLI / kwargs)

A config file is optional. If none is given, the first of ``osint.toml``,
``osint.yaml``, ``osint.yml`` or ``osint.json`` found in the working directory
is used. TOML needs Python 3.11+ (or the ``tomli`` package); YAML needs
``pyyaml``; JSON always works.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, fields
from typing import Any, Dict

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; osint-cli-tool-skeleton/0.2; +https://github.com/soxoj/osint-cli-tool-skeleton)"
)

ENV_PREFIX = "OSINT_"
CONFIG_FILENAMES = ("osint.toml", "osint.yaml", "osint.yml", "osint.json")


@dataclass
class Settings:
    """Everything the engine needs, in one place."""

    #: Name of the plugin to run (see ``--list-plugins``).
    plugin: str = "http_title"
    #: Proxy URL, e.g. ``socks5://127.0.0.1:1080`` or ``http://host:8080``.
    proxy: str = ""
    #: Per-request total timeout, seconds.
    timeout: float = 100.0
    #: Maximum number of targets processed concurrently.
    concurrency: int = 10
    #: User-Agent for outgoing HTTP requests.
    user_agent: str = DEFAULT_USER_AGENT
    #: Optional Netscape/Mozilla-format cookie file.
    cookie_file: str = ""
    #: Disable the progress bar.
    no_progressbar: bool = False
    #: Disable coloured console output.
    no_color: bool = False
    #: Suppress console output entirely (library / piping friendly).
    silent: bool = False
    #: Logging level name (DEBUG/INFO/WARNING/ERROR).
    log_level: str = "ERROR"
    #: Plugin-specific options. Free-form; consumed by the plugin via
    #: ``self.options``.
    options: Dict[str, Any] = field(default_factory=dict)

    # -- construction helpers ----------------------------------------------
    @classmethod
    def load(
        cls,
        config_path: str | None = None,
        env: Dict[str, str] | None = None,
        overrides: Dict[str, Any] | None = None,
    ) -> "Settings":
        data: Dict[str, Any] = {}
        data.update(_read_config_file(config_path))
        data.update(_read_env(env if env is not None else os.environ))
        data.update({k: v for k, v in (overrides or {}).items() if v is not None})
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        known = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in data.items() if k in known}
        # Anything unknown is treated as a plugin option for convenience.
        extra = {k: v for k, v in data.items() if k not in known}
        settings = cls(**kwargs)
        if extra:
            settings.options = {**extra, **settings.options}
        return settings

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def _read_config_file(config_path: str | None) -> Dict[str, Any]:
    path = config_path
    if not path:
        for candidate in CONFIG_FILENAMES:
            if os.path.exists(candidate):
                path = candidate
                break
    if not path:
        return {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    text = open(path, "r", encoding="utf-8").read()
    if path.endswith(".json"):
        data = json.loads(text)
    elif path.endswith((".yaml", ".yml")):
        data = _load_yaml(text)
    elif path.endswith(".toml"):
        data = _load_toml(text)
    else:
        raise ValueError(f"Unsupported config format: {path}")

    # Allow a top-level [tool.osint] / {"osint": {...}} wrapper.
    if isinstance(data, dict):
        if "osint" in data and isinstance(data["osint"], dict):
            data = data["osint"]
        elif "tool" in data and isinstance(data.get("tool"), dict) and "osint" in data["tool"]:
            data = data["tool"]["osint"]
    return data or {}


def _load_toml(text: str) -> dict:
    try:
        import tomllib  # Python 3.11+
        return tomllib.loads(text)
    except ModuleNotFoundError:
        try:
            import tomli
            return tomli.loads(text)
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError(
                "Reading TOML config requires Python 3.11+ or `pip install tomli`."
            ) from exc


def _load_yaml(text: str) -> dict:
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("Reading YAML config requires `pip install pyyaml`.") from exc
    return yaml.safe_load(text) or {}


def _read_env(env: Dict[str, str]) -> Dict[str, Any]:
    """Map ``OSINT_*`` env vars onto settings.

    ``OSINT_PROXY``, ``OSINT_TIMEOUT``, ``OSINT_PLUGIN`` ... map to scalar
    fields. ``OSINT_OPTION_<KEY>`` populates ``options[<key>]``.
    """
    out: Dict[str, Any] = {}
    options: Dict[str, Any] = {}
    scalar_fields = {f.name for f in fields(Settings) if f.name != "options"}

    for raw_key, raw_val in env.items():
        if not raw_key.startswith(ENV_PREFIX):
            continue
        key = raw_key[len(ENV_PREFIX):].lower()
        if key.startswith("option_"):
            options[key[len("option_"):]] = _coerce(raw_val)
        elif key in scalar_fields:
            out[key] = _coerce(raw_val)

    if options:
        out["options"] = options
    return out


def _coerce(value: str) -> Any:
    """Best-effort string -> bool/int/float/str.

    Word-style booleans only (``true``/``false``/``yes``/``no``/``on``/``off``)
    so that numeric settings like ``OSINT_CONCURRENCY=1`` stay integers.
    """
    low = value.strip().lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
