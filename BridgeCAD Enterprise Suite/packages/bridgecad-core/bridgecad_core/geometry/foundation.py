"""
bridgecad_core.geometry.foundation — Foundation layout geometry.
M1 Week 1 Day 4: N×M pile group grid, pile cap corners,
well-foundation outer circle, open-footing stepped outline.
All outputs in metres, centred at (0, 0) of the pier/abutment centreline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bridgecad_core.models import BridgeProject


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass
class PileGroupLayout:
    """Pile group and pile-cap geometry centred at (0, 0).

    Coordinate convention
    ---------------------
    - X is transverse (parallel to the bridge axis at plan view).
    - Y is longitudinal (perpendicular to the bridge axis, toward the river).
    - (0, 0) is the pier / abutment centreline at top of pile cap.
    """

    # ---- pile data -------------------------------------------------------
    pile_diameter_m: float            = 0.0
    pile_spacing_m: float             = 0.0
    piles_per_group: int              = 0
    pile_rows: int                    = 0
    pile_cols: int                    = 0

    pile_positions: list[tuple[float, float]] = field(default_factory=list)
    """(x, y) centre of each pile (metres from group centroid)."""

    # ---- pile cap --------------------------------------------------------
    pile_cap_width_m: float           = 0.0   # transverse
    pile_cap_length_m: float          = 0.0   # longitudinal
    pile_cap_thickness_m: float       = 0.0
    pile_cap_corners: list[tuple[float, float]] = field(default_factory=list)
    """4 corners of pile cap rectangle (x, y): BL, BR, TR, TL."""

    # ---- well foundation (if used instead of piles) ----------------------
    well_outer_radius_m: float        = 0.0
    well_inner_radius_m: float        = 0.0
    well_total_depth_m: float         = 0.0

    # ---- open footing stepped outline -----------------------------------
    open_footing_steps: list[tuple[float, float, float, float]] = field(default_factory=list)
    """List of (x_left, y_bottom, width, height) for each footing step."""


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def compute_pile_group_layout(project: "BridgeProject") -> PileGroupLayout:
    """Derive pile group geometry for the primary pier from a validated BridgeProject.

    Parameters
    ----------
    project : BridgeProject
        Fully-validated Pydantic model instance.

    Returns
    -------
    PileGroupLayout
        Populated dataclass.  For well / open foundations the pile_positions
        list is empty and the relevant well/footing fields are set instead.
    """
    fd  = project.foundation_details
    sub = project.substructure

    from bridgecad_core.types import FoundationType

    foundation_type = fd.type

    # ---- pile foundation ------------------------------------------------
    if foundation_type == FoundationType.PILE:
        pile_dia_m    = float(fd.pile_diameter_mm) / 1000.0 if fd.pile_diameter_mm else 1.2
        pile_spacing  = float(fd.pile_spacing_m)             if fd.pile_spacing_m  else 2.4
        n_piles       = int(fd.piles_per_pier)               if fd.piles_per_pier  else 4
        cap_thick_m   = float(fd.pile_cap_thickness_mm) / 1000.0 if fd.pile_cap_thickness_mm else 1.5

        # --- determine rows × cols (prefer near-square arrangement) ------
        cols = max(1, math.ceil(math.sqrt(n_piles)))
        rows = max(1, math.ceil(n_piles / cols))
        # Ensure rows × cols >= n_piles
        while rows * cols < n_piles:
            cols += 1

        # --- generate pile positions (centred at origin) -----------------
        pile_positions: list[tuple[float, float]] = []
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= n_piles:
                    break
                x = (c - (cols - 1) / 2.0) * pile_spacing
                y = (r - (rows - 1) / 2.0) * pile_spacing
                pile_positions.append((x, y))

        # --- pile cap size (100 mm overhang each side per IS:2911) -------
        cap_w = (cols - 1) * pile_spacing + pile_dia_m + 2 * 0.100
        cap_l = (rows - 1) * pile_spacing + pile_dia_m + 2 * 0.100
        half_w = cap_w / 2.0
        half_l = cap_l / 2.0

        cap_corners = [
            (-half_w, -half_l),   # BL
            ( half_w, -half_l),   # BR
            ( half_w,  half_l),   # TR
            (-half_w,  half_l),   # TL
        ]

        return PileGroupLayout(
            pile_diameter_m=pile_dia_m,
            pile_spacing_m=pile_spacing,
            piles_per_group=n_piles,
            pile_rows=rows,
            pile_cols=cols,
            pile_positions=pile_positions,
            pile_cap_width_m=cap_w,
            pile_cap_length_m=cap_l,
            pile_cap_thickness_m=cap_thick_m,
            pile_cap_corners=cap_corners,
        )

    # ---- well (caisson) foundation --------------------------------------
    from bridgecad_core.types import FoundationType as FT
    if foundation_type in (FT.WELL, FT.WELL_PLUS_PILE):
        # Well outer diameter inferred from pier shaft width (approx 2.5× shaft)
        pier_shaft_w = float(sub.pier_shaft_width_m) if sub.pier_shaft_width_m else 2.0
        outer_r = max(pier_shaft_w, 1.5)            # minimum 1.5 m outer radius
        inner_r = outer_r * 0.55                     # steining thickness ≈ 0.45 × outer_r
        # Depth from scour level to pile cutoff (approximate)
        pile_cut = float(project.foundation_details.pile_cutoff_level_m) if fd.pile_cutoff_level_m else 0.0
        well_depth = max(0.0, float(project.hydraulic_data.scour_level_m) - pile_cut + 5.0)

        return PileGroupLayout(
            well_outer_radius_m=outer_r,
            well_inner_radius_m=inner_r,
            well_total_depth_m=well_depth,
        )

    # ---- open / raft foundation -----------------------------------------
    # Build stepped outline: base footing + wall footing (2-step common)
    footing_width_base = float(sub.pier_shaft_width_m) * 3.0 if sub.pier_shaft_width_m else 3.0
    footing_width_top  = float(sub.pier_shaft_width_m) * 1.8 if sub.pier_shaft_width_m else 1.8
    step_height = 0.3   # 300 mm per step (typical)

    steps = [
        (-(footing_width_base / 2), 0.0, footing_width_base, step_height),      # base
        (-(footing_width_top  / 2), step_height, footing_width_top, step_height), # top step
    ]

    return PileGroupLayout(
        open_footing_steps=steps,
    )


__all__ = ["PileGroupLayout", "compute_pile_group_layout"]
