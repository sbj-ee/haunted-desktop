"""Load and merge haunted-desktop configuration."""

from __future__ import annotations

import os
import tomllib
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(__file__).with_name("config.default.toml")
_XDG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
USER_PATH = _XDG / "haunted-desktop" / "config.toml"
# Legacy path from early "haunt" name
LEGACY_USER_PATH = _XDG / "haunt" / "config.toml"


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Path | None = None) -> dict[str, Any]:
    with DEFAULT_PATH.open("rb") as f:
        cfg = tomllib.load(f)
    user = path
    if user is None:
        if USER_PATH.is_file():
            user = USER_PATH
        elif LEGACY_USER_PATH.is_file():
            user = LEGACY_USER_PATH
    if user is not None and Path(user).is_file():
        with Path(user).open("rb") as f:
            cfg = _deep_merge(cfg, tomllib.load(f))
    for key in ("pid_file", "log_file"):
        if key in cfg.get("daemon", {}):
            cfg["daemon"][key] = str(Path(cfg["daemon"][key]).expanduser())
    return cfg


def ensure_user_config() -> Path:
    """Write default config if missing; return path."""
    USER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not USER_PATH.exists():
        USER_PATH.write_text(DEFAULT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return USER_PATH
