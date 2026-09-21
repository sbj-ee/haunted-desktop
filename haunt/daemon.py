"""Background spawn loop for haunt."""

from __future__ import annotations

import atexit
import logging
import os
import random
import signal
import sys
from pathlib import Path
from typing import Any

from gi.repository import GLib, Gtk

from haunt.config import load_config
from haunt.overlay import ensure_gtk, spawn_once


def _setup_logging(log_file: str) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr),
        ],
    )


def _write_pid(path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(os.getpid()), encoding="utf-8")

    def _clear() -> None:
        try:
            if p.is_file() and p.read_text(encoding="utf-8").strip() == str(os.getpid()):
                p.unlink()
        except OSError:
            pass

    atexit.register(_clear)


def read_pid(cfg: dict[str, Any] | None = None) -> int | None:
    cfg = cfg or load_config()
    path = Path(cfg["daemon"]["pid_file"])
    if not path.is_file():
        return None
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None
    # Still alive?
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    return pid


def stop_daemon(cfg: dict[str, Any] | None = None) -> bool:
    pid = read_pid(cfg)
    if pid is None:
        return False
    os.kill(pid, signal.SIGTERM)
    return True


class HauntApp:
    def __init__(self, cfg: dict[str, Any], once: bool = False) -> None:
        self.cfg = cfg
        self.once = once
        self._schedule_id: int | None = None

    def start(self) -> None:
        ensure_gtk()
        # Prefer X11 for input shaping when auto
        if self.cfg.get("display", {}).get("backend") == "x11":
            os.environ.setdefault("GDK_BACKEND", "x11")
        elif self.cfg.get("display", {}).get("backend") == "wayland":
            os.environ.setdefault("GDK_BACKEND", "wayland")

        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)

        if self.once:
            spawn_once(self.cfg)
            # Quit after overlays die — poll
            GLib.timeout_add(500, self._quit_when_idle)
        else:
            _write_pid(self.cfg["daemon"]["pid_file"])
            self._schedule_next()

        Gtk.main()

    def _on_signal(self, signum: int, _frame: object) -> None:
        logging.info("signal %s — shutting down", signum)
        Gtk.main_quit()

    def _quit_when_idle(self) -> bool:
        # Any top-level haunt windows still up?
        alive = [w for w in Gtk.Window.list_toplevels() if w.get_visible()]
        if not alive:
            Gtk.main_quit()
            return False
        return True

    def _schedule_next(self) -> None:
        sc = self.cfg.get("spawn", {})
        lo = float(sc.get("interval_min_s", 45))
        hi = float(sc.get("interval_max_s", 180))
        if hi < lo:
            lo, hi = hi, lo
        delay_ms = int(random.uniform(lo, hi) * 1000)
        logging.info("next haunt in %.1fs", delay_ms / 1000.0)
        self._schedule_id = GLib.timeout_add(delay_ms, self._spawn)

    def _spawn(self) -> bool:
        n = 1
        if random.random() < float(self.cfg.get("spawn", {}).get("double_chance", 0.0)):
            n = 2
        for _ in range(n):
            try:
                spawn_once(self.cfg)
                logging.info("spawned creature")
            except Exception:
                logging.exception("spawn failed")
        self._schedule_next()
        return False  # one-shot timer; we reschedule manually


def run_daemon(once: bool = False, config_path: str | None = None) -> None:
    from pathlib import Path

    from haunt.config import load_config

    cfg = load_config(Path(config_path) if config_path else None)
    _setup_logging(cfg["daemon"]["log_file"])
    if not once:
        existing = read_pid(cfg)
        if existing:
            raise SystemExit(f"haunted-desktop already running (pid {existing}). Use: haunt stop")
    logging.info("haunted-desktop starting (once=%s)", once)
    HauntApp(cfg, once=once).start()
