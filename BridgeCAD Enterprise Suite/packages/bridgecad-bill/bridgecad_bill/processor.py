"""
bridgecad_bill.processor — Extract quantities from BridgeProject and build a
priced BillOfQuantities using the MORTH rates database.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .models import BillOfQuantities, BillSection, BillItem
from .rates_db import get_rates_db


def extract_and_price(
    project: Any,
    state: str | None = None,
    contingency_pct: Decimal = Decimal("15"),
) -> BillOfQuantities:
    """Build a fully-priced BOQ from a BridgeProject.

    Parameters
    ----------
    project : BridgeProject
    state : str | None
        Two-letter state code for PWD rate override (e.g. "MH").
    contingency_pct : Decimal
        Contingency percentage to add on top of civil works total.

    Returns
    -------
    BillOfQuantities
    """
    db   = get_rates_db()
    pm   = project.project_master
    gi   = project.geometry_input
    ss   = project.superstructure
    sub  = project.substructure
    fd   = project.foundation_details
    calc = project.calculations
    bj   = project.bearings_joints

    total_len  = float(gi.total_length_m)
    overall_w  = float(gi.overall_width_m)
    cw         = float(gi.carriageway_width_m or 7.5)

    conc_fnd   = Decimal(str(float(getattr(calc, "concrete_volume_foundation_cum", 0) or 0)))
    conc_sub   = Decimal(str(float(getattr(calc, "concrete_volume_substructure_cum", 0) or 0)))
    conc_sup   = Decimal(str(float(getattr(calc, "concrete_volume_superstructure_cum", 0) or 0)))
    rebar_mt   = Decimal(str(float(getattr(calc, "rebar_weight_tonnes_approx", 0) or 0)))
    prestress  = Decimal(str(float(getattr(calc, "prestress_tonnes_approx", 0) or 0)))
    bearing_n  = int(getattr(calc, "bearing_count", 0) or 0)
    expjt_n    = int(getattr(calc, "expansion_joint_count", 0) or 0)

    wc_sqm       = Decimal(str(total_len * cw))
    formwork_sqm = Decimal(str(round(float(conc_sup) * 4.5, 1)))
    app_l        = Decimal(str(float(getattr(sub, "approach_slab_length_m", 3.5) or 3.5)))
    app_t        = Decimal(str(float(getattr(sub, "approach_slab_thickness_mm", 200) or 200) / 1000.0))
    app_cum      = (app_l * Decimal(str(overall_w)) * app_t * 2).quantize(Decimal("0.01"))
    expjt_rm     = Decimal(str(overall_w * expjt_n))
    railing_rm   = Decimal(str(total_len * 2 + float(app_l) * 4))
    wp_sqm       = Decimal(str(total_len * overall_w))
    earthwork    = Decimal(str(round(total_len * overall_w * 2.5, 1)))
    pile_len_total = Decimal(str(
        float(getattr(fd, "pile_length_m", 0) or 0) *
        int(getattr(fd, "piles_per_pier", 0) or 0) *
        (int(len([s for s in gi.span_lengths_m])) + 1)  # per support
    ))

    # Pile item code based on diameter
    pile_dia = int(getattr(fd, "pile_diameter_mm", 0) or 0)
    if pile_dia <= 600:
        pile_code = "1801.1"
    elif pile_dia <= 1000:
        pile_code = "1801.2"
    elif pile_dia <= 1200:
        pile_code = "1801.3"
    else:
        pile_code = "1801.4"

    # Concrete code based on grade
    def _conc_code(grade_name: str) -> str:
        mapping = {
            "M20": "1701.1", "M25": "1701.2", "M30": "1701.3",
            "M35": "1701.4", "M40": "1701.5", "M45": "1701.6",
            "M50": "1701.7", "M55": "1701.8",
        }
        return mapping.get(grade_name, "1701.3")

    fnd_grade = getattr(getattr(project.materials, "concrete_foundation", None), "name", "M25") or "M25"
    sub_grade = getattr(getattr(project.materials, "concrete_substructure", None), "name", "M30") or "M30"
    sup_grade = getattr(getattr(project.materials, "concrete_superstructure", None), "name", "M40") or "M40"

    def _item(code: str, qty: Decimal, override_desc: str | None = None) -> BillItem:
        m = db.meta(code)
        desc = override_desc or (m[0] if m else code)
        unit = m[1] if m else "UNIT"
        ref  = m[2] if m else ""
        rate = db.get(code, state)
        item = BillItem(
            item_code=code, description=desc, unit=unit,
            quantity=qty, rate=rate, ref=ref,
        )
        item.compute_amount()
        return item

    boq = BillOfQuantities(
        project_name = str(getattr(pm, "project_title", "") or ""),
        bridge_name  = str(getattr(pm, "bridge_name",   "") or ""),
        chainage_km  = str(float(getattr(pm, "chainage_km", 0) or 0)),
        contingency_pct = contingency_pct,
    )

    # ── Section 1: Earthwork ─────────────────────────────────────────────
    sec1 = BillSection("300", "EARTHWORK AND EMBANKMENT")
    sec1.add(_item("301.1", (conc_fnd * Decimal("3.0")).quantize(Decimal("0.1")),
                   "Excavation for pile caps and footings"))
    sec1.add(_item("301.2", earthwork, "Embankment for approach roads (both sides)"))
    boq.add_section(sec1)

    # ── Section 2: Piling ────────────────────────────────────────────────
    sec2 = BillSection("1800", "PILING AND FOUNDATION")
    if pile_len_total > 0:
        sec2.add(_item(pile_code, pile_len_total))
        sec2.add(_item("1801.6", Decimal(str(int(getattr(fd, "piles_per_pier", 4) or 4) * 2))))
    sec2.add(_item("1701.2", conc_fnd,
                   f"Concrete {fnd_grade} — pile cap and foundation"))
    sec2.add(_item("1702.1", (conc_fnd * Decimal("2.5")).quantize(Decimal("0.1")),
                   "Formwork — pile cap and footing"))
    boq.add_section(sec2)

    # ── Section 3: Substructure ──────────────────────────────────────────
    sec3 = BillSection("1700A", "SUBSTRUCTURE — PIER AND ABUTMENT")
    sec3.add(_item(_conc_code(sub_grade), conc_sub,
                   f"Concrete {sub_grade} — pier shaft, cap, abutment wall"))
    sec3.add(_item("1702.1", formwork_sqm * Decimal("0.4"),
                   "Formwork — substructure (pier/abutment)"))
    sec3.add(_item("2901.4", (conc_sub * Decimal("1.2")).quantize(Decimal("0.1")),
                   "Select granular backfill behind abutments"))
    sec3.add(_item("2901.2", Decimal(str(int(total_len / 1.5))),
                   "Weep holes 100mm dia in abutment/wing wall"))
    boq.add_section(sec3)

    # ── Section 4: Superstructure ────────────────────────────────────────
    sec4 = BillSection("1700B", "SUPERSTRUCTURE — DECK AND GIRDERS")
    sec4.add(_item(_conc_code(sup_grade), conc_sup,
                   f"Concrete {sup_grade} — girders, deck slab"))
    sec4.add(_item("1702.2", formwork_sqm, "Formwork — superstructure curved soffit"))
    sec4.add(_item("1601.1", rebar_mt, "Reinforcement steel Fe500D — all items"))
    if prestress > 0:
        sec4.add(_item("1601.2", prestress, "Prestressing strand G1860 supply, fix, stress"))
        sec4.add(_item("1703.1", Decimal(str(total_len * 4)), "Duct grouting for prestress tendons"))
    sec4.add(_item("501.3", wc_sqm, "Bituminous concrete (BC) wearing coat 40mm"))
    sec4.add(_item("2601.1", wp_sqm, "Bituminous waterproofing membrane on deck"))
    boq.add_section(sec4)

    # ── Section 5: Approach Slab ─────────────────────────────────────────
    sec5 = BillSection("2900A", "APPROACH SLAB AND APPURTENANCES")
    sec5.add(_item("2901.1", app_cum, f"Approach slab M30 — both ends"))
    sec5.add(_item("1702.1", (app_cum * Decimal("4")).quantize(Decimal("0.1")),
                   "Formwork — approach slab"))
    boq.add_section(sec5)

    # ── Section 6: Bearings & Joints ─────────────────────────────────────
    sec6 = BillSection("2700", "BEARINGS AND EXPANSION JOINTS")
    if bearing_n > 0:
        sec6.add(_item("2701.1", Decimal(str(bearing_n)),
                       f"Bearings supply & install ({bearing_n} nos)"))
    if expjt_rm > 0:
        sec6.add(_item("2801.2", expjt_rm,
                       f"Strip seal expansion joints ({expjt_n} locations)"))
    boq.add_section(sec6)

    # ── Section 7: Safety Works ───────────────────────────────────────────
    sec7 = BillSection("800", "SAFETY AND TRAFFIC WORKS")
    sec7.add(_item("801.1", railing_rm * Decimal("2"),
                   "Metal beam crash barrier (both sides, both ends)"))
    sec7.add(_item("2601.3", Decimal(str(int(total_len / 6))),
                   "Deck scupper outlets"))
    boq.add_section(sec7)

    # ── Section 8: River Training ─────────────────────────────────────────
    sec8 = BillSection("2500", "RIVER TRAINING AND SCOUR PROTECTION")
    sec8.add(_item("601.2", Decimal(str(round(total_len * overall_w * 0.3, 1))),
                   "Boulder launching apron at piers and abutments"))
    sec8.add(_item("601.1", Decimal(str(round(total_len * 2.0, 1))),
                   "Stone pitching on bank protection"))
    boq.add_section(sec8)

    return boq


__all__ = ["extract_and_price"]
