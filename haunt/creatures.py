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
}


def pick_creature(names: list[str]) -> str:
    valid = [n for n in names if n in PAINTERS]
    if not valid:
        valid = list(PAINTERS)
    # Bias toward amorphous shadow for meeting-safe default feel
    weights = []
    for n in valid:
        weights.append(2.5 if n == "shadow" else 1.0)
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
    _soft_fill(cr, opacity)
    PAINTERS[name](cr, float(w), float(h))
