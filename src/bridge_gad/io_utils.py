import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import yaml
import json
import logging

logger = logging.getLogger(__name__)


def read_input_excel(path: str) -> pd.DataFrame:
    """Read bridge input parameters from Excel.

    FIX GENSPARK-003: use header=None to match bridge_generator.py convention
    (all rows are data; columns are Value / Variable / Description).
    """
    return pd.read_excel(path, header=None)


def _parse_num(raw: Any) -> Optional[float]:
    """Best-effort numeric parse; returns None for blanks or non-numeric."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        if pd.isna(raw):
            return None
        return float(raw)
    s = str(raw).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_ground_profile_sheet(
    path: str,
    *,
    sheet_name: Any = None,
    min_rows: int = 2,
) -> Optional[List[Tuple[float, float]]]:
    """Read optional Existing-Ground polyline from a secondary worksheet.

    Expected layout (matches ``inputs\\lisp_input.xlsx`` Sheet2 and Civil 3D chainage export):
    Column 0 = Chainage x; Column 1 = Existing Ground RL y.  Both columns in metres or drawing units.

    Header rows that are not numeric pairs are skipped.  Returns None if the sheet
    is missing or contains fewer than ``min_rows`` valid points so the drawing
    pipeline can skip the green Existing-Ground line silently.

    When ``sheet_name`` is None the probe order is:
    1. sheets named "Ground", "EG", "Existing Ground", "Chainage RL";
    2. the 2nd sheet by index (1-based index 2 in Excel = pandas index 1).
    """
    p = Path(path)
    if not p.exists():
        return None

    candidate_sheets: List[Any] = []
    if sheet_name is not None:
        candidate_sheets = [sheet_name]
    else:
        try:
            xl = pd.ExcelFile(p)
            names = xl.sheet_names
            preferred = ["Ground", "EG", "Existing Ground", "Chainage RL"]
            candidate_sheets = [n for n in preferred if n in names]
            if len(names) >= 2:
                candidate_sheets.append(names[1])
        except Exception:
            candidate_sheets = [1]

    last_err: Optional[Exception] = None
    for cand in candidate_sheets:
        try:
            df = pd.read_excel(p, sheet_name=cand, header=None)
        except Exception as exc:  # pragma: no cover - defensive
            last_err = exc
            continue
        if df is None or len(df) < min_rows:
            continue
        pairs: List[Tuple[float, float]] = []
        for _, row in df.iterrows():
            if len(row) < 2:
                continue
            x = _parse_num(row.iloc[0])
            y = _parse_num(row.iloc[1])
            if x is None or y is None:
                continue
            pairs.append((x, y))
        if len(pairs) >= min_rows:
            pairs.sort(key=lambda pt: pt[0])
            logger.info(
                "read_ground_profile_sheet: %d ground points from sheet=%s",
                len(pairs), cand,
            )
            return pairs

    if last_err is not None:
        logger.warning("read_ground_profile_sheet skipped (err=%s)", last_err)
    return None


def read_per_span_footing_sheet(
    path: str,
    *,
    sheet_name: Any = None,
) -> Optional[List[Dict[str, float]]]:
    """Read optional per-span footing table from a third worksheet.

    Matches ``inputs\\lisp_input.xlsx`` Sheet3 columns: SPAN, FUTRL, FUTD, FUTW, FUTL.
    Returns a list of per-pier footing rows (one row per intermediate pier; length = NSPAN-1).
    Returns None when the probe fails so generators fall back to the single-row
    FUTRL / FUTD / FUTW / FUTL defaults from Parameters sheet.
    """
    p = Path(path)
    if not p.exists():
        return None

    candidate_sheets: List[Any] = []
    if sheet_name is not None:
        candidate_sheets = [sheet_name]
    else:
        try:
            xl = pd.ExcelFile(p)
            names = xl.sheet_names
            preferred = ["Footings", "Pier Footings", "SpanFootings", "SPAN"]
            candidate_sheets = [n for n in preferred if n in names]
            if len(names) >= 3:
                candidate_sheets.append(names[2])
        except Exception:
            candidate_sheets = [2]

    cols_wanted = ["SPAN1", "FUTRL", "FUTD", "FUTW", "FUTL"]
    last_err: Optional[Exception] = None
    for cand in candidate_sheets:
        try:
            df = pd.read_excel(p, sheet_name=cand, header=None)
        except Exception as exc:  # pragma: no cover
            last_err = exc
            continue
        if df is None or len(df) < 2:
            continue
        rows: List[Dict[str, float]] = []
        for _, r in df.iterrows():
            vals = [_parse_num(r.iloc[i]) if i < len(r) else None for i in range(5)]
            if any(v is None for v in vals):
                continue
            rows.append({k: v for k, v in zip(cols_wanted, vals)})  # type: ignore[dict-item]
        if rows:
            logger.info(
                "read_per_span_footing_sheet: %d pier footing rows from sheet=%s",
                len(rows), cand,
            )
            return rows

    if last_err is not None:
        logger.warning("read_per_span_footing_sheet skipped (err=%s)", last_err)
    return None


def read_ground_profile_from_variables(variables: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
    """Extract Existing-Ground polyline from ``GROUND_PROFILE_JSON`` variable.

    Escape hatch for dict-only callers (JSON format:
    ``[[ch_0, rl_0], [ch_1, rl_1], ...]``.
    """
    raw = variables.get("GROUND_PROFILE_JSON") or variables.get("ground_profile_json")
    if not raw:
        return None
    try:
        arr = json.loads(raw) if isinstance(raw, str) else raw
    except Exception as exc:
        logger.warning("GROUND_PROFILE_JSON parse failed: %s", exc)
        return None
    if not isinstance(arr, list) or len(arr) < 2:
        return None
    pairs: List[Tuple[float, float]] = []
    for row in arr:
        if not isinstance(row, (list, tuple)) or len(row) < 2:
            continue
        x = _parse_num(row[0])
        y = _parse_num(row[1])
        if x is None or y is None:
            continue
        pairs.append((x, y))
    pairs.sort(key=lambda pt: pt[0])
    return pairs or None


def save_results_to_excel(results: Dict[str, float], output_path: str) -> None:
    """Save computed results to Excel."""
    df = pd.DataFrame([results])
    df.to_excel(output_path, index=False)


def read_config_yaml(path: Path) -> Dict[str, Any]:
    """Read configuration from YAML file.

    Args:
        path: Path to the YAML configuration file

    Returns:
        Dictionary with configuration parameters
    """
    with open(path, "r") as file:
        return yaml.safe_load(file) or {}


def save_config_yaml(config: Dict[str, Any], path: Path) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        path: Path to save the YAML file
    """
    with open(path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)
