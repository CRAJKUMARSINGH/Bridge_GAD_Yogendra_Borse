#!/usr/bin/env python3
"""
Run batch generation on SweetWilledDocuments using BridgeGAD-00, exporting DXF, PDF, SVG, HTML, PNG.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bridge_gad.bridge_generator import BridgeGADGenerator
from bridge_gad.output_formats import MultiFormatExporter

IN_DIR = ROOT / "Sample_test_input_files" / "SweetWilledDocuments"
OUT_DIR = ROOT / "BATCH_OUTPUTS"
OUT_DIR.mkdir(exist_ok=True)

formats = ["pdf", "html", "svg", "png"]

def main():
    inputs = sorted(IN_DIR.glob("SweetWilledDocument-*.xlsx"))
    if not inputs:
        print(f"No inputs found in {IN_DIR}. Run scripts/generate_sweetwilled_docs.py first.")
        return 1

    for excel in inputs:
        print(f"Processing {excel.name}...")
        gen = BridgeGADGenerator()
        out_base = OUT_DIR / excel.stem
        out_base.parent.mkdir(exist_ok=True, parents=True)
        dxf_path = out_base.with_suffix(".dxf")

        if not gen.generate_complete_drawing(excel, dxf_path):
            print(f"  ❌ Failed to generate DXF for {excel.name}")
            continue
        else:
            print(f"  ✅ DXF: {dxf_path}")

        exporter = MultiFormatExporter(gen)
        for fmt in formats:
            try:
                p = exporter.export(out_base.with_suffix(f".{fmt}"), fmt)
                print(f"  ✅ {fmt.upper()}: {p}")
            except Exception as e:
                print(f"  ❌ {fmt.upper()} failed: {e}")

    print("\nBatch generation complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
