"""`python -m bridge_gad` — shortcut entrypoints.

Sub-commands:
  all <out_dir> [--pdf-layout A4_landscape]
        Run the full test run with all BRIDGE_TEMPLATES.
  n <out_dir> --n 10 [--base-template continuous_3x12m]
        Generate parameterised variants (1 → infinity).
"""

from __future__ import annotations

import sys

from .generate_all_drawings import _cli


if __name__ == "__main__":
    sys.exit(_cli())
