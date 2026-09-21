"""haunt command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="haunt",
        description="haunted-desktop — subtle Linux overlay — random spooky silhouettes across the screen.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Config TOML (default: ~/.config/haunted-desktop/config.toml)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("start", help="Start the background haunt daemon")
    sub.add_parser("stop", help="Stop a running haunt daemon (kill switch)")
    sub.add_parser("status", help="Show whether haunt is running")
    p_once = sub.add_parser("once", help="Spawn one creature and exit")
    p_once.add_argument(
        "--creature",
        choices=["ghost", "bat", "cat", "spider", "shadow", "eyes"],
        default=None,
        help="Force a creature type",
    )
    sub.add_parser("init-config", help="Write default config to ~/.config/haunted-desktop/config.toml")

    args = parser.parse_args(argv)

    if args.cmd == "init-config":
        from haunt.config import ensure_user_config

        path = ensure_user_config()
        print(f"wrote {path}")
        return 0

    if args.cmd == "status":
        from haunt.config import load_config
        from haunt.daemon import read_pid

        cfg = load_config(args.config)
        pid = read_pid(cfg)
        if pid:
            print(f"running pid={pid}")
            return 0
        print("stopped")
        return 1

    if args.cmd == "stop":
        from haunt.config import load_config
        from haunt.daemon import stop_daemon

        cfg = load_config(args.config)
        if stop_daemon(cfg):
            print("stopped")
            return 0
        print("not running", file=sys.stderr)
        return 1

    if args.cmd == "start":
        from haunt.daemon import run_daemon

        run_daemon(once=False, config_path=str(args.config) if args.config else None)
        return 0

    if args.cmd == "once":
        from haunt.config import load_config
        from haunt.overlay import ensure_gtk, spawn_once  # pins Gtk 3.0 before gi import

        from gi.repository import GLib, Gtk

        cfg = load_config(args.config)
        ensure_gtk()
        win = spawn_once(cfg, creature=args.creature)

        def _poll() -> bool:
            if not win.get_visible():
                Gtk.main_quit()
                return False
            return True

        GLib.timeout_add(200, _poll)
        Gtk.main()
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
