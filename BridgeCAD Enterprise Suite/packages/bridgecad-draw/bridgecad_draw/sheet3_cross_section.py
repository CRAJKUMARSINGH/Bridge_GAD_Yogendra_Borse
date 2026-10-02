"""
bridgecad_draw.sheet3_cross_section — Sheet 3: Typical Mid-Span Cross Section.

Draws:
  1. Deck slab (full width, hatched)
  2. Wearing coat layer
  3. Girders (I-shaped or T-beam per type)
  4. Kerbs / crash barriers / parapets
  5. Footpaths
  6. Camber parabola reference line (dashed)
  7. Width dimension strings (carriageway, footpath, overall)
  8. Depth dimension strings (slab, WC, girder)
  9. Level tags (top of deck, soffit, road level)
 10. Section label, scale bar, title block
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

from .dxf_engine import new_sheet, save
from .primitives import (
    line, polyline, rectangle, circle, text, hatch_rect, hatch_poly,
    dim_linear_h, dim_linear_v, level_tag, scale_bar,
)
from .titleblocks import draw_border, draw_title_block


def generate(project: Any, output_path: str | Path,
             scale_denom: int = 50) -> Path:
    """Generate Sheet 3 — Typical Mid-Span Cross Section."""
    doc, msp = new_sheet("S3 Cross Section")
    _draw(msp, project, scale_denom)
    return save(doc, output_path)


def _draw(msp: Any, project: Any, scale_denom: int = 50) -> None:
    from bridgecad_core.geometry import compute_cross_section_geometry

    gi  = project.geometry_input
    ss  = project.superstructure
    pm  = project.project_master
    hd  = project.hydraulic_data

    cs  = compute_cross_section_geometry(project)

    # ── Layout ────────────────────────────────────────────────────────────
    draw_border(msp, "A1")
    draw_title_block(
        msp,
        project_title = getattr(pm, "project_title", "") or "",
        bridge_name   = getattr(pm, "bridge_name",   "") or "",
        drawing_no    = getattr(pm, "drawing_no",  "GAD-003") or "GAD-003",
        drawing_title = "TYPICAL MID-SPAN CROSS SECTION",
        revision      = getattr(getattr(pm, "revision", None), "name", "R0") or "R0",
        sheet_no="3", total_sheets="7",
    )

    # ── Scale ─────────────────────────────────────────────────────────────
    ow_m    = float(cs.overall_width_m)
    # Fit overall width into 700 mm drawing width
    sc      = min(700.0 / max(ow_m, 0.1), 30.0)   # mm per metre, max 30
    cx      = 420.0                                 # centre X of sheet (mm)
    base_y  = 180.0                                 # Y of road surface at CL

    def hx(off_m):  return cx + off_m * sc
    def vy(rl_m):   return base_y + rl_m * sc

    deck_t_mm  = float(ss.deck_thickness_mm    or 230) / 1000.0
    wc_t_mm    = float(ss.wearing_coat_thickness_mm or 65) / 1000.0
    girder_d   = float(ss.girder_depth_mm      or 1200) / 1000.0
    g_spacing  = float(ss.girder_spacing_m     or 2.5)
    n_girders  = int(ss.girders_per_deck_count or 4)
    cw         = float(gi.carriageway_width_m  or 7.5)
    half_ow    = ow_m / 2.0
    half_cw    = cw   / 2.0
    fp_l       = float(gi.footpath_left_m      or 0.0)
    fp_r       = float(gi.footpath_right_m     or 0.0)
    kerb_l     = float(gi.kerb_width_left_m    or 0.25)
    kerb_r     = float(gi.kerb_width_right_m   or 0.25)
    camber_mm  = float(gi.camber_mm            or 0)

    th = max(2.5, sc * 0.3)

    # ── Wearing coat (top layer) ──────────────────────────────────────────
    wc_y = base_y
    wc_h = wc_t_mm * sc
    rectangle(msp, hx(-half_ow), wc_y - wc_h, ow_m * sc, wc_h,
              layer="SUPER-WEARING")
    hatch_rect(msp, hx(-half_ow), wc_y - wc_h, ow_m * sc, wc_h,
               pattern="AR-SAND", scale=sc * 0.003, layer="STRUC-HATCHING", color=8)

    # ── Deck slab ─────────────────────────────────────────────────────────
    slab_y = wc_y - wc_h
    slab_h = deck_t_mm * sc
    rectangle(msp, hx(-half_ow), slab_y - slab_h, ow_m * sc, slab_h,
              layer="SUPER-DECK", lw=50)
    hatch_rect(msp, hx(-half_ow), slab_y - slab_h, ow_m * sc, slab_h,
               pattern="ANSI31", scale=sc * 0.02, layer="STRUC-HATCHING", color=8)

    soffit_y = slab_y - slab_h

    # ── Girders ───────────────────────────────────────────────────────────
    gw_top   = g_spacing * 0.5 * sc   # half top flange width (mm)
    gw_web   = 0.15 * sc              # half web width (mm)
    gw_bot   = g_spacing * 0.4 * sc   # half bottom flange width (mm)
    g_flange = girder_d * 0.12 * sc   # flange thickness
    g_depth  = girder_d * sc

    g_starts = [
        (i - (n_girders - 1) / 2.0) * g_spacing
        for i in range(n_girders)
    ]
    for g_cl in g_starts:
        gx = hx(g_cl)
        gy = soffit_y
        # I/T cross-section outline
        pts = [
            (gx - gw_top, gy),
            (gx - gw_web, gy - g_depth + g_flange),
            (gx - gw_bot, gy - g_depth),
            (gx + gw_bot, gy - g_depth),
            (gx + gw_web, gy - g_depth + g_flange),
            (gx + gw_top, gy),
        ]
        polyline(msp, pts, layer="SUPER-GIRDER", close=True, lw=40)
        hatch_poly(msp, pts, pattern="ANSI31", scale=sc * 0.015,
                   layer="STRUC-HATCHING", color=8)

    girder_bot_y = soffit_y - g_depth

    # ── Kerbs ─────────────────────────────────────────────────────────────
    kerb_h = 0.22 * sc   # 220 mm standard kerb height
    for side, sign in [("L", -1), ("R", +1)]:
        kw = (kerb_l if side == "L" else kerb_r) * sc
        kx = hx(sign * half_cw) + (0 if sign == 1 else -kw)
        rectangle(msp, kx, wc_y - kerb_h, kw, kerb_h,
                  layer="SUPER-KERB", lw=30)

    # ── Parapets ──────────────────────────────────────────────────────────
    par_h = float(ss.parapet_height_mm or 1000) / 1000.0 * sc
    par_w = 0.25 * sc
    for sign in [-1, +1]:
        px = hx(sign * half_ow) + (-par_w if sign == 1 else 0)
        rectangle(msp, px, wc_y, par_w, par_h,
                  layer="SUPER-PARAPET", lw=35)
        hatch_rect(msp, px, wc_y, par_w, par_h,
                   pattern="ANSI31", scale=sc * 0.012, layer="STRUC-HATCHING")

    # ── Footpaths ─────────────────────────────────────────────────────────
    fp_h = 0.15 * sc
    if fp_l > 0:
        rectangle(msp, hx(-half_ow + kerb_l), wc_y, fp_l * sc, fp_h,
                  layer="SUPER-FOOTPATH", lw=25)
    if fp_r > 0:
        rectangle(msp, hx(half_cw + kerb_r), wc_y, fp_r * sc, fp_h,
                  layer="SUPER-FOOTPATH", lw=25)

    # ── Camber reference (dashed) ─────────────────────────────────────────
    if camber_mm > 0:
        pts_cam = []
        for i in range(21):
            xf = -half_cw + i * cw / 20.0
            yf = cs.camber_y_at_x(xf) / 1000.0 * sc * 3.0
            pts_cam.append((hx(xf), wc_y + yf))
        if len(pts_cam) >= 2:
            polyline(msp, pts_cam, layer="SUPER-CAMBER", color=6)
        text(msp, f"CAMBER {camber_mm}mm",
             hx(0), wc_y + camber_mm / 1000.0 * sc * 3.0 + th,
             height=th, layer="SUPER-CAMBER", halign="CENTER", color=6)

    # ── Width dimensions ──────────────────────────────────────────────────
    dim_y = wc_y + par_h + th * 4
    dim_linear_h(msp, hx(-half_cw), wc_y, hx(half_cw), wc_y,
                 dim_y=dim_y, label=f"CW = {cw:.3f} m", text_height=th)
    dim_linear_h(msp, hx(-half_ow), wc_y, hx(half_ow), wc_y,
                 dim_y=dim_y + th * 5, label=f"OW = {ow_m:.3f} m",
                 text_height=th)

    # ── Depth dimensions ──────────────────────────────────────────────────
    dim_x = hx(-half_ow) - th * 15
    dim_linear_v(msp, dim_x, soffit_y, dim_x, wc_y,
                 dim_x=dim_x - th * 6,
                 label=f"D = {deck_t_mm:.3f}m + WC {wc_t_mm:.3f}m",
                 text_height=th * 0.85)
    dim_linear_v(msp, dim_x, girder_bot_y, dim_x, soffit_y,
                 dim_x=dim_x - th * 6,
                 label=f"Girder {girder_d:.3f}m",
                 text_height=th * 0.85)

    # ── Level tags ────────────────────────────────────────────────────────
    road_rl = float(getattr(pm, "road_level_rl_m", 0) or 0)
    level_tag(msp, hx(half_ow) + th, wc_y, road_rl, text_height=th)
    text(msp, "TOP OF WC / ROAD LEVEL", hx(half_ow) + th * 12, wc_y,
         height=th, layer="TEXT-LEVEL")
    level_tag(msp, hx(half_ow) + th, soffit_y, road_rl - deck_t_mm - wc_t_mm,
              text_height=th)
    text(msp, "SOFFIT", hx(half_ow) + th * 12, soffit_y,
         height=th, layer="TEXT-LEVEL")

    # ── CL marker ─────────────────────────────────────────────────────────
    line(msp, (hx(0), girder_bot_y - th * 3), (hx(0), wc_y + par_h + th * 3),
         layer="STRUC-CENTRE")
    text(msp, "¢", hx(0) + th * 0.5, wc_y + par_h + th * 1.5,
         height=th * 1.4, layer="STRUC-CENTRE", halign="CENTER")

    # ── Labels ────────────────────────────────────────────────────────────
    text(msp, "SECTION A-A — TYPICAL MID-SPAN CROSS SECTION",
         cx, wc_y + par_h + th * 18,
         height=th * 1.5, layer="TEXT-HEADER", halign="CENTER")
    text(msp, f"Scale 1:{scale_denom}", cx, wc_y + par_h + th * 14,
         height=th, layer="TEXT-SPEC", halign="CENTER")

    # ── Scale bar ─────────────────────────────────────────────────────────
    scale_bar(msp, hx(-half_ow), girder_bot_y - th * 8,
              scale_denom, segments=4,
              seg_len_m=max(1.0, round(ow_m / 6)),
              text_height=th * 0.85)


__all__ = ["generate"]
