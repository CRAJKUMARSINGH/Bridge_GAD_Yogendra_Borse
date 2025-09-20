#!/usr/bin/env python3
"""
Generate SweetWilledDocument-01..10 Excel inputs for BridgeGAD-00.
Each file follows the (Value, Variable, Description) row format expected by the generator.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Sample_test_input_files" / "SweetWilledDocuments"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Base data template adapted from create_sample_input.py
base_rows = [
    [186, "SCALE1", "Scale1 - Drawing scale for plans and elevations"],
    [100, "SCALE2", "Scale2 - Drawing scale for sections"],
    [0.00, "SKEW", "Degree Of Skew In Plan Of The Bridge"],
    [100.00, "DATUM", "Datum level for the drawing"],
    [110.00, "TOPRL", "Top RL Of The Bridge"],
    [0.00, "LEFT", "Left Most Chainage Of The Bridge"],
    [50.00, "RIGHT", "Right Most Chainage Of The Bridge"],
    [10.00, "XINCR", "Chainage Increment In X Direction"],
    [1.00, "YINCR", "Elevation Increment In Y Direction"],
    [21, "NOCH", "Total No. Of Chainages On C/S"],
    [3, "NSPAN", "Number of Spans"],
    [36.00, "LBRIDGE", "Length Of Bridge"],
    [0.00, "ABTL", "Read Chainage Of Left Abutment"],
    [110.50, "RTL", "Road Top Level"],
    [109.50, "SOFL", "Soffit Level"],
    [0.23, "KERBW", "Width Of Kerb At Deck Top"],
    [0.23, "KERBD", "Depth Of Kerb Above Deck Top"],
    [11.10, "CCBR", "Clear Carriageway Width Of Bridge"],
    [0.90, "SLBTHC", "Thickness Of Slab At Centre"],
    [0.75, "SLBTHE", "Thickness Of Slab At Edge"],
    [0.75, "SLBTHT", "Thickness Of Slab At Tip"],
    [110.00, "CAPT", "Pier Cap Top RL"],
    [109.40, "CAPB", "Pier Cap Bottom RL = Pier Top"],
    [1.20, "CAPW", "Cap Width"],
    [1.20, "PIERTW", "Pier Top Width"],
    [10.00, "BATTR", "Pier Batter"],
    [12.00, "PIERST", "Straight Length Of Pier"],
    [1.00, "PIERN", "Sr No Of Pier"],
    [12.00, "SPAN1", "Span Individual Length"],
    [100.00, "FUTRL", "Founding RL Of Pier Found"],
    [1.00, "FUTD", "Depth Of Footing"],
    [4.50, "FUTW", "Width Of Rect Footing"],
    [12.00, "FUTL", "Length Of Footing Along Current Direction"],
    [12.00, "ABTLEN", "Length Of Abutment Along Current Direction at cap level"],
    [0.30, "DWTH", "Dirtwall Thickness"],
    [0.75, "ALCW", "Abutment Left Cap Width Excluding D/W"],
    [1.20, "ALCD", "Abutment Left Cap Depth"],
    [10.00, "ALFB", "Abt Left Front Batter (1 HOR : 10 VER)"],
    [101.00, "ALFBL", "Abt Left Front Batter RL"],
    [100.75, "ALFBR", "Abt RIGHT Front Batter RL"],
    [10.00, "ALTB", "Abt Left Toe Batter (1 HOR : 5 VER)"],
    [101.00, "ALTBL", "Abt Left Toe Batter Level Footing Top"],
    [100.75, "ALTBR", "Abt RIGHT Toe Batter Level Footing Top"],
    [1.50, "ALFO", "Abutment Left Front Offset To Footing"],
    [1.00, "ALFD", "Abt Left Footing Depth"],
    [3.00, "ALBB", "Abt Left Back Batter"],
    [101.00, "ALBBL", "Abt Left Back Batter RL"],
    [100.75, "ALBBR", "Abt RIGHT Back Batter RL"],
    [3.50, "LASLAB", "Length of approach slab"],
    [12.00, "APWTH", "Width of approach slab"],
    [0.38, "APTHK", "Thickness of approach slab"],
    [0.08, "WCTH", "Thickness of wearing course"],
]

variants = [
    {"NSPAN": 1, "SPAN1": 20.0, "LBRIDGE": 20.0, "RTL": 110.8},
    {"NSPAN": 2, "SPAN1": 22.5, "LBRIDGE": 45.0, "SKEW": 10.0},
    {"NSPAN": 3, "SPAN1": 30.0, "LBRIDGE": 90.0, "SKEW": 15.0},
    {"NSPAN": 4, "SPAN1": 25.0, "LBRIDGE": 100.0, "TOPRL": 112.0},
    {"NSPAN": 5, "SPAN1": 24.0, "LBRIDGE": 120.0, "SOFL": 108.5},
    {"NSPAN": 3, "SPAN1": 40.0, "LBRIDGE": 120.0, "SKEW": 30.0},
    {"NSPAN": 2, "SPAN1": 35.0, "LBRIDGE": 70.0, "CCBR": 12.5},
    {"NSPAN": 6, "SPAN1": 20.0, "LBRIDGE": 120.0, "KERBW": 0.30},
    {"NSPAN": 3, "SPAN1": 18.0, "LBRIDGE": 54.0, "DATUM": 99.5},
    {"NSPAN": 4, "SPAN1": 27.5, "LBRIDGE": 110.0, "SKEW": 5.0},
]

for i, overrides in enumerate(variants, start=1):
    rows = [r[:] for r in base_rows]  # copy
    # apply overrides by matching Variable column
    for j, r in enumerate(rows):
        var = r[1]
        if var in overrides:
            rows[j][0] = overrides[var]
    df = pd.DataFrame(rows, columns=["Value","Variable","Description"])
    out = OUT_DIR / f"SweetWilledDocument-{i:02d}.xlsx"
    df.to_excel(out, index=False, header=False)
    print(f"Created {out}")

print(f"All SweetWilledDocument files written to: {OUT_DIR}")
