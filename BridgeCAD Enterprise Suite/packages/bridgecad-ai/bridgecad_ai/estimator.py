"""
bridgecad_ai.estimator — No-API cost and quantity predictor.

Uses parametric heuristics derived from MORTH unit rates and standard
IRC proportioning rules.  No external API call required.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QuantityEstimate:
    concrete_superstructure_cum: float
    concrete_substructure_cum:   float
    concrete_foundation_cum:     float
    rebar_mt:                    float
    prestress_mt:                float
    formwork_sqm:                float
    wc_sqm:                      float


@dataclass
class CostEstimate:
    civil_works_inr:    float
    contingency_inr:    float
    grand_total_inr:    float
    cost_per_sqm_inr:   float
    cost_per_rm_inr:    float


def estimate_quantities(
    total_length_m:       float,
    overall_width_m:      float,
    n_spans:              int,
    pier_height_m:        float    = 8.0,
    pile_length_m:        float    = 15.0,
    piles_per_support:    int      = 4,
    is_prestressed:       bool     = False,
) -> QuantityEstimate:
    """Parametric quantity estimation using standard IRC proportioning."""
    deck_area = total_length_m * overall_width_m

    # Superstructure (deck slab + girders)
    conc_sup = deck_area * 0.55     # CUM/SQM ratio for T-beam deck

    # Substructure (piers + abutments)
    n_piers     = n_spans - 1
    n_supports  = n_piers + 2
    conc_sub    = (n_piers * 3.14159 * 0.75**2 * pier_height_m  # pier shafts
                   + n_supports * overall_width_m * 2.0 * 0.8)  # pier caps + abut

    # Foundation (pile caps + piles)
    conc_fnd   = (n_supports * piles_per_support *
                  3.14159 * 0.5**2 * pile_length_m  # pile volume
                  + n_supports * overall_width_m * 2.5 * 1.5)  # pile caps

    # Reinforcement
    rebar_mt   = (conc_sup + conc_sub + conc_fnd) * 0.095  # ~95 kg/CUM

    # Prestress (only if prestressed)
    prestress  = conc_sup * 0.025 if is_prestressed else 0.0  # ~25 kg/CUM

    # Formwork (superstructure curved soffit)
    formwork   = deck_area * 2.5   # SQM

    # Wearing coat
    wc_sqm     = total_length_m * (overall_width_m * 0.85)  # carriageway only

    return QuantityEstimate(
        concrete_superstructure_cum = round(conc_sup, 1),
        concrete_substructure_cum   = round(conc_sub, 1),
        concrete_foundation_cum     = round(conc_fnd, 1),
        rebar_mt                    = round(rebar_mt, 1),
        prestress_mt                = round(prestress, 2),
        formwork_sqm                = round(formwork, 1),
        wc_sqm                      = round(wc_sqm, 1),
    )


def estimate_cost(
    qty: QuantityEstimate,
    contingency_pct: float = 15.0,
    state: str | None = None,
) -> CostEstimate:
    """Price the quantity estimate using indicative 2024-25 MORTH rates."""
    # Unit rates (INR/unit) — same basis as rates_db seed values
    rates = {
        "conc_sup":     10500.0,  # M40 superstructure
        "conc_sub":      8400.0,  # M30 substructure
        "conc_fnd":      7200.0,  # M25 foundation
        "rebar":        75000.0,  # Fe500D MT
        "prestress":   145000.0,  # G1860 strand MT
        "formwork":      1800.0,  # curved soffit SQM
        "wc":             380.0,  # BC 40mm SQM
    }

    # State PWD adjustment factor (±10–20% typical)
    adj = {"MH": 1.05, "GJ": 1.02, "RJ": 0.95, "UP": 0.97,
           "KA": 1.08, "TN": 1.06, "AP": 1.04, "TS": 1.04}.get(
        (state or "").upper(), 1.0
    )

    civil = (
        qty.concrete_superstructure_cum * rates["conc_sup"]
        + qty.concrete_substructure_cum   * rates["conc_sub"]
        + qty.concrete_foundation_cum     * rates["conc_fnd"]
        + qty.rebar_mt                    * rates["rebar"]
        + qty.prestress_mt                * rates["prestress"]
        + qty.formwork_sqm                * rates["formwork"]
        + qty.wc_sqm                      * rates["wc"]
    ) * adj

    contingency  = civil * contingency_pct / 100.0
    grand_total  = civil + contingency

    # deck area proxy
    deck_area = qty.wc_sqm / 0.85 if qty.wc_sqm > 0 else 1.0
    total_len = deck_area / max(qty.wc_sqm / qty.wc_sqm, 1)  # rough

    return CostEstimate(
        civil_works_inr  = round(civil,       0),
        contingency_inr  = round(contingency, 0),
        grand_total_inr  = round(grand_total, 0),
        cost_per_sqm_inr = round(grand_total / max(deck_area, 1), 0),
        cost_per_rm_inr  = round(grand_total / max(total_len, 1), 0),
    )


__all__ = ["QuantityEstimate", "CostEstimate", "estimate_quantities", "estimate_cost"]
