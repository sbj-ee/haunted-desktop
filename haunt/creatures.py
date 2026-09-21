"""Cairo silhouette painters — soft, natural, meeting-safe shadows."""

from __future__ import annotations

import math
import random
from typing import Callable

import cairo

Painter = Callable[[cairo.Context, float, float], None]


def _ellipse(cr: cairo.Context, cx: float, cy: float, rx: float, ry: float) -> None:
    cr.save()
    cr.translate(cx, cy)
    cr.scale(max(rx, 0.01), max(ry, 0.01))
    cr.arc(0, 0, 1.0, 0, 2 * math.pi)
    cr.restore()


def _soft_fill(cr: cairo.Context, opacity: float) -> None:
    """Near-black with slight cool tint — reads as shadow, not cartoon ink."""
    cr.set_source_rgba(0.07, 0.06, 0.09, max(0.05, min(1.0, opacity)))


def _glow_eye(cr: cairo.Context, cx: float, cy: float, rx: float, ry: float, peak: float) -> None:
    """Dim cool-amber radial glow — not neon, not cartoon."""
    # Outer haze
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, max(rx, ry) * 2.2)
    g.add_color_stop_rgba(0.0, 0.72, 0.62, 0.38, peak * 0.55)
    g.add_color_stop_rgba(0.35, 0.55, 0.48, 0.28, peak * 0.28)
    g.add_color_stop_rgba(1.0, 0.2, 0.18, 0.12, 0.0)
    cr.set_source(g)
    _ellipse(cr, cx, cy, rx * 2.0, ry * 2.0)
    cr.fill()
    # Soft core (still dim)
    g2 = cairo.RadialGradient(cx, cy, 0, cx, cy, max(rx, ry))
    g2.add_color_stop_rgba(0.0, 0.85, 0.78, 0.55, peak)
    g2.add_color_stop_rgba(0.55, 0.65, 0.55, 0.32, peak * 0.35)
    g2.add_color_stop_rgba(1.0, 0.3, 0.25, 0.15, 0.0)
    cr.set_source(g2)
    _ellipse(cr, cx, cy, rx, ry)
    cr.fill()


def paint_eyes(cr: cairo.Context, w: float, h: float, opacity: float = 0.22) -> None:
    """Lone pair of dim glowing eyes — sparse meeting-safe easter egg."""
    cr.save()
    # Peak alpha stays low even if config opacity is raised
    peak = max(0.10, min(0.48, opacity * 1.05))
    cy = h * 0.48
    # Slightly uneven spacing / height reads more natural
    spacing = w * random.uniform(0.14, 0.22)
    rx = w * random.uniform(0.028, 0.042)
    ry = rx * random.uniform(0.85, 1.15)
    y_jitter = h * 0.01
    _glow_eye(cr, w * 0.5 - spacing, cy - y_jitter, rx, ry, peak)
    _glow_eye(cr, w * 0.5 + spacing, cy + y_jitter * 0.5, rx * 0.95, ry * 1.05, peak * 0.92)
    cr.restore()


def paint_eyes_accent(cr: cairo.Context, w: float, h: float, opacity: float) -> None:
    """Tiny eye pair nested in a shadow silhouette (rare accent)."""
    cr.save()
    peak = max(0.06, min(0.32, opacity * 0.75))
    cx = w * random.uniform(0.35, 0.55)
    cy = h * random.uniform(0.55, 0.68)
    spacing = w * 0.045
    rx = w * 0.012
    ry = rx * 1.1
    _glow_eye(cr, cx - spacing, cy, rx, ry, peak)
    _glow_eye(cr, cx + spacing, cy, rx * 0.95, ry, peak * 0.9)
    cr.restore()


def paint_ghost(cr: cairo.Context, w: float, h: float) -> None:
    """Soft vertical wisp — no face cutouts (too cartoony on camera)."""
    cr.save()
    cr.translate(w * 0.5, h * 0.12)
    cr.move_to(-w * 0.18, h * 0.12)
    cr.curve_to(-w * 0.22, 0, w * 0.22, 0, w * 0.18, h * 0.12)
    cr.line_to(w * 0.16, h * 0.68)
    for i in range(4):
        x0 = w * 0.16 - (w * 0.32) * (i / 4)
        x1 = w * 0.16 - (w * 0.32) * ((i + 0.5) / 4)
        x2 = w * 0.16 - (w * 0.32) * ((i + 1) / 4)
        y_dip = h * (0.74 if i % 2 == 0 else 0.68)
        cr.curve_to(x0, h * 0.68, x1, y_dip, x2, h * 0.68)
    cr.close_path()
    cr.fill()
    cr.restore()


def paint_bat(cr: cairo.Context, w: float, h: float) -> None:
    """Distant bat blot — fused wings, no ear spikes."""
    cr.save()
    cr.translate(w * 0.5, h * 0.48)
    _ellipse(cr, 0, 0, w * 0.05, h * 0.07)
    cr.fill()
    for side in (-1, 1):
        cr.move_to(0, 0)
        cr.curve_to(side * w * 0.12, -h * 0.18, side * w * 0.28, -h * 0.02, side * w * 0.34, h * 0.02)
        cr.curve_to(side * w * 0.22, h * 0.06, side * w * 0.08, h * 0.03, 0, 0)
        cr.fill()
    cr.restore()


def paint_cat(cr: cairo.Context, w: float, h: float) -> None:
    """Low crouching shadow — ears only as soft triangles."""
    cr.save()
    cr.translate(w * 0.48, h * 0.62)
    _ellipse(cr, 0, 0, w * 0.14, h * 0.08)
    cr.fill()
    cr.arc(-w * 0.16, -h * 0.05, w * 0.07, 0, 2 * math.pi)
    cr.fill()
    for tip, side in ((-w * 0.22, -1), (-w * 0.10, 1)):
        cr.move_to(tip, -h * 0.08)
        cr.line_to(tip + side * w * 0.025, -h * 0.18)
        cr.line_to(tip + side * w * 0.055, -h * 0.06)
        cr.close_path()
        cr.fill()
    cr.set_line_width(w * 0.025)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(w * 0.12, 0)
    cr.curve_to(w * 0.2, -h * 0.12, w * 0.24, h * 0.08, w * 0.28, -h * 0.02)
    cr.stroke()
    cr.restore()


def paint_spider(cr: cairo.Context, w: float, h: float) -> None:
    """Tiny mote with faint legs — reads as dust mote until you look."""
    cr.save()
    cr.translate(w * 0.5, h * 0.55)
    cr.arc(0, 0, w * 0.045, 0, 2 * math.pi)
    cr.fill()
    cr.set_line_width(max(1.0, w * 0.012))
    for i in range(3):
        ang = -0.45 + i * 0.4
        for side in (-1, 1):
            cr.move_to(side * w * 0.03, 0)
            cr.curve_to(
                side * w * 0.12,
                -h * (0.08 + ang * 0.05),
                side * w * 0.18,
                h * (0.02 + i * 0.03),
                side * w * 0.22,
                h * (0.06 + i * 0.04),
            )
            cr.stroke()
    cr.restore()


def paint_shadow(cr: cairo.Context, w: float, h: float) -> None:
    """Floor-hugging amorphous shade — most natural / meeting-safe."""
    cr.save()
    cr.translate(0, h * 0.62)
    cr.move_to(0, h * 0.12)
    cr.curve_to(w * 0.12, 0, w * 0.28, -h * 0.08, w * 0.42, -h * 0.02)
    cr.curve_to(w * 0.55, h * 0.06, w * 0.7, -h * 0.1, w * 0.85, 0)
    cr.curve_to(w * 0.92, h * 0.1, w * 0.65, h * 0.2, w * 0.38, h * 0.16)
    cr.curve_to(w * 0.18, h * 0.14, w * 0.05, h * 0.18, 0, h * 0.12)
    cr.close_path()
    cr.fill()
    cr.restore()


PAINTERS: dict[str, Painter] = {
    "ghost": paint_ghost,
    "bat": paint_bat,
    "cat": paint_cat,
    "spider": paint_spider,
    "shadow": paint_shadow,
    # eyes drawn via draw_creature (needs opacity for glow peak)
}

CREATURE_NAMES = ["ghost", "bat", "cat", "spider", "shadow", "eyes"]


def pick_creature(names: list[str]) -> str:
    valid = [n for n in names if n in CREATURE_NAMES]
    if not valid:
        valid = list(CREATURE_NAMES)
    # Bias: shadow most common; eyes rarer than the rest
    weight_map = {
        "shadow": 1.6,
        "ghost": 1.2,
        "bat": 1.1,
        "cat": 1.0,
        "spider": 0.9,
        "eyes": 1.0,
    }
    weights = [weight_map.get(n, 1.0) for n in valid]
    return random.choices(valid, weights=weights, k=1)[0]


def draw_creature(
    surface: cairo.ImageSurface,
    name: str,
    opacity: float,
) -> None:
    w, h = surface.get_width(), surface.get_height()
    cr = cairo.Context(surface)
    cr.set_operator(cairo.OPERATOR_CLEAR)
    cr.paint()
    cr.set_operator(cairo.OPERATOR_OVER)
    if name == "eyes":
        paint_eyes(cr, float(w), float(h), opacity)
        return
    _soft_fill(cr, opacity)
    painter = PAINTERS.get(name, paint_shadow)
    painter(cr, float(w), float(h))
    # Rare dim eyes nested in a floor shadow
    if name == "shadow" and random.random() < 0.12:
        paint_eyes_accent(cr, float(w), float(h), opacity)
