"""
bridgecad_export.orchestrator — Unified export: DXF + BOQ + QA report → ZIP bundle.
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

BASE = Path(__file__).parents[4]   # repo root


def _core_path():
    p = BASE / "packages" / "bridgecad-core"
    if p not in [Path(s) for s in sys.path]:
        sys.path.insert(0, str(p))


def export_all(
    project: Any,
    output_dir: str | Path,
    prefix: str       = "GAD",
    state: str | None = None,
    scale_denom: int  = 100,
) -> Path:
    """Run the full export pipeline and return path to the ZIP bundle.

    Steps
    -----
    1. Generate 7-sheet DXF package (bridgecad-draw)
    2. Extract and price BOQ → Excel + CSV (bridgecad-bill)
    3. Run QA checks → HTML report (bridgecad-qa)
    4. Bundle everything into a ZIP (bridgecad-export.bundler)

    Returns
    -------
    Path
        Path to the generated ``{prefix}_bundle.zip``.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results: dict[str, list[Path]] = {"dxf": [], "bill": [], "qa": []}

    # ── Step 1: DXF drawings ──────────────────────────────────────────────
    try:
        draw_out = out / "drawings"
        sys.path.insert(0, str(BASE / "packages" / "bridgecad-draw"))
        from bridgecad_draw.booklet import generate_package
        dxf_files = generate_package(project, draw_out, prefix=prefix,
                                     scale_denom=scale_denom)
        results["dxf"] = dxf_files
        logger.info("DXF: %d sheets generated", len(dxf_files))
    except Exception as exc:
        logger.warning("DXF generation failed: %s", exc)

    # ── Step 2: Bill of Quantities ────────────────────────────────────────
    try:
        bill_out = out / "bill"
        bill_out.mkdir(exist_ok=True)
        sys.path.insert(0, str(BASE / "packages" / "bridgecad-bill"))
        from bridgecad_bill.processor import extract_and_price
        from bridgecad_bill.formatters.excel_formatter import format_excel
        from bridgecad_bill.formatters.csv_formatter   import format_csv
        boq = extract_and_price(project, state=state)
        xlsx_path = format_excel(boq, bill_out / f"{prefix}_BOQ.xlsx")
        csv_path  = format_csv(boq,   bill_out / f"{prefix}_BOQ.csv")
        results["bill"] = [xlsx_path, csv_path]
        logger.info("BOQ: grand total INR %s  (xlsx+csv)", f"{float(boq.grand_total):,.0f}")
    except Exception as exc:
        logger.warning("BOQ generation failed: %s", exc)

    # ── Step 3: QA report ─────────────────────────────────────────────────
    try:
        qa_out = out / "qa"
        qa_out.mkdir(exist_ok=True)
        sys.path.insert(0, str(BASE / "packages" / "bridgecad-core"))
        from bridgecad_core.validation import run_all
        report = run_all(project)

        sys.path.insert(0, str(BASE / "packages" / "bridgecad-qa"))
        from bridgecad_qa.reports import generate_html_report
        html_path = generate_html_report(report, qa_out / f"{prefix}_QA.html", project)
        results["qa"] = [html_path]
        logger.info("QA: score=%d  critical_fails=%d",
                    report.score, report.critical_fail_count)
    except Exception as exc:
        logger.warning("QA report failed: %s", exc)

    # ── Step 4: ZIP bundle ────────────────────────────────────────────────
    from .bundler import create_bundle
    bundle_path = create_bundle(out, prefix, results)
    logger.info("Bundle: %s  (%.1f KB)", bundle_path.name,
                bundle_path.stat().st_size / 1024)
    return bundle_path


__all__ = ["export_all"]
