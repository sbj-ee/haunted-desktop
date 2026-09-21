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
    """Bright amber radial glow with a hot core — not neon, not cartoon."""
    # Outer haze
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, max(rx, ry) * 2.2)
    g.add_color_stop_rgba(0.0, 0.95, 0.78, 0.38, peak * 0.75)
    g.add_color_stop_rgba(0.35, 0.85, 0.62, 0.25, peak * 0.42)
    g.add_color_stop_rgba(1.0, 0.2, 0.18, 0.12, 0.0)
    cr.set_source(g)
    _ellipse(cr, cx, cy, rx * 2.0, ry * 2.0)
    cr.fill()
    # Bright core
    g2 = cairo.RadialGradient(cx, cy, 0, cx, cy, max(rx, ry))
    g2.add_color_stop_rgba(0.0, 1.0, 0.95, 0.72, peak)
    g2.add_color_stop_rgba(0.55, 0.98, 0.75, 0.35, peak * 0.7)
    g2.add_color_stop_rgba(1.0, 0.3, 0.25, 0.15, 0.0)
    cr.set_source(g2)
    _ellipse(cr, cx, cy, rx, ry)
    cr.fill()


def _demon_eye(
    cr: cairo.Context, cx: float, cy: float, ew: float, eh: float, tilt: float, peak: float
) -> None:
    """Slanted almond eye: red haze, molten orange core, black vertical slit pupil."""
    cr.save()
    cr.translate(cx, cy)
    cr.rotate(tilt)
    # Red haze around the eye
    haze_r = min(ew * 0.85, eh * 2.4)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, haze_r)
    g.add_color_stop_rgba(0.0, 1.0, 0.15, 0.03, peak * 0.55)
    g.add_color_stop_rgba(0.5, 0.75, 0.05, 0.02, peak * 0.22)
    g.add_color_stop_rgba(1.0, 0.4, 0.0, 0.0, 0.0)
    cr.set_source(g)
    cr.arc(0, 0, haze_r, 0, 2 * math.pi)
    cr.fill()
    # Almond: flat, heavy upper lid; fuller lower curve
    hw = ew / 2
    cr.move_to(-hw, 0)
    cr.curve_to(-hw * 0.35, -eh * 0.55, hw * 0.4, -eh * 0.6, hw, 0)
    cr.curve_to(hw * 0.45, eh * 0.85, -hw * 0.4, eh * 0.9, -hw, 0)
    cr.close_path()
    g2 = cairo.RadialGradient(0, 0, 0, 0, 0, hw)
    g2.add_color_stop_rgba(0.0, 1.0, 0.88, 0.25, peak)
    g2.add_color_stop_rgba(0.45, 1.0, 0.42, 0.06, peak)
    g2.add_color_stop_rgba(0.85, 0.85, 0.08, 0.02, peak)
    g2.add_color_stop_rgba(1.0, 0.45, 0.0, 0.0, peak * 0.9)
    cr.set_source(g2)
    cr.fill_preserve()
    # Vertical slit pupil, clipped to the eye
    cr.save()
    cr.clip()
    cr.save()
    cr.scale(ew * 0.045, eh * 0.8)
    cr.arc(0, 0.08, 1, 0, 2 * math.pi)
    cr.restore()
    cr.set_source_rgba(0.02, 0.0, 0.0, min(1.0, peak * 1.1))
    cr.fill()
    cr.restore()
    cr.restore()


def paint_eyes(cr: cairo.Context, w: float, h: float, opacity: float = 0.22) -> None:
    """Pair of glowing demon eyes: angry slant, molten glow, slit pupils."""
    cr.save()
    peak = max(0.30, min(1.0, opacity * 1.3))
    cy = h * 0.5
    ew = w * random.uniform(0.28, 0.32)
    eh = ew * 0.5
    spacing = w * random.uniform(0.21, 0.25)
    tilt = random.uniform(0.28, 0.42)  # inner corners lower = angry
    _demon_eye(cr, w * 0.5 - spacing, cy, ew, eh, tilt, peak)
    _demon_eye(cr, w * 0.5 + spacing, cy, ew, eh, -tilt, peak)
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


def _hole(cr: cairo.Context, cx: float, cy: float, rx: float, ry: float, tilt: float = 0.0) -> None:
    """Add an (optionally tilted) ellipse sub-path; cut out under EVEN_ODD fill."""
    cr.save()
    cr.translate(cx, cy)
    cr.rotate(tilt)
    cr.scale(max(rx, 0.01), max(ry, 0.01))
    cr.new_sub_path()
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.restore()


def _mask_outline(cr: cairo.Context, w: float, h: float) -> None:
    """Hooded head tapering to a long, pointed chin (path only)."""
    cx = w * 0.5
    cr.move_to(cx, h * 0.01)
    cr.curve_to(cx + w * 0.42, h * 0.01, cx + w * 0.46, h * 0.30, cx + w * 0.34, h * 0.58)
    cr.curve_to(cx + w * 0.26, h * 0.80, cx + w * 0.12, h * 0.96, cx, h * 0.99)
    cr.curve_to(cx - w * 0.12, h * 0.96, cx - w * 0.26, h * 0.80, cx - w * 0.34, h * 0.58)
    cr.curve_to(cx - w * 0.46, h * 0.30, cx - w * 0.42, h * 0.01, cx, h * 0.01)
    cr.close_path()


def _mask_holes(cr: cairo.Context, w: float, h: float) -> None:
    cx = w * 0.5
    # Eyes: drooping teardrops, outer corners sagging down
    _hole(cr, cx - w * 0.17, h * 0.34, w * 0.075, h * 0.085, tilt=0.35)
    _hole(cr, cx + w * 0.17, h * 0.34, w * 0.075, h * 0.085, tilt=-0.35)
    # Mouth: long open oval, the mask's scream
    _hole(cr, cx, h * 0.70, w * 0.115, h * 0.155)


def paint_shadow(cr: cairo.Context, w: float, h: float, opacity: float = 0.75) -> None:
    """Life-size Scream mask: pale bone-white face, black eyes and mouth, soft glow."""
    a = max(0.05, min(1.0, opacity * 1.25))
    cx, cy = w * 0.5, h * 0.5
    cr.save()
    # Soft cool halo so it reads against dark and busy backgrounds
    g = cairo.RadialGradient(cx, cy, min(w, h) * 0.2, cx, cy, h * 0.62)
    g.add_color_stop_rgba(0.0, 0.85, 0.88, 0.95, a * 0.28)
    g.add_color_stop_rgba(1.0, 0.85, 0.88, 0.95, 0.0)
    cr.set_source(g)
    cr.paint()
    # Face
    _mask_outline(cr, w, h)
    face = cairo.LinearGradient(0, 0, 0, h)
    face.add_color_stop_rgba(0.0, 0.93, 0.93, 0.90, a)
    face.add_color_stop_rgba(1.0, 0.80, 0.80, 0.78, a)
    cr.set_source(face)
    cr.fill_preserve()
    cr.set_source_rgba(0.05, 0.05, 0.07, a)  # thin dark edge
    cr.set_line_width(max(2.0, w * 0.012))
    cr.stroke()
    # Black eyes and mouth
    _mask_holes(cr, w, h)
    cr.set_source_rgba(0.02, 0.02, 0.03, min(1.0, a + 0.1))
    cr.fill()
    cr.restore()


def _alien_head(cr: cairo.Context, w: float, h: float) -> None:
    """Head + neck outline path: elongated dome, tapering jaw, small chin."""
    cx = w * 0.5
    cr.move_to(cx, h * 0.02)
    cr.curve_to(cx + w * 0.54, h * 0.02, cx + w * 0.46, h * 0.38, cx + w * 0.30, h * 0.60)
    cr.curve_to(cx + w * 0.22, h * 0.72, cx + w * 0.12, h * 0.80, cx + w * 0.075, h * 0.86)
    cr.curve_to(cx + w * 0.07, h * 0.92, cx + w * 0.08, h * 0.96, cx + w * 0.085, h)
    cr.line_to(cx - w * 0.085, h)
    cr.curve_to(cx - w * 0.08, h * 0.96, cx - w * 0.07, h * 0.92, cx - w * 0.075, h * 0.86)
    cr.curve_to(cx - w * 0.12, h * 0.80, cx - w * 0.22, h * 0.72, cx - w * 0.30, h * 0.60)
    cr.curve_to(cx - w * 0.46, h * 0.38, cx - w * 0.54, h * 0.02, cx, h * 0.02)
    cr.close_path()


def _alien_eye_path(cr: cairo.Context, w: float, h: float) -> None:
    cr.move_to(-w * 0.19, 0)
    cr.curve_to(-w * 0.09, -h * 0.115, w * 0.11, -h * 0.10, w * 0.21, -h * 0.005)
    cr.curve_to(w * 0.10, h * 0.105, -w * 0.09, h * 0.135, -w * 0.19, 0)
    cr.close_path()


def paint_alien(cr: cairo.Context, w: float, h: float, opacity: float = 0.75) -> None:
    """Gray alien head, lit and shaded: mottled skin, deep glossy eyes, no outline."""
    a = max(0.05, min(1.0, opacity * 1.25))
    cx = w * 0.5
    rng = random.Random()
    cr.save()
    # Very faint cold glow behind the head
    g = cairo.RadialGradient(cx, h * 0.4, w * 0.2, cx, h * 0.4, h * 0.66)
    g.add_color_stop_rgba(0.0, 0.5, 0.85, 0.7, a * 0.16)
    g.add_color_stop_rgba(1.0, 0.5, 0.85, 0.7, 0.0)
    cr.set_source(g)
    cr.paint()

    # --- Skin, clipped to the head ---
    cr.save()
    _alien_head(cr, w, h)
    cr.clip_preserve()
    base = cairo.LinearGradient(0, 0, 0, h)
    base.add_color_stop_rgba(0.0, 0.62, 0.65, 0.60, a)
    base.add_color_stop_rgba(0.6, 0.52, 0.56, 0.52, a)
    base.add_color_stop_rgba(1.0, 0.38, 0.42, 0.39, a)
    cr.set_source(base)
    cr.fill()
    # Mottled, slightly waxy skin
    for _ in range(420):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(0.004, 0.014) * w
        if rng.random() < 0.55:
            cr.set_source_rgba(0.22, 0.27, 0.24, rng.uniform(0.03, 0.07) * a)
        else:
            cr.set_source_rgba(0.85, 0.9, 0.85, rng.uniform(0.03, 0.06) * a)
        cr.arc(x, y, r, 0, 2 * math.pi)
        cr.fill()
    # Key light from the upper left, falling to dark edges (gives volume)
    lit = cairo.RadialGradient(cx - w * 0.12, h * 0.26, h * 0.03, cx, h * 0.42, h * 0.62)
    lit.add_color_stop_rgba(0.0, 0.92, 0.97, 0.93, 0.26 * a)
    lit.add_color_stop_rgba(0.5, 0.0, 0.0, 0.0, 0.0)
    lit.add_color_stop_rgba(1.0, 0.0, 0.03, 0.02, 0.62 * a)
    cr.set_source(lit)
    cr.paint()
    # Neck falls into shadow
    neck = cairo.LinearGradient(0, h * 0.72, 0, h)
    neck.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, 0.0)
    neck.add_color_stop_rgba(1.0, 0.0, 0.02, 0.01, 0.6 * a)
    cr.set_source(neck)
    cr.paint()
    cr.restore()

    # --- Eyes: socket shadow, deep glossy black, soft reflections ---
    for sign in (-1, 1):
        cr.save()
        cr.translate(cx + sign * w * 0.20, h * 0.44)
        cr.rotate(-sign * 0.42)
        sock = cairo.RadialGradient(0, 0, w * 0.12, 0, 0, w * 0.34)
        sock.add_color_stop_rgba(0.0, 0.0, 0.02, 0.01, 0.5 * a)
        sock.add_color_stop_rgba(1.0, 0.0, 0.02, 0.01, 0.0)
        cr.set_source(sock)
        cr.arc(0, 0, w * 0.34, 0, 2 * math.pi)
        cr.fill()
        _alien_eye_path(cr, w, h)
        cr.save()
        cr.clip()
        eye = cairo.RadialGradient(-w * 0.05, -h * 0.03, w * 0.01, 0, 0, w * 0.22)
        eye.add_color_stop_rgba(0.0, 0.10, 0.14, 0.15, min(1.0, a + 0.1))
        eye.add_color_stop_rgba(0.55, 0.01, 0.02, 0.02, min(1.0, a + 0.1))
        eye.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, min(1.0, a + 0.1))
        cr.set_source(eye)
        cr.paint()
        # Broad soft window reflection
        refl = cairo.RadialGradient(-w * 0.07, -h * 0.045, 0, -w * 0.07, -h * 0.045, w * 0.09)
        refl.add_color_stop_rgba(0.0, 0.85, 0.95, 1.0, 0.30 * a)
        refl.add_color_stop_rgba(1.0, 0.85, 0.95, 1.0, 0.0)
        cr.set_source(refl)
        cr.paint()
        # Tiny hard specular
        cr.set_source_rgba(0.95, 1.0, 1.0, 0.7 * a)
        cr.arc(-w * 0.075, -h * 0.05, max(1.5, w * 0.008), 0, 2 * math.pi)
        cr.fill()
        cr.restore()
        cr.restore()

    # --- Nostril slits and a thin, nearly flat mouth ---
    cr.set_source_rgba(0.04, 0.07, 0.06, 0.75 * a)
    for sign in (-1, 1):
        cr.save()
        cr.translate(cx + sign * w * 0.016, h * 0.635)
        cr.rotate(sign * 0.4)
        cr.scale(max(1.0, w * 0.004), max(2.0, w * 0.009))
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
        cr.fill()
    cr.set_source_rgba(0.04, 0.07, 0.06, 0.7 * a)
    cr.set_line_width(max(1.2, w * 0.006))
    cr.move_to(cx - w * 0.05, h * 0.725)
    cr.curve_to(cx - w * 0.02, h * 0.728, cx + w * 0.02, h * 0.728, cx + w * 0.05, h * 0.724)
    cr.stroke()
    cr.restore()


PAINTERS: dict[str, Painter] = {
    "ghost": paint_ghost,
    "bat": paint_bat,
    "cat": paint_cat,
    "spider": paint_spider,
    "shadow": paint_shadow,
    # eyes drawn via draw_creature (needs opacity for glow peak)
}

CREATURE_NAMES = ["ghost", "bat", "cat", "spider", "shadow", "eyes", "pair", "alien"]


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
        "pair": 2.0,  # mask head + demon eyes together
        "alien": 1.5,
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
    if name == "shadow":
        paint_shadow(cr, float(w), float(h), opacity)
        return
    if name == "alien":
        paint_alien(cr, float(w), float(h), opacity)
        return
    _soft_fill(cr, opacity)
    painter = PAINTERS.get(name, paint_shadow)
    painter(cr, float(w), float(h))

