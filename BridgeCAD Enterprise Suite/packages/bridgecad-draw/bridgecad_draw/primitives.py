"""
bridgecad_draw.primitives — High-level DXF drawing helpers built on ezdxf.

All helpers accept an ``msp`` (modelspace) object and return the entity or None.
Coordinates are in real-world metres unless noted (ezdxf draws in model units).

Design notes
------------
- Every helper is a standalone function; no class state.
- Layer names reference LAYER_REGISTRY keys defined in layers.py.
- All functions guard against invalid inputs and return None on failure.
- Scale-aware helpers accept ``scale`` (denominator, e.g. 100 for 1:100).
"""
from __future__ import annotations

import math
from typing import Any, Sequence


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Pt2 = tuple[float, float]
Pts = Sequence[Pt2]


# ---------------------------------------------------------------------------
# Low-level attribute builder
# ---------------------------------------------------------------------------

def _attribs(layer: str, color: int | None = None,
             linetype: str | None = None, lw: int | None = None) -> dict:
    d: dict[str, Any] = {"layer": layer}
    if color is not None:
        d["color"] = color
    if linetype is not None:
        d["linetype"] = linetype
    if lw is not None:
        d["lineweight"] = lw
    return d


# ---------------------------------------------------------------------------
# Basic geometry
# ---------------------------------------------------------------------------

def line(msp, p1: Pt2, p2: Pt2, layer: str = "STRUC-OUTLINE",
         color: int | None = None, lw: int | None = None) -> Any:
    """Draw a single line from *p1* to *p2*."""
    try:
        return msp.add_line(p1, p2, dxfattribs=_attribs(layer, color, lw=lw))
    except Exception:
        return None


def polyline(msp, points: Pts, layer: str = "STRUC-OUTLINE",
             close: bool = False, color: int | None = None,
             lw: int | None = None) -> Any:
    """Draw a lightweight polyline through *points*."""
    try:
        pts = [(float(x), float(y)) for x, y in points]
        if close and pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        return msp.add_lwpolyline(pts, dxfattribs=_attribs(layer, color, lw=lw))
    except Exception:
        return None


def rectangle(msp, x: float, y: float, w: float, h: float,
              layer: str = "STRUC-OUTLINE",
              color: int | None = None, lw: int | None = None) -> Any:
    """Draw a closed rectangle with bottom-left corner at (x, y)."""
    pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
    return polyline(msp, pts, layer=layer, color=color, lw=lw)


def circle(msp, cx: float, cy: float, r: float,
           layer: str = "STRUC-OUTLINE", color: int | None = None) -> Any:
    """Draw a circle centred at (cx, cy) with radius r."""
    try:
        return msp.add_circle((cx, cy), r, dxfattribs=_attribs(layer, color))
    except Exception:
        return None


def arc(msp, cx: float, cy: float, r: float,
        start_deg: float, end_deg: float,
        layer: str = "STRUC-OUTLINE", color: int | None = None) -> Any:
    """Draw an arc centred at (cx, cy)."""
    try:
        return msp.add_arc((cx, cy), r, start_deg, end_deg,
                           dxfattribs=_attribs(layer, color))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------

def text(msp, content: str, x: float, y: float, height: float = 0.5,
         layer: str = "TEXT-GENERAL", rotation: float = 0.0,
         color: int | None = None, halign: str = "LEFT") -> Any:
    """Add a simple text entity."""
    try:
        align_map = {"LEFT": 0, "CENTER": 4, "RIGHT": 2,
                     "MIDDLE": 5, "TOP_LEFT": 1}
        ha = align_map.get(halign.upper(), 0)
        attribs = _attribs(layer, color)
        attribs.update({"height": float(height)})
        if rotation:
            attribs["rotation"] = float(rotation)
        t = msp.add_text(str(content), dxfattribs=attribs)
        if ha:
            t.set_placement((x, y), align=ha)
        else:
            t.dxf.insert = (float(x), float(y))
        return t
    except Exception:
        return None


def mtext(msp, content: str, x: float, y: float, width: float,
          height: float = 0.5, layer: str = "TEXT-GENERAL",
          color: int | None = None) -> Any:
    """Add an MTEXT (multi-line text) entity."""
    try:
        attribs = _attribs(layer, color)
        attribs["char_height"] = float(height)
        attribs["width"] = float(width)
        attribs["insert"] = (float(x), float(y))
        return msp.add_mtext(str(content), dxfattribs=attribs)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Hatching
# ---------------------------------------------------------------------------

def hatch_rect(msp, x: float, y: float, w: float, h: float,
               pattern: str = "ANSI31", scale: float = 1.0,
               layer: str = "STRUC-HATCHING", color: int | None = None) -> Any:
    """Fill a rectangle with a hatch pattern (concrete = ANSI31, earth = ANSI37)."""
    try:
        hatch = msp.add_hatch(dxfattribs=_attribs(layer, color))
        hatch.set_pattern_fill(pattern, scale=scale)
        pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        hatch.paths.add_polyline_path(pts, is_closed=True)
        return hatch
    except Exception:
        return None


def hatch_poly(msp, points: Pts, pattern: str = "ANSI31",
               scale: float = 1.0, layer: str = "STRUC-HATCHING",
               color: int | None = None) -> Any:
    """Fill an arbitrary polygon with a hatch pattern."""
    try:
        hatch = msp.add_hatch(dxfattribs=_attribs(layer, color))
        hatch.set_pattern_fill(pattern, scale=scale)
        pts = [(float(x), float(y)) for x, y in points]
        hatch.paths.add_polyline_path(pts, is_closed=True)
        return hatch
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Dimension helpers
# ---------------------------------------------------------------------------

def dim_linear_h(msp, x1: float, y1: float, x2: float, y2: float,
                 dim_y: float, label: str | None = None,
                 layer: str = "DIM-LINEAR",
                 text_height: float = 0.35) -> Any:
    """Horizontal linear dimension between (x1,y1) and (x2,y2).

    *dim_y* is the y-position of the dimension line.
    """
    try:
        # Extension lines
        line(msp, (x1, y1), (x1, dim_y), layer=layer)
        line(msp, (x2, y2), (x2, dim_y), layer=layer)
        # Dimension line with arrowheads (simple tick)
        line(msp, (x1, dim_y), (x2, dim_y), layer=layer)
        # Arrowhead ticks
        tick = text_height * 0.8
        line(msp, (x1, dim_y - tick), (x1, dim_y + tick), layer=layer)
        line(msp, (x2, dim_y - tick), (x2, dim_y + tick), layer=layer)
        # Label
        display = label if label else f"{abs(x2 - x1):.3f}"
        cx = (x1 + x2) / 2
        text(msp, display, cx, dim_y + text_height * 0.3,
             height=text_height, layer="DIM-LINEAR", halign="CENTER")
    except Exception:
        return None


def dim_linear_v(msp, x1: float, y1: float, x2: float, y2: float,
                 dim_x: float, label: str | None = None,
                 layer: str = "DIM-LINEAR",
                 text_height: float = 0.35) -> Any:
    """Vertical linear dimension between (x1,y1) and (x2,y2).

    *dim_x* is the x-position of the dimension line.
    """
    try:
        line(msp, (x1, y1), (dim_x, y1), layer=layer)
        line(msp, (x2, y2), (dim_x, y2), layer=layer)
        line(msp, (dim_x, y1), (dim_x, y2), layer=layer)
        tick = text_height * 0.8
        line(msp, (dim_x - tick, y1), (dim_x + tick, y1), layer=layer)
        line(msp, (dim_x - tick, y2), (dim_x + tick, y2), layer=layer)
        display = label if label else f"{abs(y2 - y1):.3f}"
        cy = (y1 + y2) / 2
        text(msp, display, dim_x + text_height * 0.5, cy,
             height=text_height, layer="DIM-LINEAR", rotation=90)
    except Exception:
        return None


def level_tag(msp, x: float, y: float, rl: float,
              text_height: float = 0.35, layer: str = "DIM-LEVEL") -> None:
    """Draw a reduced-level (RL) tag: horizontal tick + RL value."""
    try:
        w = text_height * 3
        line(msp, (x - w, y), (x + w, y), layer=layer)
        line(msp, (x, y), (x, y - text_height * 0.5), layer=layer)
        label = f"RL {rl:.3f}"
        text(msp, label, x + w * 1.1, y, height=text_height,
             layer="TEXT-LEVEL")
    except Exception:
        pass


def chainage_tag(msp, x: float, y: float, ch_km: float,
                 text_height: float = 0.35, layer: str = "CIVIL-CHAINAGE") -> None:
    """Draw a chainage marker: vertical tick + CH label."""
    try:
        tick_h = text_height * 1.5
        line(msp, (x, y), (x, y - tick_h), layer=layer)
        label = f"CH {ch_km:.3f}"
        text(msp, label, x, y - tick_h - text_height * 0.3,
             height=text_height, layer="DIM-CHAINAGE", rotation=90)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Symbol helpers
# ---------------------------------------------------------------------------

def north_arrow(msp, cx: float, cy: float, size: float = 2.0,
                layer: str = "SYM-NORTHARROW") -> None:
    """Draw a simple north arrow centred at (cx, cy)."""
    try:
        tip   = (cx, cy + size)
        left  = (cx - size * 0.35, cy - size * 0.5)
        right = (cx + size * 0.35, cy - size * 0.5)
        base  = (cx, cy - size * 0.2)
        # Left half filled (dark)
        hatch_poly(msp, [tip, left, base], pattern="SOLID",
                   scale=1.0, layer=layer, color=7)
        # Outline
        polyline(msp, [tip, left, base, right, tip],
                 layer=layer, close=False)
        text(msp, "N", cx, cy + size + size * 0.3,
             height=size * 0.45, layer=layer, halign="CENTER")
    except Exception:
        pass


def section_mark(msp, x: float, y: float, label: str = "A",
                 size: float = 1.0, layer: str = "SYM-SECTIONMARK") -> None:
    """Draw a section-cut marker: circle + label."""
    try:
        circle(msp, x, y, size * 0.6, layer=layer, color=1)
        text(msp, label, x, y - size * 0.2,
             height=size * 0.6, layer=layer, halign="CENTER")
    except Exception:
        pass


def scale_bar(msp, x: float, y: float, scale_denom: int,
              segments: int = 5, seg_len_m: float = 5.0,
              layer: str = "SYM-SCALE", text_height: float = 0.35) -> None:
    """Draw a graphic scale bar."""
    try:
        total = segments * seg_len_m
        rectangle(msp, x, y, total, text_height * 0.8, layer=layer)
        # Alternating fill
        for i in range(segments):
            sx = x + i * seg_len_m
            if i % 2 == 0:
                hatch_rect(msp, sx, y, seg_len_m, text_height * 0.8,
                           pattern="SOLID", scale=1.0, layer=layer, color=7)
        # Labels
        for i in range(segments + 1):
            val = i * seg_len_m
            text(msp, f"{val:.0f}m", x + i * seg_len_m,
                 y - text_height * 1.2, height=text_height,
                 layer="TEXT-GENERAL", halign="CENTER")
        text(msp, f"1 : {scale_denom}", x + total / 2,
             y + text_height * 1.5, height=text_height,
             layer="TEXT-GENERAL", halign="CENTER")
    except Exception:
        pass


__all__ = [
    "line", "polyline", "rectangle", "circle", "arc",
    "text", "mtext",
    "hatch_rect", "hatch_poly",
    "dim_linear_h", "dim_linear_v", "level_tag", "chainage_tag",
    "north_arrow", "section_mark", "scale_bar",
]
