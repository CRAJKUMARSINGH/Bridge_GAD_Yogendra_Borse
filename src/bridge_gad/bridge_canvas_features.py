"""BridgeCanvas features integrated into Bridge GAD Generator.

Sourced from: BridgeCanvas/bridge_processor.py and BridgeCanvas/streamlit_app/app_with_all_features.py
Integrated features:
  - IRC/IS parameter validation with compliance scoring
  - DXF entity cleanup (orphan points, degenerate entities)
  - 5 standard bridge templates (simple, continuous, girder, culvert, arch)
  - Batch processing helper
  - Smart title block recentering utility
"""

from __future__ import annotations

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# ── IRC/IS Bridge Parameter Validator ────────────────────────────────────────

def validate_bridge_parameters(variables: Dict[str, Any]) -> Dict[str, Any]:
    """Validate bridge parameters against IRC/IS standards.

    Sourced from BridgeCanvas/streamlit_app/app_with_all_features.py::validate_bridge_parameters

    Returns:
        Dict with keys: is_valid, critical_issues, warnings, score (0-100)
    """
    issues: List[str] = []
    warnings: List[str] = []

    try:
        # Vertical clearance (IRC 5:2015 — minimum 5.5m)
        rtl   = float(variables.get("RTL",   variables.get("rtl",   100)))
        datum = float(variables.get("DATUM", variables.get("datum",  95)))
        clearance = rtl - datum
        if clearance < 5.5:
            issues.append(
                f"Vertical clearance {clearance:.2f}m < 5.5m (IRC 5:2015 minimum)"
            )

        # Slab thickness — L/20 rule
        span1  = float(variables.get("SPAN1",  variables.get("span1",  12)))
        slbthe = float(variables.get("SLBTHE", variables.get("slbthe", 0.75)))
        min_thickness = span1 / 20
        if slbthe < min_thickness:
            issues.append(
                f"Slab thickness {slbthe:.2f}m < {min_thickness:.2f}m (L/20 rule)"
            )

        # Pier width minimum
        piertw = float(variables.get("PIERTW", variables.get("piertw", 1.2)))
        if piertw < 1.0:
            warnings.append(f"Pier width {piertw:.2f}m < 1.0m (recommended minimum)")

        # Footing depth minimum
        futd = float(variables.get("FUTD", variables.get("futd", 2.0)))
        if futd < 0.8:
            warnings.append(f"Footing depth {futd:.2f}m < 0.8m (recommended minimum)")

        # Span limit for slab bridges
        if span1 > 50:
            warnings.append(f"Span {span1:.1f}m exceeds typical slab bridge limit (50m)")

        # Number of spans sanity check
        nspan = int(float(variables.get("NSPAN", variables.get("nspan", 1))))
        if nspan > 10:
            warnings.append(f"Unusual number of spans: {nspan}")

        # Skew angle
        skew = float(variables.get("SKEW", variables.get("skew", 0)))
        if abs(skew) > 45:
            issues.append(f"Skew angle {skew}° exceeds ±45° limit")

        # Deck width
        ccbr = float(variables.get("CCBR", variables.get("ccbr", 8.0)))
        if ccbr < 4.25:
            warnings.append(f"Carriageway width {ccbr:.2f}m < 4.25m (IRC 5 minimum for single lane)")

    except Exception as exc:
        warnings.append(f"Validation error: {exc}")

    score = max(0, 100 - (len(issues) * 20 + len(warnings) * 5))
    return {
        "is_valid":        len(issues) == 0,
        "critical_issues": issues,
        "warnings":        warnings,
        "score":           score,
    }


# ── DXF Entity Cleanup ────────────────────────────────────────────────────────

def cleanup_dxf_entities(doc, eps: float = 1e-6) -> Dict[str, int]:
    """Remove orphan/degenerate entities from a DXF document.

    Sourced from BridgeCanvas/bridge_processor.py::remove_orphan_points_and_degenerate_entities

    Removes:
      - Zero-length LINEs
      - LWPOLYLINEs with <2 distinct vertices or near-zero extents
      - Zero-radius CIRCLEs and ARCs
      - Stray POINT entities

    Returns:
        Dict with removed counts per entity type.
    """
    msp = doc.modelspace()
    removed = {
        "lines":      0,
        "polylines":  0,
        "circles":    0,
        "arcs":       0,
        "points":     0,
    }
    to_remove: List[Tuple[str, Any]] = []

    for e in list(msp.query("LINE")):
        try:
            s, t = e.dxf.start, e.dxf.end
            dx, dy, dz = float(s.x)-float(t.x), float(s.y)-float(t.y), float(s.z)-float(t.z)
            if dx*dx + dy*dy + dz*dz <= eps*eps:
                to_remove.append(("lines", e))
        except Exception:
            continue

    for e in list(msp.query("LWPOLYLINE")):
        try:
            pts = [tuple(p[:2]) for p in e.get_points("xy")]
            if len(pts) < 2:
                to_remove.append(("polylines", e)); continue
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if (max(xs)-min(xs))**2 + (max(ys)-min(ys))**2 <= eps*eps:
                to_remove.append(("polylines", e))
        except Exception:
            continue

    for e in list(msp.query("CIRCLE")):
        try:
            if float(e.dxf.radius) <= eps:
                to_remove.append(("circles", e))
        except Exception:
            continue

    for e in list(msp.query("ARC")):
        try:
            if float(e.dxf.radius) <= eps:
                to_remove.append(("arcs", e))
        except Exception:
            continue

    for e in list(msp.query("POINT")):
        to_remove.append(("points", e))

    for key, ent in to_remove:
        try:
            ent.destroy()
            removed[key] += 1
        except Exception:
            continue

    total = sum(removed.values())
    if total:
        logger.info("DXF cleanup removed %d entities: %s", total, removed)
    return removed


# ── Bridge Templates ──────────────────────────────────────────────────────────

BRIDGE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "simple_12m": {
        "name": "Simple Span 12m",
        "description": "Single span RCC slab bridge (12m)",
        "parameters": {
            "SCALE1": 186, "SCALE2": 1, "SKEW": 0, "DATUM": 95, "TOPRL": 100,
            "LEFT": 0, "RIGHT": 100, "XINCR": 5, "YINCR": 1, "NOCH": 2,
            "NSPAN": 1, "LBRIDGE": 12, "ABTL": 0, "RTL": 100.5, "SOFL": 99.5,
            "KERBW": 0.23, "KERBD": 0.15, "CCBR": 8.0, "SLBTHC": 0.6,
            "SLBTHE": 0.6, "SLBTHT": 0.6, "CAPT": 100.5, "CAPB": 99.3,
            "CAPW": 1.2, "PIERTW": 1.2, "BATTR": 10, "PIERST": 5, "PIERN": 0,
            "SPAN1": 12, "FUTRL": 90, "FUTD": 2, "FUTW": 2.5, "FUTL": 3.5,
            "DWTH": 0.3, "ALCW": 0.75, "ALCD": 1.2, "ALFB": 10, "ALFBL": 101,
            "ALTB": 10, "ALTBL": 100.5, "ALFO": 0.5, "ALBB": 5, "ALBBL": 101.5,
            "ABTLEN": 8.46, "LASLAB": 3.5, "APWTH": 8.46, "APTHK": 0.2,
            "WCTH": 0.08, "ALFL": 95, "ARFL": 95, "ALFBR": 100.75,
            "ALTBR": 100.5, "ALFD": 1.5, "ALBBR": 101.5,
        },
    },
    "continuous_3x12m": {
        "name": "Continuous 3×12m",
        "description": "3-span continuous RCC slab (3×12m)",
        "parameters": {
            "SCALE1": 186, "SCALE2": 1, "SKEW": 0, "DATUM": 95, "TOPRL": 100,
            "LEFT": 0, "RIGHT": 100, "XINCR": 5, "YINCR": 1, "NOCH": 2,
            "NSPAN": 3, "LBRIDGE": 36, "ABTL": 0, "RTL": 100.98, "SOFL": 99.5,
            "KERBW": 0.23, "KERBD": 0.15, "CCBR": 10.5, "SLBTHC": 0.75,
            "SLBTHE": 0.75, "SLBTHT": 0.75, "CAPT": 100.5, "CAPB": 99.3,
            "CAPW": 1.2, "PIERTW": 1.5, "BATTR": 10, "PIERST": 5, "PIERN": 2,
            "SPAN1": 12, "FUTRL": 90, "FUTD": 2, "FUTW": 4.5, "FUTL": 3.5,
            "DWTH": 0.3, "ALCW": 0.75, "ALCD": 1.2, "ALFB": 10, "ALFBL": 101,
            "ALTB": 10, "ALTBL": 100.5, "ALFO": 0.5, "ALBB": 5, "ALBBL": 101.5,
            "ABTLEN": 11.0, "LASLAB": 3.5, "APWTH": 11.0, "APTHK": 0.2,
            "WCTH": 0.08, "ALFL": 95, "ARFL": 95, "ALFBR": 100.75,
            "ALTBR": 100.5, "ALFD": 1.5, "ALBBR": 101.5,
        },
    },
    "girder_4x18m": {
        "name": "Girder Bridge 4×18m",
        "description": "4-span RCC girder bridge (4×18m)",
        "parameters": {
            "SCALE1": 186, "SCALE2": 1, "SKEW": 0, "DATUM": 95, "TOPRL": 105,
            "LEFT": 0, "RIGHT": 100, "XINCR": 5, "YINCR": 1, "NOCH": 2,
            "NSPAN": 4, "LBRIDGE": 72, "ABTL": 0, "RTL": 101.5, "SOFL": 99.8,
            "KERBW": 0.23, "KERBD": 0.15, "CCBR": 12.0, "SLBTHC": 0.9,
            "SLBTHE": 0.9, "SLBTHT": 0.9, "CAPT": 101.0, "CAPB": 99.8,
            "CAPW": 1.5, "PIERTW": 2.0, "BATTR": 10, "PIERST": 6, "PIERN": 3,
            "SPAN1": 18, "FUTRL": 90, "FUTD": 2.5, "FUTW": 6.5, "FUTL": 4.0,
            "DWTH": 0.3, "ALCW": 0.75, "ALCD": 1.2, "ALFB": 10, "ALFBL": 101,
            "ALTB": 10, "ALTBL": 100.5, "ALFO": 0.5, "ALBB": 5, "ALBBL": 101.5,
            "ABTLEN": 12.5, "LASLAB": 3.5, "APWTH": 12.5, "APTHK": 0.25,
            "WCTH": 0.08, "ALFL": 95, "ARFL": 95, "ALFBR": 100.75,
            "ALTBR": 100.5, "ALFD": 1.5, "ALBBR": 101.5,
        },
    },
    "box_culvert_8m": {
        "name": "Box Culvert 8m",
        "description": "Single cell box culvert (8m span)",
        "parameters": {
            "SCALE1": 186, "SCALE2": 1, "SKEW": 0, "DATUM": 95, "TOPRL": 100,
            "LEFT": 0, "RIGHT": 100, "XINCR": 5, "YINCR": 1, "NOCH": 2,
            "NSPAN": 1, "LBRIDGE": 8, "ABTL": 0, "RTL": 100.0, "SOFL": 99.5,
            "KERBW": 0.23, "KERBD": 0.15, "CCBR": 8.0, "SLBTHC": 0.5,
            "SLBTHE": 0.5, "SLBTHT": 0.5, "CAPT": 100.0, "CAPB": 99.2,
            "CAPW": 1.0, "PIERTW": 0.8, "BATTR": 10, "PIERST": 4, "PIERN": 0,
            "SPAN1": 8, "FUTRL": 92, "FUTD": 1.5, "FUTW": 3.5, "FUTL": 3.0,
            "DWTH": 0.3, "ALCW": 0.75, "ALCD": 1.0, "ALFB": 10, "ALFBL": 100,
            "ALTB": 10, "ALTBL": 99.5, "ALFO": 0.5, "ALBB": 5, "ALBBL": 100.5,
            "ABTLEN": 8.46, "LASLAB": 3.0, "APWTH": 8.46, "APTHK": 0.2,
            "WCTH": 0.08, "ALFL": 95, "ARFL": 95, "ALFBR": 100.25,
            "ALTBR": 99.5, "ALFD": 1.5, "ALBBR": 100.5,
        },
    },
    "arch_24m": {
        "name": "Arch Bridge 24m",
        "description": "RCC arch bridge (24m span)",
        "parameters": {
            "SCALE1": 186, "SCALE2": 1, "SKEW": 0, "DATUM": 95, "TOPRL": 105,
            "LEFT": 0, "RIGHT": 100, "XINCR": 5, "YINCR": 1, "NOCH": 2,
            "NSPAN": 1, "LBRIDGE": 24, "ABTL": 0, "RTL": 102.0, "SOFL": 100.5,
            "KERBW": 0.23, "KERBD": 0.15, "CCBR": 11.0, "SLBTHC": 0.8,
            "SLBTHE": 0.8, "SLBTHT": 0.8, "CAPT": 101.5, "CAPB": 100.3,
            "CAPW": 1.5, "PIERTW": 2.5, "BATTR": 10, "PIERST": 6, "PIERN": 0,
            "SPAN1": 24, "FUTRL": 90, "FUTD": 2.5, "FUTW": 7.0, "FUTL": 4.5,
            "DWTH": 0.3, "ALCW": 0.75, "ALCD": 1.2, "ALFB": 10, "ALFBL": 101,
            "ALTB": 10, "ALTBL": 100.5, "ALFO": 0.5, "ALBB": 5, "ALBBL": 101.5,
            "ABTLEN": 11.5, "LASLAB": 3.5, "APWTH": 11.5, "APTHK": 0.25,
            "WCTH": 0.08, "ALFL": 95, "ARFL": 95, "ALFBR": 100.75,
            "ALTBR": 100.5, "ALFD": 1.5, "ALBBR": 101.5,
        },
    },
}


def make_template_excel(params: Dict[str, Any]) -> bytes:
    """Return Excel bytes for a template parameter dict."""
    data = [[v, k, k] for k, v in params.items()]
    df = pd.DataFrame(data, columns=["Value", "Variable", "Description"])
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Parameters")
    buf.seek(0)
    return buf.getvalue()


# ── Batch Processing ──────────────────────────────────────────────────────────

def batch_generate(
    files: List[Tuple[str, bytes]],
    acad_version: str = "R2010",
) -> List[Dict[str, Any]]:
    """Generate DXF for multiple Excel files.

    Args:
        files: List of (filename, bytes) tuples.
        acad_version: AutoCAD version string.

    Returns:
        List of result dicts with keys: filename, success, dxf_bytes, error.
    """
    import tempfile
    from .bridge_generator import BridgeGADGenerator

    results = []
    for filename, file_bytes in files:
        safe_name = Path(filename).name
        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                excel_path = tmp_path / safe_name
                excel_path.write_bytes(file_bytes)
                output_path = tmp_path / f"{excel_path.stem}.dxf"

                gen = BridgeGADGenerator(acad_version=acad_version)
                ok = gen.generate_complete_drawing(excel_path, output_path)

                if ok and output_path.exists():
                    results.append({
                        "filename": safe_name,
                        "success":  True,
                        "dxf_bytes": output_path.read_bytes(),
                        "error":    None,
                    })
                else:
                    results.append({
                        "filename": safe_name,
                        "success":  False,
                        "dxf_bytes": None,
                        "error":    "Generation returned no output",
                    })
        except Exception as exc:
            logger.exception("Batch generation failed for %s", safe_name)
            results.append({
                "filename": safe_name,
                "success":  False,
                "dxf_bytes": None,
                "error":    str(exc),
            })
    return results


def batch_results_to_zip(results: List[Dict[str, Any]]) -> bytes:
    """Bundle successful batch results into a ZIP archive."""
    import zipfile, io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in results:
            if r["success"] and r.get("dxf_bytes"):
                stem = Path(r["filename"]).stem
                zf.writestr(f"{stem}.dxf", r["dxf_bytes"])
    buf.seek(0)
    return buf.getvalue()


# ── Smart Title Recentering ───────────────────────────────────────────────────

def smart_recenter_title(
    elements: List[Dict[str, Any]],
    *,
    title_tag: str = "title_block",
    target_origin: Tuple[float, float] = (50.0, 50.0),
) -> None:
    """Move the title block to target_origin, shifting the whole drawing.

    Sourced from BridgeCanvas/smart_title.py
    """
    titles = [e for e in elements if e.get("tag") == title_tag]
    if not titles:
        return
    title = titles[0]
    dx = target_origin[0] - title["x"]
    dy = target_origin[1] - title["y"]
    for el in elements:
        el["x"] += dx
        el["y"] += dy
