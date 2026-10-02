"""
bridgecad_draw.titleblocks — IRC / NHAI / MORTH title block generator.

A title block occupies the bottom-right corner of the sheet.
Standard dimensions (A1 landscape, 841 × 594 mm):
  - Sheet border:     inner margin 10 mm from edge
  - Title block:      180 mm wide × 55 mm tall, bottom-right
  - Revision table:   50 mm wide × full title-block height, left of title block

All coordinates are in mm (model space, 1 unit = 1 mm).
"""
from __future__ import annotations

from typing import Any

from .primitives import rectangle, text, line
from .layers import L


# ---------------------------------------------------------------------------
# Sheet size constants (mm)
# ---------------------------------------------------------------------------
_SHEET_SIZES: dict[str, tuple[float, float]] = {
    "A0": (1189.0, 841.0),
    "A1": (841.0,  594.0),
    "A2": (594.0,  420.0),
    "A3": (420.0,  297.0),
    "A4": (297.0,  210.0),
}

_MARGIN  = 10.0   # mm outer margin
_TB_H    = 55.0   # title block height mm
_TB_W    = 185.0  # title block width mm
_REV_W   = 45.0   # revision strip width mm


def draw_border(msp: Any, sheet_size: str = "A1") -> tuple[float, float]:
    """Draw outer and inner sheet borders.

    Returns
    -------
    (sheet_w, sheet_h) : tuple
        Full sheet dimensions in mm.
    """
    sw, sh = _SHEET_SIZES.get(sheet_size.upper(), _SHEET_SIZES["A1"])
    m = _MARGIN
    # Outer border
    rectangle(msp, 0, 0, sw, sh, layer="BORDER-OUTER")
    # Inner border (drawing area)
    rectangle(msp, m, m, sw - 2*m, sh - 2*m, layer="BORDER-INNER")
    return sw, sh


def draw_title_block(
    msp: Any,
    project_title: str = "",
    bridge_name: str = "",
    drawing_no: str = "GAD-001",
    drawing_title: str = "GENERAL ARRANGEMENT DRAWING",
    revision: str = "R0",
    date_str: str = "",
    designed_by: str = "",
    checked_by: str = "",
    approved_by: str = "",
    client: str = "",
    consultant: str = "",
    scale_str: str = "1:100",
    sheet_no: str = "1",
    total_sheets: str = "1",
    sheet_size: str = "A1",
) -> None:
    """Draw the IRC-standard title block in the bottom-right corner."""
    sw, sh = _SHEET_SIZES.get(sheet_size.upper(), _SHEET_SIZES["A1"])
    m = _MARGIN

    # Title block bounding box (bottom-right)
    tb_x0 = sw - m - _TB_W
    tb_y0 = m
    tb_x1 = sw - m
    tb_y1 = m + _TB_H

    # Outer box
    rectangle(msp, tb_x0, tb_y0, _TB_W, _TB_H,
              layer="TITLEBLK-BOX", lw=50)

    # ── Row layout (bottom to top) ─────────────────────────────────────────
    row_h = [10.0, 10.0, 10.0, 12.0, 13.0]  # 5 rows, total = 55 mm
    ys = [tb_y0]
    for rh in row_h:
        ys.append(ys[-1] + rh)

    def _cell(x0, y0, w, h, val, th=3.0, bold=False):
        rectangle(msp, x0, y0, w, h, layer="TITLEBLK-BOX", lw=25)
        if val:
            text(msp, str(val), x0 + 1.5, y0 + h/2 - th/2,
                 height=th, layer="TITLEBLK-TEXT")

    col_split = [0, 60, 90, 125, _TB_W]  # 4 columns

    # Row 0 (bottom) — sheet number / total
    r0y = ys[0]; r0h = row_h[0]
    _cell(tb_x0,              r0y, 60,  r0h, f"DRG: {drawing_no}",  th=2.8)
    _cell(tb_x0 + 60,         r0y, 30,  r0h, f"Rev: {revision}",    th=2.8)
    _cell(tb_x0 + 90,         r0y, 35,  r0h, f"Date: {date_str}",   th=2.8)
    _cell(tb_x0 + 125,        r0y, _TB_W-125, r0h,
          f"Sheet {sheet_no}/{total_sheets}", th=2.8)

    # Row 1 — design/check/approval
    r1y = ys[1]; r1h = row_h[1]
    _cell(tb_x0,              r1y, 60,  r1h, f"Designed: {designed_by}", th=2.5)
    _cell(tb_x0 + 60,         r1y, 60,  r1h, f"Checked: {checked_by}",   th=2.5)
    _cell(tb_x0 + 120,        r1y, _TB_W-120, r1h, f"Approved: {approved_by}", th=2.5)

    # Row 2 — scale / client
    r2y = ys[2]; r2h = row_h[2]
    _cell(tb_x0,              r2y, 50, r2h, f"Scale: {scale_str}", th=2.8)
    _cell(tb_x0 + 50,         r2y, _TB_W-50, r2h, f"Client: {client}", th=2.8)

    # Row 3 — consultant
    r3y = ys[3]; r3h = row_h[3]
    _cell(tb_x0,              r3y, _TB_W, r3h, f"Consultant: {consultant}", th=3.0)

    # Row 4 (top) — drawing title
    r4y = ys[4]; r4h = row_h[4]
    _cell(tb_x0,              r4y, _TB_W, r4h, f"{drawing_title}", th=3.5)

    # Project title above title block
    text(msp, project_title, tb_x0, tb_y1 + 2.0,
         height=3.5, layer="TITLEBLK-TEXT")
    text(msp, bridge_name, tb_x0, tb_y1 + 7.0,
         height=3.0, layer="TITLEBLK-TEXT")


def draw_revision_strip(
    msp: Any,
    revisions: list[tuple[str, str, str]] | None = None,
    sheet_size: str = "A1",
) -> None:
    """Draw the revision history strip to the left of the title block.

    *revisions* is a list of (rev_tag, date, description) tuples.
    """
    sw, sh = _SHEET_SIZES.get(sheet_size.upper(), _SHEET_SIZES["A1"])
    m = _MARGIN
    strip_x0 = sw - m - _TB_W - _REV_W
    strip_y0 = m
    strip_h  = _TB_H

    rectangle(msp, strip_x0, strip_y0, _REV_W, strip_h,
              layer="TITLEBLK-BOX", lw=25)

    # Header
    hh = 6.0
    rectangle(msp, strip_x0, strip_y0 + strip_h - hh,
              _REV_W, hh, layer="TITLEBLK-BOX", lw=25)
    text(msp, "REVISION HISTORY", strip_x0 + 1.5,
         strip_y0 + strip_h - hh + 1.5, height=2.5, layer="TITLEBLK-TEXT")

    row_h = 8.0
    y = strip_y0 + strip_h - hh - row_h
    for rev, dt, desc in (revisions or [])[:5]:
        rectangle(msp, strip_x0, y, _REV_W, row_h,
                  layer="TITLEBLK-BOX", lw=13)
        text(msp, f"{rev}  {dt}  {desc[:20]}", strip_x0 + 1.5, y + 2.0,
             height=2.2, layer="TITLEBLK-TEXT")
        y -= row_h


__all__ = ["draw_border", "draw_title_block", "draw_revision_strip",
           "_SHEET_SIZES"]
