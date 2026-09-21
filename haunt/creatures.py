"""Cairo silhouette painters for haunt creatures."""

from __future__ import annotations

import math
import random
from typing import Callable

import cairo

Painter = Callable[[cairo.Context, float, float], None]

def _ellipse(cr: cairo.Context, cx: float, cy: float, rx: float, ry: float) -> None:
    cr.save()
    cr.translate(cx, cy)
    cr.scale(rx, ry)
    cr.arc(0, 0, 1.0, 0, 2 * math.pi)
    cr.restore()



def paint_ghost(cr: cairo.Context, w: float, h: float) -> None:
    cr.save()
    cr.translate(w * 0.5, h * 0.08)
    # Body
    cr.move_to(-w * 0.28, h * 0.15)
    cr.curve_to(-w * 0.35, 0, w * 0.35, 0, w * 0.28, h * 0.15)
    cr.line_to(w * 0.28, h * 0.72)
    # Wavy hem
    steps = 5
    for i in range(steps):
        x0 = w * 0.28 - (w * 0.56) * (i / steps)
        x1 = w * 0.28 - (w * 0.56) * ((i + 0.5) / steps)
        x2 = w * 0.28 - (w * 0.56) * ((i + 1) / steps)
        y_dip = h * (0.82 if i % 2 == 0 else 0.72)
        cr.curve_to(x0, h * 0.72, x1, y_dip, x2, h * 0.72)
    cr.close_path()
    cr.fill()
    # Eyes (cutouts via destination-out later — draw as holes with operator)
    cr.set_operator(cairo.OPERATOR_CLEAR)
    for ex in (-w * 0.1, w * 0.1):
        cr.arc(ex, h * 0.28, w * 0.045, 0, 2 * math.pi)
        cr.fill()
    # Mouth
    cr.arc(0, h * 0.42, w * 0.06, 0.15 * math.pi, 0.85 * math.pi)
    cr.set_line_width(w * 0.025)
    cr.stroke()
    cr.restore()


def paint_bat(cr: cairo.Context, w: float, h: float) -> None:
    cr.save()
    cr.translate(w * 0.5, h * 0.45)
    # Body
    _ellipse(cr, 0, 0, w * 0.08, h * 0.12)
    cr.fill()
    # Wings
    for side in (-1, 1):
        cr.move_to(0, 0)
        cr.curve_to(side * w * 0.15, -h * 0.25, side * w * 0.35, -h * 0.05, side * w * 0.42, h * 0.02)
        cr.curve_to(side * w * 0.28, h * 0.08, side * w * 0.12, h * 0.05, 0, 0)
        cr.fill()
    # Ears
    for side in (-1, 1):
        cr.move_to(side * w * 0.02, -h * 0.08)
        cr.line_to(side * w * 0.05, -h * 0.18)
        cr.line_to(side * w * 0.08, -h * 0.06)
        cr.close_path()
        cr.fill()
    cr.restore()


def paint_cat(cr: cairo.Context, w: float, h: float) -> None:
    cr.save()
    cr.translate(w * 0.45, h * 0.55)
    # Body
    _ellipse(cr, 0, 0, w * 0.18, h * 0.12)
    cr.fill()
    # Head
    cr.arc(-w * 0.2, -h * 0.08, w * 0.1, 0, 2 * math.pi)
    cr.fill()
    # Ears
    for side, tip in ((-1, -w * 0.28), (1, -w * 0.12)):
        cr.move_to(tip, -h * 0.12)
        cr.line_to(tip + side * w * 0.04, -h * 0.28)
        cr.line_to(tip + side * w * 0.08, -h * 0.1)
        cr.close_path()
        cr.fill()
    # Tail
    cr.set_line_width(w * 0.035)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(w * 0.16, 0)
    cr.curve_to(w * 0.28, -h * 0.2, w * 0.32, h * 0.15, w * 0.38, -h * 0.05)
    cr.stroke()
    # Eyes clear
    cr.set_operator(cairo.OPERATOR_CLEAR)
    for ex in (-w * 0.24, -w * 0.16):
        cr.arc(ex, -h * 0.09, w * 0.018, 0, 2 * math.pi)
        cr.fill()
    cr.restore()


def paint_spider(cr: cairo.Context, w: float, h: float) -> None:
    cr.save()
    cr.translate(w * 0.5, h * 0.55)
    cr.arc(0, 0, w * 0.08, 0, 2 * math.pi)
    cr.fill()
    cr.arc(0, -h * 0.08, w * 0.05, 0, 2 * math.pi)
    cr.fill()
    cr.set_line_width(w * 0.02)
    for i in range(4):
        ang = -0.6 + i * 0.35
        for side in (-1, 1):
            cr.move_to(side * w * 0.06, -h * 0.02)
            cr.curve_to(
                side * w * 0.2,
                -h * (0.15 + ang * 0.1),
                side * w * 0.28,
                h * (0.05 + i * 0.04),
                side * w * 0.32,
                h * (0.12 + i * 0.05),
            )
            cr.stroke()
    cr.restore()


def paint_shadow(cr: cairo.Context, w: float, h: float) -> None:
    """Amorphous creeping shadow blob."""
    cr.save()
    cr.translate(0, h * 0.55)
    cr.move_to(0, h * 0.2)
    cr.curve_to(w * 0.1, 0, w * 0.3, -h * 0.15, w * 0.45, -h * 0.05)
    cr.curve_to(w * 0.6, h * 0.1, w * 0.75, -h * 0.2, w * 0.9, 0)
    cr.curve_to(w * 0.95, h * 0.15, w * 0.7, h * 0.35, w * 0.4, h * 0.3)
    cr.curve_to(w * 0.2, h * 0.28, w * 0.05, h * 0.35, 0, h * 0.2)
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
    return random.choice(valid)


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
    cr.set_source_rgba(0.05, 0.02, 0.08, max(0.05, min(1.0, opacity)))
    PAINTERS[name](cr, float(w), float(h))
