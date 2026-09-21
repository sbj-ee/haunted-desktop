"""Transparent always-on-top click-through overlay window (GTK3 + Cairo)."""

from __future__ import annotations

import math
import os
import random
from typing import Any

import cairo

# gi requires DISPLAY / Wayland session
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from haunt.creatures import draw_creature, pick_creature


def _screen_size() -> tuple[int, int]:
    display = Gdk.Display.get_default()
    if display is None:
        return 1920, 1080
    mon = display.get_primary_monitor() or display.get_monitor(0)
    geo = mon.get_geometry()
    scale = mon.get_scale_factor()
    return geo.width * scale, geo.height * scale


def _apply_click_through(window: Gtk.Window) -> None:
    """Make the window ignore pointer input (X11; best-effort elsewhere)."""
    gdk_win = window.get_window()
    if gdk_win is None:
        return
    # Empty input shape => events pass through
    region = cairo.Region()
    try:
        gdk_win.input_shape_combine_region(region, 0, 0)
    except Exception:
        # Older Gdk API
        try:
            gdk_win.input_shape_combine_region(region)
        except Exception:
            pass


class CreatureOverlay(Gtk.Window):
    def __init__(self, cfg: dict[str, Any], creature: str | None = None) -> None:
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_keep_above(bool(cfg.get("display", {}).get("always_on_top", True)))
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)

        ccfg = cfg.get("creature", {})
        self.creature = creature or pick_creature(list(ccfg.get("set", ["ghost"])))
        self.opacity = float(ccfg.get("opacity", 0.55))
        speed = random.uniform(float(ccfg.get("speed_min", 0.08)), float(ccfg.get("speed_max", 0.22)))
        scale = random.uniform(float(ccfg.get("scale_min", 0.12)), float(ccfg.get("scale_max", 0.28)))
        lifetime = random.uniform(
            float(ccfg.get("lifetime_min_s", 6)), float(ccfg.get("lifetime_max_s", 14))
        )

        sw, sh = _screen_size()
        self.sw, self.sh = sw, sh
        self.box_h = max(48, int(sh * scale))
        self.box_w = max(48, int(self.box_h * 0.9))
        self.direction = random.choice([-1, 1])
        # Start just off-screen
        if self.direction > 0:
            self.x = -float(self.box_w)
        else:
            self.x = float(sw)
        # Prefer lower half / mid for crawling feel; bats higher
        if self.creature == "bat":
            self.y = random.uniform(sh * 0.05, sh * 0.45)
        elif self.creature == "shadow":
            self.y = sh - self.box_h - random.uniform(0, sh * 0.08)
        else:
            self.y = random.uniform(sh * 0.15, sh * 0.7)

        self.vx = self.direction * speed * sw  # px / s
        self.bob_amp = self.box_h * (0.06 if self.creature == "bat" else 0.02)
        self.bob_freq = random.uniform(0.25, 0.55)  # slow, natural drift
        self.t = 0.0
        self.lifetime = lifetime
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.box_w, self.box_h)
        draw_creature(self._surface, self.creature, self.opacity)

        self.set_default_size(self.box_w, self.box_h)
        self.move(int(self.x), int(self.y))
        self.connect("draw", self._on_draw)
        self.connect("realize", self._on_realize)

        self._tick_id = GLib.timeout_add(16, self._tick)  # ~60 Hz

    def _on_realize(self, *_args: object) -> None:
        _apply_click_through(self)

    def _on_draw(self, _widget: Gtk.Widget, cr: cairo.Context) -> bool:
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(self._surface, 0, 0)
        cr.paint()
        return False

    def _tick(self) -> bool:
        dt = 0.016
        self.t += dt
        if self.t >= self.lifetime:
            self.destroy()
            return False
        self.x += self.vx * dt
        bob = math.sin(self.t * self.bob_freq * 2 * math.pi) * self.bob_amp
        # Fade in/out
        fade = 1.0
        edge = 2.5  # soft fade in/out
        if self.t < edge:
            fade = self.t / edge
        elif self.t > self.lifetime - edge:
            fade = max(0.0, (self.lifetime - self.t) / edge)
        # Redraw with fade by adjusting opacity surface occasionally is expensive;
        # use window opacity when available.
        try:
            self.set_opacity(max(0.05, min(1.0, fade)))
        except Exception:
            pass
        self.move(int(self.x), int(self.y + bob))
        # Off the far side
        if self.direction > 0 and self.x > self.sw + self.box_w:
            self.destroy()
            return False
        if self.direction < 0 and self.x < -self.box_w * 2:
            self.destroy()
            return False
        self.queue_draw()
        return True


def spawn_once(cfg: dict[str, Any], creature: str | None = None) -> CreatureOverlay:
    win = CreatureOverlay(cfg, creature=creature)
    win.show_all()
    _apply_click_through(win)
    return win


def ensure_gtk() -> None:
    if os.environ.get("DISPLAY") is None and os.environ.get("WAYLAND_DISPLAY") is None:
        raise SystemExit(
            "haunt needs a graphical session (DISPLAY or WAYLAND_DISPLAY). "
            "X11 is recommended for reliable click-through."
        )
    # Force X11 backend when requested
    backend = os.environ.get("HAUNT_GDK_BACKEND")
    if backend:
        os.environ["GDK_BACKEND"] = backend
