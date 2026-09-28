# spec.md — Bridge GAD Professional Layout Elevation & Multi-Sheet Polish

Natural language: English.
Spec date: 2026-09-28.
Scope: `bridge_generator.py` (single-sheet GAD generator), `dxf_to_pdf.py`, `multi_sheet_generator.py`, `bridge_canvas_features.py` ZIP wiring, `test_ultimate_app.py` regression coverage.

## 1. Problem

The single-sheet GAD generator in `BridgeGADGenerator.generate_complete_drawing` has three quality problems that hurt professional review-readiness and contradict the user's 99% CAD-clarity mandate:

1. **Rigid vertical plan placement wastes space & breaks elegance.** The plan view and its pier/abutment footing drawings are pinned to the hard-coded constant `yc = self.datum - 30.0` in three independent functions (`draw_abutment_footing_plan` L616, `draw_pier_foundation_plan` L661, `draw_abutment_foundation_plans` L728). This 30-unit gap is independent of actual elevation extents, datum level, drawing scale, or label height — for tall piers it crushes plan into labels; for short piers with low-foundation deep footings it leaves a ~20-30 m blank vertical band.

2. **Plan ↔ Elevation cross-reference is visually weak.** The user explicitly requires: *"Level of pier in elevation and in plan edge of extreme northern plan line"* — the top edge of the plan view (northern boundary of the extreme-most pier footing rectangle, i.e. `y1 = yc + futlsq / 2` in the pier-foundation-plan loop) must visually align with the pier-cap-level RL line (`CAPT`) drawn in the elevation view. The current code draws plan 30 units below datum with no reference to CAPT at all, so the cross-reference is coincidental at best, misleading at worst.

3. **Side elevation is shoe-horned onto the main GAD sheet and needs its own page.** `draw_side_elevation()` L1026 draws the deck cross-section and typical pier cross-section at `side_x_offset = self.hpos(RIGHT) + 40 * scale1` — to the right of the main elevation — and both sections use a `section_scale = 0.5` shrink factor. This creates three visual defects: (a) the main sheet becomes horizontally wide, exceeding A4/A3 printable area; (b) the 0.5x section scale with `hhs/vvs` double-scaling produces blurry 0.85*scale1 labels that don't match the dimension-style text heights set by `PMB100`; (c) the side elevation cannot be plotted separately for submission reviewers who expect a dedicated "SIDE ELEVATION / TYPICAL CROSS-SECTION" sheet. Cross-referencing the Scribd GAD-7-233-5 final PDF shows the industry standard: GAD main sheet has plan + elevation + key dimensions; side/cross-section gets its own numbered sheet with its own border + title block + centered content.

Combined, these three problems produce drawings that are:
- Not submittable to consultant review without manual AutoCAD touch-up (defeats the tool's purpose).
- Not consistent with IRC SP:84 (Code of Practice for Concrete Road Bridges) drawing conventions (plan ↔ pier-cap alignment, separate cross-section sheets, dimension text ≥ 2.5 mm printed height on a scaled drawing).

## 2. Users / Consumers

| Actor | Role | What they do with this change |
|-------|------|-------------------------------|
| Drafter (Bridge GAD operator) | Primary | Generates GAD + companion cross-section DXF/PDF from 1 Excel file → submits to consultant. Expects 1-click, no manual post-processing. |
| Consultant Reviewer | Secondary | Opens 2 DXF/PDF files: Sheet 1 (GAD: Elevation + Plan + RL/Chainage axes + key dims) and Sheet 2 (Side Elevation / Typical Cross-Section). Expects clear captions, no crowded sections, plan ↔ pier-top visual alignment. |
| Streamlit Tab 1 user | Primary | Clicks "Generate Drawing" — expects download links for **both** main + companion in ZIP; not just the single crowded main DXF. |
| FastAPI `/generate` caller | Primary | HTTP API consumer — response must include companion file path + manifest entry so CI pipelines collect both. |
| `test_ultimate_app.py` | Automated gate | Guards regressions; asserts entity counts, layer/text-keywords, companion-sheet existence. |

## 3. Goals

- G1 — Unshackle plan vertical positioning: derive plan anchor from **real elevation content bounds + CAPT level + gap computed from text-height**, not the magic number `30.0`.
- G2 — Correct cross-reference alignment: northern top edge of plan's extreme-most pier footing rectangle shall sit at (or at a small, text-height-derived gap above/below) the same drawing-Y as the pier cap-top RL (`CAPT`) elevation line.
- G3 — Side elevation → dedicated companion sheet: separate DXF document, its own border + title block ("Sheet 2 of 2 — SIDE ELEVATION & TYPICAL CROSS SECTIONS"), 1:1 scale sections matching PMB100 dim-style, centered on A4/A3. Old cramped `side_x_offset` right-of-main placement removed entirely from main sheet.
- G4 — Professional-grade finish alignment to the Scribd GAD-7-233-5 reference: dimension text ≥ 2.5 mm (1:1 DXF world units for A4 print = 2.5), hatching stubs retained for concrete, section markers (A-A, B-B) with directional arrows on main sheet pointing to companion, title block with sheet-of-sheets counter (both sheets share a common drawing title).
- G5 — Full backwards compatibility: existing callers of `generate_complete_drawing()` that only pass `excel_file + output_file` continue to work; they simply get an **additional** companion `.dxf` written next to output (e.g. `output.dxf` → `output_side_elevation.dxf`); no signature change required for basic use.

## 4. Non-Goals (Out of Scope)

These are explicitly **not** touched in this spec (defer to Phase 3 C2/C3/C4 later):
- Full hatching of concrete/soil/AC (hatching is planned C2 work; we add the **hatch-stub layer & region outline** only so a later C2 pass can fill them in without re-computing geometry).
- Full DXF structural regression entity-count suite (C3 work; we add minimal smoke assertions only for the new companion sheet + plan alignment rules).
- A1/A0 zone marks, north-arrow key-plan on GAD sheet, consultant signature/stamp boxes, revision history column (C4 work).
- CLI `cli.py` subparser rewrite (C5 work; we hook API + Streamlit only; CLI stays beam-calc-only).
- PyVista / three.js 3D preview (the dead `living_gad` was already deleted; no 3D here).
- PaperSpace LAYOUT objects inside a **single** DXF: we choose the simpler, better-supported approach of **two separate DXF modelspace documents**, then bundling into one multi-page PDF via the existing `bundle_drawings_to_pdf` in `dxf_to_pdf.py`. Reason: `ezdxf.addons.drawing.Frontend.draw_layout` only renders ModelSpace today (see `dxf_to_pdf.py` L151); Paperspace layout rendering would require a dxf_to_pdf rewrite of much higher complexity. Two-DXF + existing PDF bundler is the idiomatic, testable, low-risk choice.

## 5. Functional Requirements

### FR1 — Plan Anchor Derivation (BridgeGADGenerator)

**Affected functions:** `draw_pier_foundation_plan`, `draw_abutment_footing_plan`, `draw_abutment_foundation_plans`, and a NEW private helper `_compute_plan_anchor_yc() -> float` added before the plan views run.

The `yc` passed into all plan-view callers MUST be computed as follows, with NO literal `datum - 30.0` remaining anywhere:

1. Compute **elevation-content bottom RL**: the lowest RL value actually drawn in elevation. Candidates compared & min taken:
   - `FUTRL - FUTD` (footing bottom, all piers & abutments).
   - `ARTBL` (abutment return toe bottom level).
   - Any RL produced by `draw_level_markings` (current datum through TOPRL step YINCR).
   Call this value `bottom_elevation_rl`.

2. Compute **pier-cap-top RL** = single authoritative value from `CAPT` variable (already used by `draw_piers_elevation` L363+ to cap pier shafts at CAPT).

3. Compute **gap in drawing-units** between elevation-bottom and plan-top. The gap SHALL be derived from the plan-view P# label height: `label_height = 1.5 * self.scale1` (exactly the value used at `draw_pier_foundation_plan` L714), and multiplied by a configurable-but-sane default multiplier `PLAN_VERTICAL_GAP_LABEL_MULTIPLIER = 4.0`. User profile says "free to decide vertical distance from bottom" — this rule frees us from the 30.0 constant AND produces proportional spacing regardless of SCALE1 value (scale=100 vs scale=200 both look balanced).

4. Compute **yc from the cross-reference alignment rule (Goal G2)**:
   - Plan view uses `y_top = yc + FUTLSQ / 2` for each pier footing rectangle (see `draw_pier_foundation_plan` L675).
   - We REQUIRE: the northern-most (max-Y) footing edge of the extreme-most pier (this y_top value) MUST equal the CAPT level's drawing-Y position, **minus** the label-anchor gap.
   - Formally: let `capt_drawing_y = self.vpos(CAPT)`. Then y_top_of_first_pier = `capt_drawing_y - gap_drawing_units`. Since `y_top = yc + max(futlsq / 2 for all piers, abutment abtlen/2)` we have:
     `yc = capt_drawing_y - gap_drawing_units - max_footing_half_height_drawing`
   - Safety guard: if the resulting `yc` would place plan ABOVE the lowest-elevation-content bottom drawing-Y (i.e. overlap risk), fall back to positioning below elevation content with the same `gap_drawing_units` padding (no cross-reference in that pathological case, but no overlap ever).

5. A new private attribute MUST be set during `generate_complete_drawing` **before** any plan-view draw call runs: `self._plan_yc = _compute_plan_anchor_yc()`. All three existing draw functions MUST read from `self._plan_yc` and MUST NOT contain any literal `datum - 30.0`.

### FR2 — Side Elevation → Companion Sheet (BridgeGADGenerator)

**Affected functions:** `generate_complete_drawing`, NEW `generate_side_elevation_sheet(companion_path: Path) -> bool`, existing `draw_side_elevation`, `draw_deck_cross_section`, `draw_pier_cross_section`.

Change contract:

1. Default backwards-compat entry point `generate_complete_drawing(excel_file, output_file) -> bool`:
   - Generates the main GAD DXF exactly as before (except: NO `self.draw_side_elevation()` call on main sheet L1373 — REMOVE that line).
   - Computes companion path: `companion = output_file.with_name(f"{output_file.stem}_side_elevation{output_file.suffix}")`.
   - Calls `self.generate_side_elevation_sheet(companion)` AFTER `self.doc.saveas(output_file)` succeeds.
   - Still returns bool True only if BOTH documents saved.

2. NEW `generate_side_elevation_sheet(companion_path) -> bool` method MUST:
   - Instantiate a FRESH, independent DXF document (`ezdxf.new(self.acad_version, setup=True)` inside the method; reuse `self.variables` (already loaded) — do NOT clone `self.doc`.
   - Call `self.setup_document_styles(doc)` refactor (new helper — pull PMB100 dimstyle + Arial text style out of `setup_styles` into a styles-applier that accepts any `doc` so the companion sheet gets IDENTICAL dim/style config as main).
   - Draw its own A4/A3 border + title block: title = "SIDE ELEVATION / TYPICAL CROSS SECTIONS", sheet counter "Sheet 2 of 2", drawing name matches main sheet name (derived from excel_file stem).
   - Call a NEW `draw_side_elevation_onto(msp, layout_params)` variant that accepts target modelspace + layout params (left/top/dpi/page_size offsets), rather than writing into `self.msp`. Reuse the geometry of `draw_deck_cross_section` + `draw_pier_cross_section`, but:
     - **REMOVE `section_scale = 0.5`** — draw at 1.0 scale so dimension text from PMB100 is proportional to the section rather than 50% too small.
     - Center deck cross-section + pier cross-section vertically on the page with a clear A-A / B-B section marker with directional ARROW heads (use `ezdxf.add_arrow` or polyline arrow stub if ezdxf version lacks native arrow helper; check ezdxf ≥ 1.2 `msp.add_arrow(...)` availability else draw polyline).
     - Section markers on MAIN sheet (at the place where `draw_side_elevation` was previously called) MUST now, instead, draw small A-A / B-B "SEE SHEET 2" directional callout arrows — one at mid-span elevation pointing up, one at a pier location pointing down, so readers know to open the companion.
   - Save companion document to `companion_path`.

3. Existing `draw_side_elevation()` method MUST be marked `@deprecated` docstring and its body changed to delegate to the new variant for any legacy caller that may invoke it directly. No deletion; deprecation-only so we don't break unknown external integrations.

### FR3 — PDF Bundler Multi-Sheet Hookup (bridge_canvas_features.py)

**Affected functions:** `make_phase_two_package_zip`, `batch_results_to_zip`, `make_template_excel` (no change), NEW small helper `collect_side_elevation_companion(primary_dxf_path) -> Path | None`.

1. For every bridge GAD primary DXF written inside `make_phase_two_package_zip` / `batch_results_to_zip`, detect the side-elevation companion next to it (pattern `*_side_elevation.dxf`). If found, add BOTH to the ZIP archive, AND render BOTH to PDF (convert each via existing `convert_dxf_to_pdf`). Result: ZIP contains 4 PDF files per template where companion exists: main DXF, main PDF, side DXF, side PDF (plus XLSX/CSV/manifest of course).

2. Manifest JSON `sheets[]` array MUST include a new sheet entry for each side elevation companion added. `sheet_code = "GAD-SIDE"` (new addition; not in PHASE_THREE_CODE_SET yet — keep separate until C3/C4 naming formalization; document as provisional).

3. Existing behavior for templates that DON'T generate a side companion (if any) is unchanged; no ZIP entry if file doesn't exist.

### FR4 — Streamlit Tab 1 + FastAPI Download Links

**Affected files:** `streamlit_app_ultimate.py` (Tab 1 "Generate Drawing"), `api.py` (POST /generate endpoint if exists — check).

1. When Tab 1's "Generate Drawing" button produces a DXF and the companion `_side_elevation.dxf` exists next to it:
   - Show TWO st.download_button widgets: "Download Main GAD" + "Download Side Elevation & Cross-Sections", plus a combined ZIP download "Download GAD + Side (ZIP)".
2. FastAPI (if generate endpoint exists in api.py): the JSON response body gains a `companion_side_elevation_url` / `companion_side_elevation_path` key.

### FR5 — Professional-Grade Finish Details (BridgeGADGenerator)

Aiming at Scribd GAD-7-233-5 professional-grade reference qualities; achievable without full C2 hatching pass:
1. **No magic numbers for gaps.** All spacing constants between views (elevation ↔ plan gap, section-on-sheet gap between A-A and B-B) SHALL be expressed as label_height × multiplier, and the multiplier SHALL live in a single class-level `LAYOUT_SPACING` dataclass-like dict so a future contributor can tune layout without hunting literals.
2. **Dimension visibility check.** Any `add_linear_dim` calls placed below the new plan area SHALL be repositioned if they'd overlap with plan geometry — we add a small 10-row region guard in `add_dimensions_and_labels` that checks `y_dim` against computed `plan_region_bottom_drawing_y`, and if conflict exists moves dims above RTL line instead.
3. **Hatch stub layers.** Create `_HATCH_CONCRETE`, `_HATCH_SOIL`, `_HATCH_AC` layers in the companion-sheet document at the locations where sections have solid areas, then place `LWPOLYLINE` outlines (closed) on those layers — these are stubs for Phase-3 C2 hatching, but even as outlines they visually differentiate concrete vs backfill on the cross-section. No solid hatching fill applied (non-goal; out of scope).

## 6. Non-Functional Requirements

### NFR1 — Backward Compatibility
- **rule:** Every existing public method signature in `BridgeGADGenerator` is unchanged. New methods are additive; no parameter list renames, no kwarg removals.
- **rule:** `generate_bridge_gad()` module-level function at L1391 returns the SAME single output path as today; it additionally writes the companion and logs its existence but the return type `Path` is preserved (external callers that only unpack the return value still work).

### NFR2 — Testability
- **rule:** All computed values (`_plan_yc`, gap_drawing_units, capt_drawing_y) are exposed as instance attributes (no local-only closures) so tests can read them after `generate_complete_drawing` without monkey-patching.
- **rule:** Side-sheet detection helper `collect_side_elevation_companion(p)` is a pure function (no global state) so it is unit-testable in isolation.

### NFR3 — Performance
- **rubric 0-2:** Total wall-clock runtime for `generate_complete_drawing + side sheet` on template_girder_4x18m.xlsx shall be ≤ 1.3× the baseline measured today (single sheet). 2 = ≤ 1.1×, 1 = ≤ 1.3×, 0 = > 1.3×. Pass threshold ≥ 1.
- Reasonable: we're writing a second small DXF document; 1.3× ceiling is generous given the companion has only 2 sections + border + title.

### NFR4 — Cleanliness
- **rule:** Zero remaining occurrences of the literal regex `datum\s*[-–]\s*30\.?0?` in the plan-view drawing code. Grep on `src/bridge_gad/bridge_generator.py` L610-L760 returns 0 matches.
- **rule:** Zero remaining occurrences of the literal regex `section_scale\s*=\s*0\.5` inside companion-sheet drawing code (main sheet's deprecated draw_side_elevation can keep it since deprecated; NEW code uses 1.0).

### NFR5 — Logging
- **rule:** New `logger.info` entries emit for: plan-anchor computation result (yc value + which rule selected), companion sheet save success/failure, dimension repositioning events if triggered.
- **rule:** No new `logger.error` entries introduced in the happy path; all errors are from existing or true failure modes only.

## 7. Constraints

1. **Environment:** pandas/openpyxl installable only via `--target ./vendor` (WinError 5 Access Denied blocks global pip). Tests must run with `PYTHONPATH=vendor;src` prefixed.
2. **No invented engineering data:** TBC stamps retained for proportions; no new RL/loads/sections invented. We only *reposition existing geometry* with layout math that uses existing parameters.
3. **No Paperspace LAYOUT rewrite of `dxf_to_pdf`:** choose 2-DXF + PDF bundler approach (§4 non-goal rationale).
4. **ezdxf capabilities:** If `msp.add_arrow` is not available in the pinned ezdxf version (check imports), fall back to 3-point LWPOLYLINE arrow stubs.
5. **Streamlit UI scope:** Tab 1 only (main GAD generator) — don't touch Tab 2-10 unless they download ZIPs that include Tab-1 outputs (then just add companion to same ZIP).
6. **No CLI change:** `cli.py` stays beam-calc only; C5 later if needed.

## 8. Dependencies / Assumptions

1. ezdxf ≥ 1.1 (already pinned by project; check requirements.txt for version — if older than 1.1 arrow-support fallback from polyline required).
2. `bundle_drawings_to_pdf` exists in `dxf_to_pdf.py` and accepts Iterable[Path] → single multi-page PDF output (confirmed per grep L332 in previous search).
3. Existing `pmb100` dimstyle correctly sets text height, extension lines, arrow size via `enhanced_lisp_functions.st()` parameters — companion reuses the exact same dimstyle setup (no new constants needed).
4. Scribd GAD-7-233-5.pdf is treated as a qualitative reference for sheet separation & cross-reference patterns. We do not copy any proprietary dimensions or exact drawing contents.
5. The companion-sheet A4/A3 size choice: inherit from main sheet. `draw_a4_border` already exists L831 — companion can call the same function (with title block changes). A4 landscape default; user can override by passing larger `RIGHT/TOPRL` that triggers larger page (future work; not this spec).

## 9. Open Questions

- **OQ1:** Does Streamlit Tab 1 need the side PDF rendered inline in a st.image preview, or just the download button? Spec default: download buttons only (PDF preview uses st.markdown with iframe, unreliable; buttons are simpler & robust). Accepting default unless user overrides.
- **OQ2:** Should the companion-sheet naming be `_side_elevation.dxf` (per FR2.1) or `_sheet2.dxf`? Spec says `_side_elevation.dxf` (self-documenting filenames are better than numbered in a flat outputs dir). Accept default.
- **OQ3:** Should companion sheet be A4 or A3? The existing A4 border function is 297×210 mm which is borderline for 1:1 section with full 11.1 m carriageway deck. Spec default: **A3 landscape** for companion, reuse `LAYOUT_PRESETS["A3_landscape"]` and scale DXF border to 420×297 mm. Accept default.

## 10. Acceptance Criteria

All ACs typed `rule` (binary pass) or `rubric` (evaluative scale + threshold).

| ID | Type | Statement | Pass Condition |
|----|------|-----------|----------------|
| AC1 | rule | No hardcoded `datum - 30.0` in plan-view draw functions | `grep -n "datum\s*-\s*30" src/bridge_gad/bridge_generator.py` returns 0 matches OR any remaining match is in comment/docstring only, not in drawing-Y assignment. |
| AC2 | rule | Plan northern-top edge aligns with CAPT drawing-Y minus label-derived gap | After generate_complete_drawing: `self._plan_yc + max_futlsq_half == approx(generator.vpos(CAPT) - (1.5 * SCALE1 * 4.0))`, tolerance = ±0.5 drawing units (floating point slack). |
| AC3 | rule | Side elevation is NOT on main GAD sheet | After generate_complete_drawing: parse main DXF's modelspace for text containing "SECTION A-A" or "UTILITY DUCT". If present, they shall be accompanied by "SEE SHEET 2" directional callout text; standalone 50%-scale A-A/B-B sections without "SEE SHEET 2" callout = FAIL. |
| AC4 | rule | Companion side-elevation file exists next to main output | `Path(output).with_suffix("").name + "_side_elevation.dxf"` → `file.exists() == True`. File parses cleanly via `ezdxf.readfile()` (no recover.readfile needed). |
| AC5 | rule | Companion document has identical dim + text styles as main | `companion_doc.dimstyles["PMB100"].dxf.dimtxt == main_doc.dimstyles["PMB100"].dxf.dimtxt` AND companion_doc has Arial text style with same font path. |
| AC6 | rule | Companion document has title block + "Sheet 2 of 2" | String search on text entities in companion modelspace finds exactly: "SIDE ELEVATION" (or close: case-insensitive substring) AND "Sheet 2 of 2" string. |
| AC7 | rule | Companion sections drawn at 1:1 section scale (no 0.5 shrink) | In the NEW `draw_side_elevation_onto` function body: `grep "section_scale"` returns 0 matches OR returns only `section_scale = 1.0`. Literal `0.5` in that function body = FAIL. |
| AC8 | rule | ZIP packages include side companion DXF + PDF when present | `make_phase_two_package_zip(template_xlsx, include_phase_three=False)` → extract ZIP; count files named `*_side_elevation.dxf` and `*_side_elevation.pdf` — both present = PASS. |
| AC9 | rule | Manifest sheet list includes side companion | `json.loads(ZIP/manifest.json)["sheets"]` contains at least one entry where `sheet_code == "GAD-SIDE"`. |
| AC10 | rubric (0-3) | Professional visual balance — no wasted vertical space, no crowding | Visually inspect sample generated DXF: 3 = ≤10% blank gap between elevation and plan (percent of total drawing height in region between lowest RL line and top of plan), no overlap of dims over plan, labels evenly spaced. 2 = ≤20% gap. 1 = ≤33% gap. 0 = >33% gap OR overlap. Pass threshold ≥ 2. |
| AC11 | rubric (0-2) | Cross-reference clarity — CAPT ↔ plan-top alignment | Inspect side-by-side: 2 = reviewer can immediately see plan's top row aligns with pier caps without measuring. 1 = can tell with ruler/measurement, 0 = no alignment visible. Pass threshold ≥ 1. |
| AC12 | rule | Backwards compat: existing tests pass untouched | `pytest test_ultimate_app.py -v` — existing 5 tests ALL pass (the 1 PytestReturnNotNoneWarning is documented pre-existing, not introduced). No modifications to old test assertions permitted. |
| AC13 | rule | New regression test exists & passes | New test function in `test_ultimate_app.py` (name: `test_professional_layout_plan_alignment`) that: (a) generates a sample drawing, (b) asserts AC1 (no 30 literal) via source text parse, (c) asserts AC2 (alignment math), (d) asserts AC4 (companion file exists + parses). |
| AC14 | rule | IDE diagnostics clean | `GetDiagnostics` returns 0 files, 0 errors, 0 warnings on the changed files: `bridge_generator.py`, `bridge_canvas_features.py`, `streamlit_app_ultimate.py`, `test_ultimate_app.py`. |
| AC15 | rule | No `datum-30` / `side_x_offset` dead paths | All old dead constants replaced by derived values; no orphaned local `yc = datum-30` variables that no caller reads. Source audit: 0 orphan unused local vars named `yc` or `side_x_offset` in changed functions. |

## 11. Verification Vocabulary Mapping (to task TRs)

Every AC above must have at least one Task-level Test Requirement (TR) mapped 1:1 or N:1 in `tasks.md`, with same rule/rubric type preserved.
