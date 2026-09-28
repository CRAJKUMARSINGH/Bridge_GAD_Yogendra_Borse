# tasks.md — GAD Professional Layout: Implementation Queue

Natural language: English.
Spec file: `spec.md` in the same folder.
Dependency order: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 (serially; each builds on previous).

---

## Task 1: BridgeGADGenerator — Plan Anchor Derivation + CAPT Alignment

**Parent ACs:** AC1, AC2, AC10, AC11, AC15.
**Affected file:** `src/bridge_gad/bridge_generator.py`.
**Status:** pending.
**Priority:** high.

### Scope

- Add a class-level layout spacing dict: `LAYOUT_SPACING = {"plan_gap_label_multiplier": 4.0, "section_gap_label_multiplier": 3.0, "dim_reposition_fallback_gap": 3.0}`. (NFR4)
- Add new private method `_compute_plan_anchor_yc() -> float` before the draw calls. It implements the 5-step algorithm from FR1: min(bottom elevation RL), get CAPT, compute gap = 1.5*scale1*multiplier, compute yc via alignment rule y_top = vpos(CAPT) − gap, safety fallback to below-content if overlap.
- Replace ALL literal `yc = self.datum - 30.0` in:
  - `draw_abutment_footing_plan` (L616).
  - `draw_pier_foundation_plan` (L661).
  - `draw_abutment_foundation_plans` (L728).
  with `yc = getattr(self, "_plan_yc", self.datum - 30.0)` defensive fallback (in case some legacy external caller invokes draw functions without running generate_complete_drawing).
- In `generate_complete_drawing`, call `self._plan_yc = self._compute_plan_anchor_yc()` **between** `self.draw_abutments()` and `self.draw_plan_view()`. Also expose attributes `self._plan_capt_drawing_y`, `self._plan_gap_drawing_units`, `self._plan_max_footing_half_height_drawing` on self for testability (NFR2).
- In `add_dimensions_and_labels` (L817): add 10-row overlap guard. Compute `plan_region_bottom_drawing_y = self._plan_yc - max_futlsq_half - extra_margin`. For each span dim `y_dim = self.vpos(RTL) + 200`; if y_dim > plan_region_bottom_drawing_y, reposition above RTL (subtract a gap instead of adding).

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T1-TR1 | rule | Grep for `datum\s*[-–]\s*30\.?0?` in plan-view functions returns 0 matches (AC1). | IDE grep on bridge_generator.py after edit. |
| T1-TR2 | rule | After `generate_complete_drawing(template_girder_4x18m.xlsx, out)`, check: `out.parent.joinpath(out.stem + "_side_elevation.dxf").exists() == True` AND `gen._plan_yc + gen._plan_max_footing_half_height_drawing == approx(gen.vpos(gen.variables["CAPT"]) - gen._plan_gap_drawing_units, abs=0.5)`. (AC2) | py_compile + pytest + approx. |
| T1-TR3 | rubric 0-2 | Visual spot-check: open generated DXF in ezdxf viewer or convert→PNG, measure gap % between lowest-elevation-content bottom and plan-top. ≤10% score 2, ≤20% score 1, else 0. Threshold ≥ 1. (AC10) | Screenshot + measured ratio. |
| T1-TR4 | rubric 0-2 | Plan-top horizontal guide-line vs CAPT line visually aligned (± label gap). 2=immediate, 1=with ruler, 0=no align. Threshold ≥ 1. (AC11) | Screenshot side-by-side guides. |
| T1-TR5 | rule | No orphan unused locals named `yc` / `side_x_offset` in changed functions. (AC15) | `ruff --select=F841` or manual source audit. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T1-TR1 | — | | |
| T1-TR2 | — | | |
| T1-TR3 | — | | Score: __/2 |
| T1-TR4 | — | | Score: __/2 |
| T1-TR5 | — | | |

---

## Task 2: BridgeGADGenerator — Side Elevation Companion Sheet

**Parent ACs:** AC3, AC4, AC5, AC6, AC7, AC12.
**Affected files:** `src/bridge_gad/bridge_generator.py`.
**Status:** pending.
**Priority:** high.
**Depends on:** Task 1 complete (shares class-level LAYOUT_SPACING dict).

### Scope

- Refactor styles setup: extract PMB100 dimstyle + Arial text style creation from `setup_styles(self)` into a NEW static/class helper `_apply_dim_and_text_styles(doc, scale1, scale2, vvs)` so companion doc can get identical settings WITHOUT calling `self.setup_document` (which overwrites `self.doc`). Keep `setup_styles` calling this helper for the main doc (backwards compat).
- NEW method `generate_side_elevation_sheet(companion_path: Path) -> bool`:
  - Creates its own `doc = ezdxf.new(self.acad_version, setup=True)`, `msp = doc.modelspace()`.
  - Calls `_apply_dim_and_text_styles(doc, self.scale1, self.scale2, self.vvs)`.
  - Draws **A3 landscape border** (420 × 297 mm — double scale vs A4). Add helper `_draw_a3_border(msp, title_str, sheet_num, total_sheets, drawing_name)` — border + inner margin box + title block.
  - Title block contains: "SIDE ELEVATION / TYPICAL CROSS SECTIONS", drawing name = excel_file stem, "Sheet 2 of 2".
  - Computes centered page layout: deck section at page top-half (x=center, y≈top 2/3 page), pier section at page bottom-half (x=center, y≈bottom 1/3), separated by `LAYOUT_SPACING["section_gap_label_multiplier"] * max_label_height`.
  - NEW private method `_draw_side_elevation_onto(msp, page_rect: Tuple[float,float,float,float]) -> bounds`: draws deck cross-section AND pier cross-section at **SECTION_SCALE_FULL = 1.0** (no 0.5x). Adds section markers (A-A, B-B) with directional ARROW stubs (ezdxf add_arrow if available; else LWPOLYLINE 3-pt arrow → closed polyline shape; check ezdxf version before call).
  - Adds HATCH STUB layers: `_HATCH_CONCRETE`, `_HATCH_SOIL`, `_HATCH_AC` (layers created with color 8/gray for concrete, color 2/yel for soil, color 3/grn for AC; closed LWPOLYLINE outlines placed on matching layers at section polygon positions; no `HATCH` entity yet — FR5.3).
  - Saves doc → companion_path. Returns True only if save succeeds.
- DEPRECATE old `draw_side_elevation()`: add docstring `"@deprecated since 2026-09-28. Use generate_side_elevation_sheet() for separate companion sheet. Legacy call draws onto main doc's modelspace at 0.5x section scale for backwards compat only."` Keep body intact; NO deletion.
- Modify `generate_complete_drawing()` (L1350):
  - REMOVE line `self.draw_side_elevation()` from the main drawing sequence (old L1373).
  - ADD in its place: a `draw_main_sheet_callouts()` helper that writes TWO "SEE SHEET 2" directional callout arrows on main sheet: one callout in middle elevation pointing downward at mid-span A-A cutting plane, one at a pier location pointing leftward at B-B cutting plane. Text "SEE SHEET 2" — 1.5*scale1 height.
  - AFTER `self.doc.saveas(output_file)` succeeds: compute companion_path, call `ok_side = self.generate_side_elevation_sheet(companion_path)`. Log both. Return True only if both saves succeed.
- Module-level `generate_bridge_gad()` function (L1391): return type still `Path` (main output). Add: `companion = output_file.with_name(f"{output_file.stem}_side_elevation{output_file.suffix}")`; if companion.exists(), log it; no change to return signature. (NFR1)

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T2-TR1 | rule | Companion file `*_side_elevation.dxf` exists next to main out and parses via `ezdxf.readfile()` (no recover). (AC4) | pytest path.exists + readfile no-exception. |
| T2-TR2 | rule | Companion dimstyle PMB100 dimtxt == main doc PMB100 dimtxt AND Arial style present in both. (AC5) | ezdxf style/dimstyle dict compare. |
| T2-TR3 | rule | Text search in companion: contains "SIDE ELEVATION" case-insensitive substring AND "Sheet 2 of 2". (AC6) | `[e.dxf.text for e in msp.query("TEXT") + msp.query("MTEXT")]` substring check. |
| T2-TR4 | rule | In `_draw_side_elevation_onto` body: `grep "section_scale\s*="` → 0 matches or only `section_scale=1.0`; literal `0.5` NOT present in that function body. (AC7) | IDE grep. |
| T2-TR5 | rule | Main DXF contains "SEE SHEET 2" callout text; standalone 50%-scale A-A section text WITHOUT callout companion = FAIL (must have callout). (AC3) | ezdxf TEXT search. |
| T2-TR6 | rule | Existing 5 tests in test_ultimate_app.py pass untouched. (AC12) | `pytest test_ultimate_app.py -v` 5/5 green. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T2-TR1 | — | | |
| T2-TR2 | — | | |
| T2-TR3 | — | | |
| T2-TR4 | — | | |
| T2-TR5 | — | | |
| T2-TR6 | — | | 5/5 green |

---

## Task 3: Bridge Canvas Features — ZIP + PDF Bundler Hookup

**Parent ACs:** AC8, AC9.
**Affected files:** `src/bridge_gad/bridge_canvas_features.py`, `src/bridge_gad/generate_all_drawings.py` (if batch mode uses similar loop, add companion collect there too).
**Status:** pending.
**Priority:** high.
**Depends on:** Task 2 complete (companion file naming pattern now defined).

### Scope

- New pure helper function `collect_side_elevation_companion(primary_dxf: Path) -> Path | None` near top of `bridge_canvas_features.py` — pure, no globals. Returns sibling `*_side_elevation.dxf` Path if it exists, else None. (NFR2)
- In `make_phase_two_package_zip` inner loop: after writing the primary DXF, call `collect_side_elevation_companion`. If found: (a) add it to ZIP at the same archive-path prefix as main, (b) call `convert_dxf_to_pdf` for it → `side_pdf_path`, (c) add side PDF to the ZIP, (d) append new entry `{"sheet_code": "GAD-SIDE", "title": "Side Elevation & Typical Cross Sections", ...}` to the `manifest["sheets"]` list. Also append row to CSV sheet index + sheet_rows for XLSX so all three manifest formats list the companion.
- Same logic in `batch_results_to_zip` — same 4 additions whenever primary DXF exists with a side companion.
- In `generate_all_drawings.py` batch mode (if it has its own ZIP/PDF loop), mirror the logic so batch output ZIPs also contain side companions (search for pattern `convert_dxf_to_pdf(` calls).
- Ensure `make_template_excel` sheet_rows count for `include_phase_three=True` is still consistent (11 rows from the C1 fix row). Adding GAD-SIDE row doesn't change template XLSX sheet count; template XLSX is for templates/schedules not per-drawing outputs.

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T3-TR1 | rule | `make_phase_two_package_zip(...)` with `include_phase_three=False` → unzip, count files: `*_side_elevation.dxf` exists AND `*_side_elevation.pdf` exists. (AC8) | pytest zipfile namelist check + open file exists. |
| T3-TR2 | rule | Manifest JSON `sheets[]` contains entry with `sheet_code == "GAD-SIDE"`. (AC9) | json.loads find in manifest. |
| T3-TR3 | rule | CSV sheet index contains a row for GAD-SIDE after processing. | csv.reader count rows / check cell. |
| T3-TR4 | rule | `collect_side_elevation_companion` returns Path when sibling exists, None otherwise (unit test with temp files). | Pure function unit test. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T3-TR1 | — | | |
| T3-TR2 | — | | |
| T3-TR3 | — | | |
| T3-TR4 | — | | |

---

## Task 4: Streamlit Tab 1 + FastAPI Companion Download Links

**Parent ACs:** AC12 (no regressions).
**Affected files:** `streamlit_app_ultimate.py`, `src/bridge_gad/api.py`.
**Status:** pending.
**Priority:** medium.
**Depends on:** Task 2 complete.

### Scope

- **Streamlit Tab 1** (Generate Drawing button): after generation succeeds and `main_dxf` Path is known, compute `side = collect_side_elevation_companion(main_dxf)`. If side exists:
  - Layout 3 download buttons in 3 columns: (col1) "Download Main GAD DXF" → reads main_dxf bytes, (col2) "Download Side Elevation DXF" → reads side_dxf bytes, (col3) "Download GAD + Side (ZIP)" → writes both DXFs + main+side PDFs into a temporary ZIP (use `zipfile` standard library, tempfile).
  - If side does not exist (old format or generation failed), show only the single original main-DXF download button as today (graceful fallback).
- **FastAPI `api.py`**: inspect existing POST generate endpoint (if one exists and returns download URLs). If so: add `companion_side_elevation_path` key + a new URL route `GET /download/{filename}/side` that serves the side companion bytes (use FileResponse). If no existing generate endpoint yet: skip this sub-step (document in evidence as "no endpoint to hook; covered via Streamlit surface"). Add test if endpoint exists.

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T4-TR1 | rule | After clicking Tab 1 Generate: if side companion exists page shows 3 download buttons; else 1 (graceful fallback UI behavior). | Streamlit `st_app_test` / manual UI screenshot OR code review showing the conditional 3-col layout exists. |
| T4-TR2 | rule | No runtime py_compile / diagnostics errors on streamlit_app_ultimate.py and api.py after edits. | py_compile + diagnostics. |
| T4-TR3 | rule | Existing 5/5 tests still pass (no regression on unrelated tabs). AC12 re-check. | pytest 5/5. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T4-TR1 | — | | Screenshot or code audit. |
| T4-TR2 | — | | |
| T4-TR3 | — | | 5/5 green. |

---

## Task 5: Test Suite — New Regression Test + Diagnostics

**Parent ACs:** AC13, AC14, AC12 (re-verify).
**Affected files:** `test_ultimate_app.py`.
**Status:** pending.
**Priority:** high.
**Depends on:** Tasks 1–4 code changes applied so new test can actually run against them.

### Scope

- NEW function `test_professional_layout_plan_alignment()` in `test_ultimate_app.py` (placed after existing `test_phase_three_package_zip`, before module-end). Body covers:
  - Uses `inputs/sample_input.xlsx` fixture or a girder template.
  - Constructs `BridgeGADGenerator()`; calls `generate_complete_drawing(xlsx, tmp_out)`.
  - **(a) AC1 source parse:** reads `bridge_generator.py` source text → regex `r"yc\s*=\s*self\.datum\s*[-–]\s*30\.?0?"` → expects 0 matches in lines belonging to plan functions. (AC1)
  - **(b) AC2 math:** asserts `abs( (gen._plan_yc + gen._plan_max_footing_half_height_drawing) - (gen.vpos(gen.variables["CAPT"]) - gen._plan_gap_drawing_units) ) <= 0.5`.
  - **(c) AC4 companion exists + parses:** side path resolved; `ezdxf.readfile(side_path)` raises no exception.
  - **(d) Minimal T2 assertions:** companion text list contains "SIDE ELEVATION" (case-insensitive) AND "Sheet 2 of 2".
  - Cleanup: remove both DXF outputs from tmp dir after assertions.
- RE-RUN full existing 5/5 green suite to re-confirm AC12.
- RE-RUN `GetDiagnostics` on the changed file set.

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T5-TR1 | rule | New test `test_professional_layout_plan_alignment` passes under pytest. (AC13) | pytest single-test PASS. |
| T5-TR2 | rule | Overall 6/6 green (5 original + 1 new) under pytest. AC12 preserved. | pytest -v run output. |
| T5-TR3 | rule | GetDiagnostics 0 files, 0 errors, 0 warnings on bridge_generator.py, bridge_canvas_features.py, streamlit_app_ultimate.py, test_ultimate_app.py. (AC14) | IDE diagnostics. |
| T5-TR4 | rule | `py_compile` on all changed Python source files returns exit 0. | PowerShell `py_compile` exit code. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T5-TR1 | — | | PASS / FAIL |
| T5-TR2 | — | | __/6 green |
| T5-TR3 | — | | |
| T5-TR4 | — | | |

---

## Task 6: Logging Check + Performance Baseline

**Parent ACs:** NFR5 (logging), NFR3 (perf).
**Affected files:** `src/bridge_gad/bridge_generator.py` (adding logs), CREAT.MD (append §17 session summary block post-implementation).
**Status:** pending.
**Priority:** low.
**Depends on:** Tasks 1–5 green.

### Scope

- Add logger.info entries as specified by NFR5:
  - `_compute_plan_anchor_yc` exit: log `"Plan anchor yc=%.2f (rule=%s, gap=%.2f, capt_y=%.2f)"` with rule in {"capt-aligned", "below-elevation-fallback"}.
  - `generate_side_elevation_sheet` save success: log `"Companion sheet saved: %s"` with path.
  - `add_dimensions_and_labels` reposition trigger: log `"Dimension overlap guard: moved %d span dims above RTL (plan region at %.2f)"`.
- PERFORMANCE check (NFR3): run `generate_complete_drawing` 3× on `inputs/template_girder_4x18m.xlsx` with fresh generator each time; compute mean pre-change vs post-change. (If pre-change baseline not available: measure post-only and report absolute mean; check ≤ 2.0 s for the whole operation.)
- Do NOT append CREAT.MD in this task (handled during milestone commit + session close per user workflow rule).

### Test Requirements (TRs)

| ID | Type | Detail | Evidence source |
|----|------|--------|-----------------|
| T6-TR1 | rule | logger.info plan-anchor line appears in `logging.getLogger(__name__).handlers` output after generate run (capture via `pytest caplog` or manual). (NFR5) | pytest caplog contains message. |
| T6-TR2 | rule | Companion save success log entry present. | caplog contains message. |
| T6-TR3 | rubric 0-2 | Mean wall-time post-change / ≤ baseline threshold. ≤ 1.1× score 2, ≤ 1.3× score 1, > 1.3× score 0. Threshold ≥ 1. (NFR3) | 3-run mean with notes. |

### Completion Evidence

| TR | Status | Result | Notes |
|----|--------|--------|-------|
| T6-TR1 | — | | |
| T6-TR2 | — | | |
| T6-TR3 | — | | Score: __/2 |

---

## AC → Task/TR Coverage Matrix

| AC | Mapped to task/TR |
|----|-------------------|
| AC1 | T1-TR1, T5-TR1a |
| AC2 | T1-TR2, T5-TR1b |
| AC3 | T2-TR5 |
| AC4 | T2-TR1, T5-TR1c |
| AC5 | T2-TR2 |
| AC6 | T2-TR3, T5-TR1d |
| AC7 | T2-TR4 |
| AC8 | T3-TR1 |
| AC9 | T3-TR2 |
| AC10 | T1-TR3 |
| AC11 | T1-TR4 |
| AC12 | T2-TR6, T4-TR3, T5-TR2 |
| AC13 | T5-TR1 |
| AC14 | T5-TR3 |
| AC15 | T1-TR5 |
| NFR1 | T2.DEPRECATE + generate_bridge_gad return type preserved |
| NFR2 | T1.expose-attrs, T3.collect pure function |
| NFR3 | T6-TR3 |
| NFR4 | T1-TR1 (no datum-30), T2-TR4 (no section_scale 0.5) |
| NFR5 | T6-TR1, T6-TR2 |
