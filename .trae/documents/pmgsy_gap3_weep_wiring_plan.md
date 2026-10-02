# PMGSY GAP-3 EG-Polyline + Weep-Holes Wiring — Implementation Plan

## Repository Research

### Scope (2 bounded items only)
This plan wires **two existing but currently disconnected** helpers into the single-sheet `generate_complete_drawing()` pipeline. **No new parameters, no new ParameterSpec entries, no new template values** — all plumbing uses keys/helpers already added in T0–T5 Option A.

#### Item A — GAP-3: Existing-Ground (EG) green wavy polyline on Sheet01 Elevation
- **Current state (STUB):** `BridgeGADGenerator.draw_cross_section_profile()` at [bridge_generator.py:317-324](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L317-L324) contains only `logger.info(...)` + try/except — draws **nothing**.
- **Readers exist but NEVER called:** `io_utils.read_ground_profile_sheet(excel_path, ...)` at [io_utils.py:37-103](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/io_utils.py#L37-L103) (Sheet2 CH/RL pairs) and `io_utils.read_ground_profile_from_variables(variables)` at [io_utils.py:163-199](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/io_utils.py#L163-L199) (GROUND_PROFILE_JSON escape-hatch). Both return `Optional[List[Tuple[float, float]]]`, `None` on absent/invalid input → silent skip safe.
- **Call order in generate_complete_drawing()** ([bridge_generator.py:1755-1758](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L1755-L1758)): `draw_cross_section_profile()` is invoked **first** (before superstructure / piers / abutments / dims / title). So any EG polyline will draw UNDER the rest — the correct z-order.
- **Coordinate mapping:** `hpos(chainage_m)` → drawing x, `vpos(RL_m)` → drawing y. These helpers are on the generator class at [bridge_generator.py:192-198](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L192-L198) with `self.hhs = self.vvs = 1000.0` scale.
- **Data source priority (OPT-IN):**
  1. `variables["GROUND_PROFILE_JSON"]` (if set → use `read_ground_profile_from_variables`)
  2. Sheet2 "Ground / EG / Existing Ground / Chainage RL" or sheet-index-2 in the same excel file → use `read_ground_profile_sheet(excel_path)`
  3. Neither → return False silently (no EG line drawn, matches pre-existing visual on generic templates)

#### Item B — Weep-hole circles wired to real Section Abutment / Return Wall views
- **Current state:** `BridgeGADGenerator.draw_weep_holes(x_start, y_start, width, height)` exists at [bridge_generator.py:1625-1735](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L1625-L1735) (staggered grid, circles at WEEP_DIAM, label below) but is **never invoked** in any drawing pipeline.
- **Section views on Sheet (single-sheet pipeline):** `draw_side_elevation()` at [bridge_generator.py:1080-1138](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L1080-L1138) draws `draw_deck_cross_section()` (Section A-A, deck+kerbs+kerb heights only) plus `draw_pier_cross_section()` below it. **No enlarged abutment-stem view exists.** No return-wall view exists.
- **WEEP keys already in pmgsy_7x9 template:** WEEP_DIAM=100, WEEP_C_TO_C=1000, WEEP_ROWS=2, WEEP_STAGGER=1.

### Constraints (HARD, inherited from T0–T5)
1. **OPT-IN silent-skip only:** Every new block must return False / early-exit if required params or input data absent. No exception propagation to caller.
2. **No generic-template regression:** simple_12m, continuous_3x12m, girder_4x18m, box_culvert_8m, arch_24m must render byte-for-byte visually identical (they do not set SOIL/WEEP/NOTES/SCHED keys → all blocks skip).
3. **No new ParameterSpecs / template keys:** Only reuse keys added in T2.
4. **99% CAD clarity:** Lines join clean; hatching closed; dims non-overlapping.

## Files and Modules

| File | Expected Change |
|------|-----------------|
| [src/bridge_gad/bridge_generator.py](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py) | (1) Implement `draw_cross_section_profile()` body — load GROUND_PROFILE_JSON / Sheet2 data, call `hpos/vpos`, draw color=3 lwpolyline + "EXISTING GROUND LEVEL" label. (2) Add 2 new OPT-IN helper methods: `draw_enlarged_abutment_section_with_weep(x0, y0)` + `draw_return_wall_section_with_weep(x0, y0)` — each draws a scaled L-shaped stem rectangle and internally calls `self.draw_weep_holes(stem_x, stem_y, stem_w, stem_h)`. (3) In `draw_side_elevation()`, after `draw_pier_cross_section()`, add guarded try/except blocks to place the 2 enlarged section views below the pier section with y-gap and call them. (4) In `generate_complete_drawing()`, store `excel_file` path on `self._excel_path` (or pass directly) so `draw_cross_section_profile()` can call `read_ground_profile_sheet(excel_path)`. (5) Add `from bridge_gad.io_utils import read_ground_profile_sheet, read_ground_profile_from_variables` at top of module if absent. |
| [test_ultimate_app.py](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/test_ultimate_app.py) | **No test assertion changes anticipated** (5 existing tests do not assert section visuals). If DXF smoke sizes grow beyond 5% tolerance, update test_drawing_generation output-size assertion (check if one exists; if not, leave untouched). |

**Not changed:**
- `standards.py`, `bridge_canvas_features.py`, `io_utils.py`, `streamlit_app_ultimate.py`, `september-update.md` — all untouched.

## Implementation Steps (dependency-ordered)

1. **Import hook (bridge_generator.py top):** Add import line for `read_ground_profile_sheet` + `read_ground_profile_from_variables` from `bridge_gad.io_utils`. Wrap in `try/except ImportError` to avoid breaking import-time if modules reload odd (safe).
2. **Excel-path hand-off:** In `generate_complete_drawing()` right after `self.setup_document()` (before read_variables), set `self._excel_path = Path(excel_file)`. This path is then available inside `draw_cross_section_profile()` without changing its signature.
3. **Implement draw_cross_section_profile() body:**
   - Try `read_ground_profile_from_variables(self.variables)` first.
   - If None AND `self._excel_path.exists()` → try `read_ground_profile_sheet(str(self._excel_path))`.
   - If result `None` OR `len(pairs) < 2` → return False silently.
   - Sort pairs by chainage ascending (already done in reader but double-safe).
   - Map each `(ch, rl)` → `(self.hpos(ch), self.vpos(rl))` → draw `add_lwpolyline(points, close=False, dxfattribs={'color': 3})` (green color=3).
   - Add text label `EXISTING GROUND LEVEL` at mid-chainage x, 1.0 m above max-RL y using `color=3` + `height = 0.9 * scale1`.
   - All wrapped in one outer `try/except Exception` → logger.warning + return False so drawing never aborts.
4. **Add 2 OPT-IN enlarged section + weep helpers on BridgeGADGenerator class (before generate_complete_drawing method block):**
   - `draw_enlarged_abutment_section_with_weep(x0, y0) -> bool`:
     - Guard: return False if any WEEP key missing (`WEEP_DIAM/WEEP_C_TO_C/WEEP_ROWS`) OR abutment stem key (ABTW, ABTB, FUTRL, RTL) absent.
     - `section_scale = 0.5` (matches deck/pier cross-section scale factor in existing code at [bridge_generator.py:1161](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L1161)).
     - Stem width = `ABTW or 0.6 * CCBR` → draw L-shaped stem lwpolyline (back-wall + footing toe).
     - Stem height = `RTL - FUTRL - SLBTHE` (from Finished Road Level to footing top, less slab).
     - Label "ENLARGED ABUTMENT — SECTION" above with dimension-style text.
     - Call `self.draw_weep_holes(stem_x_inner, stem_y_bottom, stem_w, stem_h * 0.75)` (weep inside stem middle area, avoiding top/bottom edges).
     - Return True if at least 1 weep drawn, False otherwise.
   - `draw_return_wall_section_with_weep(x0, y0) -> bool`:
     - Same WEEP guard. Similar geometry, narrower stem (typically 0.7 × ABTW). Label "RETURN WALL — SECTION". Calls draw_weep_holes inside its own rectangle.
     - L-shape matching sample PDF return wall.
5. **Wire into draw_side_elevation():**
   - After the existing `draw_pier_cross_section(side_x_offset, pier_y_offset, ...)` call ([bridge_generator.py:1130-1133](file:///e:/Rajkumar/Bridge_GAD_Yogendra_Borse/src/bridge_gad/bridge_generator.py#L1130-L1133)), calculate `next_y = pier_y_offset - 15 * self.scale1` (gap below pier section).
   - try: `self.draw_enlarged_abutment_section_with_weep(side_x_offset, next_y)`, on success decrement next_y further by `(enlarged_height_estimate + 8 * scale1)`.
   - try: `self.draw_return_wall_section_with_weep(side_x_offset, next_y)`.
   - Each wrapped in its own try/except so individual failure does NOT skip the other, AND never aborts draw_side_elevation().
6. **Regression guard:** Ensure every added code block checks key-presence before executing — so when variables for generic simple_12m run, they all short-circuit on lines like `if not (WEEP_DIAM and WEEP_C_TO_C and WEEP_ROWS): return False`.

## Dependencies and Considerations
- **ezdxf lwpolyline pattern** already pervasive in the existing codebase (ANSI31/ANSI37/AR-SAND soil hatches T4 verified) — new polyline code reuses exactly same style.
- **Coordinate scaling:** hpos/vpos use left/datum anchors set in `setup_document()`. These are stable across all templates; no re-reading needed.
- **Sheet2 probe cost:** `read_ground_profile_sheet()` opens the same Excel file with pandas/openpyxl — file is already on disk and small (<50 KB typical). No threading/performance concern. It already has full internal try/except returning None on any openpyxl error.
- **Template-agnostic:** Both features are fully key-presence-gated so generic templates (simple_12m etc.) will see identical output (T6 smoke render comparison will byte-diff output sizes).
- **Section ordering on sheet:** Enlarged sections are placed **below the pier cross section**, not right of it, so they stay within the side-elevation column — no overlap onto plan view which sits on the left half.

## Validation (exact checks after implementation)
1. **Static:** GetDiagnostics → 0 errors. `py_compile src/bridge_gad/bridge_generator.py` → 0.
2. **Pytest baseline:** `python -m pytest test_ultimate_app.py -v` → **5/5 PASSED**.
3. **Smoke render A — PMGSY 7x9 (with weep + soil + GROUND_PROFILE_JSON from template or synthetic 10-point Sheet2 pair list):**
   - Render → DXF size > 130,000 bytes (larger than prior 110,291 due to EG line + 2 enlarged section + weep circles).
   - Load DXF with ezdxf, count entities: `add_lwpolyline` count > 25 (previously ~15), `add_circle` count > 0 (weep circles), `color=3` entity count >= 1 (EG polyline).
4. **Smoke render B — simple_12m (regression):**
   - Render → DXF size within ±2% of baseline 70,618 bytes (proves all OPT-IN guards skip correctly).
5. **Negative case — PMGSY template with WEEP keys deleted:**
   - Render succeeds (no exception), circle count = 0 (weep helper correctly returns False).

## Risks
| Risk | Impact | Handling / Fallback |
|------|--------|---------------------|
| `excel_path` in draw_cross_section_profile is `None` (caller did not set `_excel_path`) | EG line not drawn, no crash | Step 2 sets `self._excel_path` at start of `generate_complete_drawing()` AND draw_cross_section_profile first tries `GROUND_PROFILE_JSON` (works even without path). On `AttributeError` silently continues. |
| Enlarged abutment section overflows page / overlaps plan view column | Minor visual overlap in edge cases | Both views drawn at same x = `side_x_offset` (right column, away from plan on left). Vertical stacking uses `scale1`-aware 15× gap. If PMGSY 7x9 smoke renders without overlap, risk is mitigated; else add page-height check before render (deferred if not observed). |
| `read_ground_profile_sheet` returns unsorted / non-monotonic chainage → weird backtracking polyline | Ugly (not safety) | Reader already sorts by chainage inside. Draw code adds 2nd defensive sort. |
| WEEP_ROWS × cols calculation produces 0 circles (e.g. stem width < WEEP_C_TO_C) | Weep holes silently absent | `draw_weep_holes` already returns count of 0; caller can log count but still succeeds. PMGSY template sets WEEP_DIAM=100 / C_TO_C=1000 against 0.6×7.5 = 4.5 m stem = room for 4 cols × 2 rows = 8 circles minimum. |
| pandas/openpyxl import errors on io_utils inside generator | Existing code also uses pandas. | Wrap io_utils import in try/except inside draw_cross_section_profile. |

---
*This plan covers exactly 2 wiring items (no new keys / no new specs) and requires one approval gate before file modification per TRAE-plan-mode workflow.*
