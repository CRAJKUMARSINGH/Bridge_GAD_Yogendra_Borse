"""
bridgecad_draw.sheet2_long_section — Bridge GAD Sheet 2: Longitudinal Section.

Draws:
  1. Ground profile polyline (green, from geometry module)
  2. HFL, LWL, Scour level horizontal datum lines
  3. Deck top and soffit lines
  4. Pier shafts (elevation)
  5. Abutment front faces
  6. Pile tips (vertical lines below pile cap)
  7. Level tags for HFL, LWL, Scour, Soffit, Top-of-deck, Pile tip
  8. Span labels and dimension strings
  9. Pier / abutment labels
 10. Section hatching (deck slab, piers, foundations)
 11. Chainage axis at bottom
 12. Title block + border (Sheet 2 of 7)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .dxf_engine import new_sheet, CoordMapper, save
from .primitives import (
    line, polyline, rectangle, circle, text, hatch_rect, hatch_poly,
    dim_linear_h, dim_linear_v, level_tag, chainage_tag,
    north_arrow, scale_bar,
)
from .titleblocks import draw_border, draw_title_block, draw_revision_strip


# ---------------------------------------------------------------------------
# Layout constants (A1 landscape, mm)
# ---------------------------------------------------------------------------
_SHEET_W = 841.0
_SHEET_H = 594.0
_MARGIN  = 10.0
_TB_H    = 65.0      # title block height at bottom
_LEVEL_AXIS_W = 30.0  # width of level axis on left
_CHAINAGE_H   = 20.0  # height of chainage axis at bottom of drawing


def generate(
    project: Any,
    output_path: str | Path,
    scale_denom: int = 100,
    v_exag: float = 2.0,
) -> Path:
    """Generate Sheet 2 (Longitudinal Section) as a DXF file.

    Parameters
    ----------
    project : BridgeProject
    output_path : str | Path
    scale_denom : int
        Horizontal scale denominator (e.g. 100 for 1:100).
    v_exag : float
        Vertical exaggeration multiplier (default 2.0 for readability).

    Returns
    -------
    Path
    """
    doc, msp = new_sheet("S2 Long Section")
    _draw_long_section(msp, project, scale_denom, v_exag)
    return save(doc, output_path)


def _draw_long_section(msp: Any, project: Any,
                       scale_denom: int = 100,
                       v_exag: float = 2.0) -> None:
    from bridgecad_core.geometry import compute_long_section_geometry

    gi  = project.geometry_input
    sub = project.substructure
    ss  = project.superstructure
    fd  = project.foundation_details
    pm  = project.project_master
    hd  = project.hydraulic_data

    # ── Geometry ──────────────────────────────────────────────────────────
    ls = compute_long_section_geometry(project)

    total_len   = float(gi.total_length_m)
    span_lens   = [float(s) for s in gi.span_lengths_m]

    hfl_rl      = ls.hfl_rl
    lwl_rl      = ls.lwl_rl
    scour_rl    = ls.scour_level_rl
    soffit_rl   = ls.soffit_rl
    top_rl      = ls.top_of_deck_rl
    pile_tip_rl = ls.pile_tip_rl

    datum_rl = min(pile_tip_rl, scour_rl) - 2.0  # baseline datum
    rl_range = max(top_rl + 2.0, hfl_rl + 3.0) - datum_rl

    # ── Drawing area ───────────────────────────────────────────────────────
    draw_x0 = _MARGIN + _LEVEL_AXIS_W + 5.0
    draw_y0 = _MARGIN + _TB_H + _CHAINAGE_H + 10.0
    draw_w  = _SHEET_W - draw_x0 - _MARGIN - 10.0
    draw_h  = _SHEET_H - draw_y0 - _MARGIN - 20.0

    # Scale factors (mm per metre)
    sc_h = draw_w / max(total_len, 0.1)           # horizontal
    sc_v = draw_h / max(rl_range, 0.1) / v_exag   # vertical (exaggerated)

    cm = CoordMapper(
        datum_rl  = datum_rl,
        origin_ch = 0.0,
        h_scale   = sc_h / 1000.0,  # CoordMapper expects h_scale in m→unit
        v_scale   = sc_v / 1000.0 * v_exag,
        x_offset  = draw_x0,
        y_offset  = draw_y0,
    )

    def hx(ch):  return draw_x0 + ch * sc_h
    def vy(rl):  return draw_y0 + (rl - datum_rl) * sc_v * v_exag

    # ── Border & title block ───────────────────────────────────────────────
    draw_border(msp, "A1")
    draw_title_block(
        msp,
        project_title = getattr(pm, "project_title", "") or "",
        bridge_name   = getattr(pm, "bridge_name", "") or "",
        drawing_no    = getattr(pm, "drawing_no",  "GAD-002") or "GAD-002",
        drawing_title = "GENERAL ARRANGEMENT — LONGITUDINAL SECTION",
        revision      = getattr(getattr(pm, "revision", None), "name", "R0") or "R0",
        date_str      = str(getattr(pm, "date_issued", "") or ""),
        designed_by   = getattr(pm, "designed_by",  "") or "",
        checked_by    = getattr(pm, "checked_by",   "") or "",
        approved_by   = getattr(pm, "approved_by",  "") or "",
        client        = getattr(getattr(pm, "client",     None), "name", "") or "",
        consultant    = getattr(getattr(pm, "consultant", None), "name", "") or "",
        scale_str     = f"1:{scale_denom} H  1:{int(scale_denom/v_exag)} V",
        sheet_no      = "2",
        total_sheets  = "7",
    )

    th = max(2.5, sc_h * 0.4)   # adaptive text height mm

    # ── Datum / chainage axis ─────────────────────────────────────────────
    line(msp, (draw_x0, draw_y0), (hx(total_len), draw_y0),
         layer="CIVIL-CHAINAGE")
    # Chainage markers every span
    cumul = 0.0
    for slen in span_lens:
        chainage_tag(msp, hx(cumul),
                     draw_y0 - 2.0,
                     (float(gi.chainage_start_km or 0)*1000 + cumul) / 1000.0,
                     text_height=th * 0.8)
        cumul += slen
    chainage_tag(msp, hx(total_len),
                 draw_y0 - 2.0,
                 (float(gi.chainage_start_km or 0)*1000 + total_len) / 1000.0,
                 text_height=th * 0.8)

    # ── Level axis (left side) ─────────────────────────────────────────────
    line(msp, (draw_x0, draw_y0), (draw_x0, vy(top_rl + 2.0)),
         layer="DIM-LEVEL")

    # ── Ground profile ────────────────────────────────────────────────────
    gnd_pts = [(hx(ch), vy(rl)) for ch, rl in ls.ground_profile_pts]
    if len(gnd_pts) >= 2:
        polyline(msp, gnd_pts, layer="CIVIL-GROUND", color=3)
        text(msp, "EXISTING GROUND LEVEL", gnd_pts[-1][0] + sc_h*0.5,
             gnd_pts[-1][1], height=th*0.85, layer="CIVIL-GROUND", color=3)

    # ── HFL line ──────────────────────────────────────────────────────────
    hfl_y_mm = vy(hfl_rl)
    line(msp, (draw_x0, hfl_y_mm), (hx(total_len), hfl_y_mm),
         layer="CIVIL-HFL", color=5)
    level_tag(msp, draw_x0 - 2.0, hfl_y_mm, hfl_rl, text_height=th*0.85,
              layer="CIVIL-HFL")
    text(msp, "HFL", hx(total_len) + sc_h*0.3, hfl_y_mm,
         height=th*0.85, layer="CIVIL-HFL", color=5)

    # ── LWL line ──────────────────────────────────────────────────────────
    lwl_y_mm = vy(lwl_rl)
    line(msp, (draw_x0, lwl_y_mm), (hx(total_len), lwl_y_mm),
         layer="CIVIL-LWL", color=4)
    level_tag(msp, draw_x0 - 2.0, lwl_y_mm, lwl_rl, text_height=th*0.85,
              layer="CIVIL-LWL")
    text(msp, "LWL", hx(total_len) + sc_h*0.3, lwl_y_mm,
         height=th*0.85, layer="CIVIL-LWL", color=4)

    # ── Scour level ───────────────────────────────────────────────────────
    scour_y_mm = vy(scour_rl)
    line(msp, (draw_x0, scour_y_mm), (hx(total_len), scour_y_mm),
         layer="CIVIL-SCOUR", color=1)
    level_tag(msp, draw_x0 - 2.0, scour_y_mm, scour_rl,
              text_height=th*0.85, layer="CIVIL-SCOUR")
    text(msp, "DESIGN SCOUR LEVEL", hx(total_len) + sc_h*0.3, scour_y_mm,
         height=th*0.85, layer="CIVIL-SCOUR", color=1)

    # ── Deck profile ──────────────────────────────────────────────────────
    sof_y_mm = vy(soffit_rl)
    top_y_mm = vy(top_rl)

    # Top of deck line
    line(msp, (hx(0), top_y_mm), (hx(total_len), top_y_mm),
         layer="SUPER-DECK")
    # Soffit line
    line(msp, (hx(0), sof_y_mm), (hx(total_len), sof_y_mm),
         layer="SUPER-DECK")
    # Deck slab hatch
    hatch_rect(msp, hx(0), sof_y_mm,
               total_len * sc_h, top_y_mm - sof_y_mm,
               pattern="ANSI31", scale=sc_h * 0.04,
               layer="STRUC-HATCHING", color=8)

    level_tag(msp, draw_x0 - 2.0, sof_y_mm, soffit_rl,
              text_height=th*0.85)
    level_tag(msp, draw_x0 - 2.0, top_y_mm, top_rl,
              text_height=th*0.85)

    # ── Pier shafts ───────────────────────────────────────────────────────
    pier_w_mm  = float(sub.pier_shaft_width_m  or 1.5) * sc_h
    pier_cap_h = float(sub.pier_cap_depth_m    or 0.8) * sc_v * v_exag
    pier_ped_h = float(sub.pier_pedestal_height_m or 0.2) * sc_v * v_exag
    pile_cap_h = float(fd.pile_cap_thickness_mm or 1500) / 1000.0 * sc_v * v_exag

    cumul = 0.0
    for i, slen in enumerate(span_lens[:-1]):
        cumul += slen
        px = hx(cumul) - pier_w_mm / 2.0
        py_top = sof_y_mm - pier_ped_h - pier_cap_h  # below soffit
        py_bot = vy(hfl_rl - float(sub.pier_height_typical_m or 8.0))

        # Pier shaft
        rectangle(msp, px, py_bot, pier_w_mm, py_top - py_bot,
                  layer="SUB-PIER", lw=40)
        hatch_rect(msp, px, py_bot, pier_w_mm, py_top - py_bot,
                   pattern="ANSI31", scale=sc_h * 0.04,
                   layer="STRUC-HATCHING", color=8)

        # Pier cap
        cap_w = float(sub.pier_cap_width_m or 2.0) * sc_h
        rectangle(msp, hx(cumul) - cap_w/2, py_top,
                  cap_w, pier_cap_h,
                  layer="SUB-PIER", lw=40)
        hatch_rect(msp, hx(cumul) - cap_w/2, py_top,
                   cap_w, pier_cap_h,
                   pattern="ANSI31", scale=sc_h * 0.04,
                   layer="STRUC-HATCHING")

        text(msp, f"P{i+1}", hx(cumul) - pier_w_mm * 0.5,
             py_bot - th * 2, height=th, layer="TEXT-GENERAL")

        # Span label at mid-span
        mid_x = hx(cumul - slen / 2.0)
        text(msp, f"{slen:.1f} m", mid_x, sof_y_mm + (top_y_mm - sof_y_mm)/2,
             height=th * 1.1, layer="TEXT-GENERAL", halign="CENTER")

    # Last span label
    mid_x = hx(total_len - span_lens[-1] / 2.0)
    text(msp, f"{span_lens[-1]:.1f} m", mid_x,
         sof_y_mm + (top_y_mm - sof_y_mm)/2,
         height=th * 1.1, layer="TEXT-GENERAL", halign="CENTER")

    # ── Abutments ─────────────────────────────────────────────────────────
    abt_w_mm  = float(sub.abutment_width_m or 1.2) * sc_h
    abt_h_mm  = float(sub.abutment_height_m or 3.2) * sc_v * v_exag
    for ch, label in [(0.0, "A1"), (total_len, "A2")]:
        if ch == 0.0:
            ax = hx(ch) - abt_w_mm
        else:
            ax = hx(ch)
        ay = sof_y_mm - abt_h_mm
        rectangle(msp, ax, ay, abt_w_mm, abt_h_mm,
                  layer="SUB-ABUT", lw=40)
        hatch_rect(msp, ax, ay, abt_w_mm, abt_h_mm,
                   pattern="ANSI31", scale=sc_h * 0.04,
                   layer="STRUC-HATCHING")
        text(msp, label, ax - th*2 if ch == 0 else ax + abt_w_mm + th*0.5,
             sof_y_mm - abt_h_mm/2, height=th, layer="TEXT-GENERAL")

    # ── Piles / foundations ───────────────────────────────────────────────
    pile_dia_mm = float(fd.pile_diameter_mm or 1200) / 1000.0 * sc_h
    pile_tip_y  = vy(pile_tip_rl)
    pile_cut_y  = vy(float(fd.pile_cutoff_level_m or scour_rl) - 1.0)

    piles_per_pier = int(fd.piles_per_pier or 4)
    cols = max(1, round(piles_per_pier ** 0.5))

    # Show pile group elevation under each support
    for ch, is_abut in (
        [(0.0, True), (total_len, True)]
        + [(sum(span_lens[:i+1]), False) for i in range(len(span_lens)-1)]
    ):
        group_w = (cols - 1) * float(fd.pile_spacing_m or 2.4) * sc_h
        for c in range(cols):
            offset = (c - (cols - 1) / 2.0) * float(fd.pile_spacing_m or 2.4) * sc_h
            px = hx(ch) + offset - pile_dia_mm / 2.0
            line(msp, (hx(ch) + offset, pile_cut_y),
                      (hx(ch) + offset, pile_tip_y),
                 layer="FOUND-PILE", lw=35)
            circle(msp, hx(ch) + offset, pile_cut_y,
                   pile_dia_mm / 2.0, layer="FOUND-PILE")

    level_tag(msp, draw_x0 - 2.0, pile_tip_y, pile_tip_rl,
              text_height=th * 0.85)
    text(msp, "PILE TIP LEVEL", hx(total_len) + sc_h * 0.3, pile_tip_y,
         height=th * 0.85, layer="TEXT-GENERAL")

    # ── Freeboard annotation ──────────────────────────────────────────────
    fb_mid_x = hx(total_len * 0.7)
    dim_linear_v(msp, fb_mid_x, hfl_y_mm, fb_mid_x, sof_y_mm,
                 dim_x=fb_mid_x + sc_h * 2.0,
                 label=f"FB={ls.freeboard_m:.3f}m",
                 text_height=th * 0.9)

    # ── View label ────────────────────────────────────────────────────────
    text(msp, "LONGITUDINAL SECTION",
         draw_x0 + draw_w / 2, vy(top_rl) + sc_v * v_exag * 2.5,
         height=th * 1.5, layer="TEXT-HEADER", halign="CENTER")
    text(msp,
         f"H Scale 1:{scale_denom}   V Scale 1:{int(scale_denom/v_exag)} (V.E.={v_exag}×)",
         draw_x0 + draw_w / 2, vy(top_rl) + sc_v * v_exag * 1.0,
         height=th * 0.9, layer="TEXT-SPEC", halign="CENTER")


__all__ = ["generate"]
