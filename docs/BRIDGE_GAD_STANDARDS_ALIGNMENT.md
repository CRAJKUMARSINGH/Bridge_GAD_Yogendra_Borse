# Bridge GAD — Standards Alignment Note (2026 first-pass upgrade)

This document summarises which parts of the Bridge GAD generator have been
raised toward a submission-ready standards-oriented workflow, and which items
still need engineer-grade detailing.

The baseline references cited in the generator metadata are:

- IRC 5:2015  — Standard Specifications and Code of Practice for Road Bridges
- IRC 6:2014  — Standard Specifications and Code of Practice for Concrete Bridges
- IRC 21:2000 — Specifications for Materials, Mix Design, Construction and Workmanship for Concrete
- IRC 83:2014 — Road Bridge Bearing Code of Practice
- IRC SP:114  — Manual on Design and Construction of Road Bridge Bearings

These are metadata labels only.  Every numeric recommendation, clearance,
and thickness value still needs to be cross-checked against the latest
publisher revisions and any authority- or owner-specific amendments.

---

## What is now aligned in the generator

### 1. Shared parameter vocabulary (`src/bridge_gad/standards.py`)

Rewritten in this iteration with dataclasses:

- `ParameterSpec` — describes every parameter key with `key/description/unit/category`.
- `OwnerProfile` — four authority presets (`IRC_MORTH`, `NHAI`, `RAILWAY`, `ULB`)
  with `owner/drawing_standard/design_live_load/review_note`.
- `PARAMETER_SPECS` — covers Metadata, Drawing, Geometry, Levels, Roadway,
  Safety, Utilities, Drainage, Bearings, Superstructure, Substructure,
  Foundation, Approach.
- `DEFAULT_METADATA` — submission-style defaults.
- `STANDARD_CHECKLIST` — seven-item GAD checklist (index plan, sheet set,
  deck/kerbs/footpath, edge treatment, bearings/joints/drainage, levels
  tied to datum/load basis, title-block completeness).
- `PHASE_TWO_SHEETS` — seven-row phase 2 sheet schedule (IDX/GAD/TYP/ABT/PIER/BRG/DRN).

Helpers exposed (used by templates, sheets, and generation):

- `get_parameter_spec(key)` / `get_parameter_description(key)`
- `get_owner_profile(key)` — falls back to `IRC_MORTH`
- `build_template_rows(parameters)` — Value/Variable/Description/Unit/Category rows
- `merge_with_metadata(parameters, **overrides)` — parameter enrichment
- `checklist_rows(items)` / `owner_profile_rows(items)` / `phase_two_sheet_rows(items)`

### 2. Standards-aware validation (`validate_bridge_parameters`)

Original IRC/IS checks kept (clearance 5.5 m, L/20 slab, pier 1.0 m,
footing 0.8 m, span 50 m, spans 10, skew ±45°, carriageway 4.25 m).

Updated standards-layer checks now use the following practical bands:

| Check | Threshold | Type |
|-------|-----------|------|
| LANES declaration + per-lane carriageway (1-lane 4.25 m, 2-lane 7.5 m) | per-lane IRC minima | critical |
| Footpath width | ≥ 1.5 m if declared | warning |
| Cross fall / camber | 1.5 – 4.0 % practical range | warning |
| Wearing course thickness | 50 – 120 mm practical range | warning |
| Safety edge treatment (CRASHB → BARRIERH ≥ 1.0 m when enabled) | 1.0 m minimum | warning |
| Deck drainage spout spacing | ≤ 10 m when declared | warning |
| Expansion joint width sanity | 0 – 100 mm | warning |
| Bearing type for multi-span bridges | presence | warning |
| Title block metadata (PROJECT_NAME/DRAWING_NO/REVISION/DRAWN_BY/CHECKED_BY/APPROVED_BY) | presence | warning |

The returned `score` runs 0–100 (20 per critical issue, 5 per warning).

### 3. Enriched template schema and workbook export

All five `BRIDGE_TEMPLATES` now use `merge_with_metadata({...}, DRAWING_NO=..., PROJECT_NAME=...)`,
automatically injecting `DEFAULT_METADATA` plus the authority owner-profile,
phase two sheet totals, and new roadway furniture fields:

- Metadata: `DRAWING_STANDARD`, `DESIGN_LIVE_LOAD`, `ROAD_CLASS`, `REVISION`,
  `DRAWN_BY`, `CHECKED_BY`, `APPROVED_BY`, `SHEET_NO`, `TOTAL_SHEETS`,
  `OWNER_PROFILE`, `DRAWING_NO`, `PROJECT_NAME`.
- Roadway / safety: `LANES`, `FOOTPATHW`, `MEDIANW`, `CROSSFALL`, `WCTH`,
  `CRASHB`, `BARRIERH`, `BARRIERT`.
- Utilities / drainage: `UTILITYD`, `DRAINSP`.
- Bearings / joints: `EXPJT`, `BEARING_TYPE`, `BEARING_W`.

`make_template_excel` now exports **four sheets**:

1. `Parameters` — Value/Variable/Description/Unit/Category via `build_template_rows`.
2. `Checklist` — `STANDARD_CHECKLIST` rows via `checklist_rows`.
3. `OwnerProfiles` — four authority presets via `owner_profile_rows`.
4. `SheetIndex` — the phase two seven-sheet schedule via `phase_two_sheet_rows`.

Additionally, `make_phase_two_package_zip(params)` produces a ZIP archive with:

- `phase2/phase2_parameters.xlsx`
- `phase2/phase2_sheet_index.csv`
- `phase2/phase2_manifest.json` (owner profile, sheet count, standard/live load basis)

### 4. Submission-style title block (`BridgeGADGenerator.add_title_block`)

Six-row boxed title block. Fields are read from the Excel input via the
folder-2 metadata vocabulary:

1. GENERAL ARRANGEMENT DRAWING + Project Name
2. DRG NO / REV / SHEET n/TOTAL (three columns)
3. STANDARD / LIVE LOAD / BEARING (three stacked)
4. DRAWN BY / CHECKED BY / APPROVED BY (three columns)
5. Company / tagline / scale line
6. Address + Email | Mob (bottom)

A new `add_project_name_footer()` method draws a full-width footer with
project name, code, and a separator line above it.

### 5. Enriched typical section (`draw_deck_cross_section`)

Method signature now takes the following explicit keyword arguments so the
caller (`draw_side_elevation`) can override them per-sheet:

```python
draw_deck_cross_section(
    x_offset, y_base, ccbr, kerbw, slbthe, kerbd, rtl,
    footpath_width=0.0,
    barrier_height=0.0,
    utility_duct_width=0.0,
    wearing_course_thickness=0.0,
    crossfall=0.025,
)
```

What is now drawn in the section (in addition to the deck slab and kerbs):

- **Footpaths** (FP) outside the kerb zone on each side when width is set.
- **Carriageway** label with width + lane count (used by the caller in elevation).
- **Wearing course with crown line** — three-point polyline
  `(edge_left_mid, center_crown, edge_right_mid)` sloped by `crossfall`.
- **Crash barrier / parapet** rectangles on each outer edge when
  `barrier_height > 0`.
- **Utility duct** — rectangle beneath the left footpath/kerb zone with
  a "UTILITY DUCT" label when width is set.

Draw-side elevation now positions a typical pier cross-section below the deck.

### 6. Phase two multi-sheet package (`DetailedSheetGenerator`)

`multi_sheet_generator.py` has been updated to deliver a real 7-sheet phase
two package via `generate_phase_two_package(variables, output_path)`:

1. **IDX — Drawing Index and Basis** — sheet schedule plus owner profile /
   drawing standard / live load basis / review note panel.
2. **GAD — General Arrangement Plan and Elevation** (uses existing enlarged plan view).
3. **TYP — Typical Cross Section** (uses existing section view).
4. **ABT — Abutment Details** (enlarged abutment elevation).
5. **PIER — Pier and Footing Details** (enlarged pier elevation).
6. **BRG — Bearing and Expansion Joint Notes** — parameter-driven note set
   with bearing type, seat width, joint gap, final-schedule note.
7. **DRN — Drainage, Safety and Utility Notes** — drainage spacing,
   barrier type+height, utility duct width, routing and coordination notes.

Each sheet carries a standards-aware title block with Drg/Rev/Basis footer,
owner-authorized contact info, and proper A4 landscape borders.

---

## What still needs engineer-grade detailing

The generator now ships **both phases** (standards vocab + phase two package).
The gaps below are the remaining engineer-grade items before a checker can
sign off on the output:

### Sheet-level polish
- [ ] A1 / A0 master border with zone marks, north arrow, key plan.
- [ ] Revision history column (instead of a single REV cell) on the title block.
- [ ] Consultant / checker / approver signature lines with practice stamp boxes.

### Details that still need real CAD drafting
- [ ] Elastomeric / PTFE bearing plan with guide blocks, hold-downs, clearances.
- [ ] Expansion joint schedule + transition slab and joint sealing details.
- [ ] Deck scuppers, down-take routing, and discharge locations in plan.
- [ ] Parapet/barrier section drawn to actual standard type (New Jersey / metal beam / RCC parapet).
- [ ] Anti-glare screen, lighting mast, sign-foundation details.
- [ ] Utility pipe schedule and trench cross-sections.

### Owner-specific details
- [ ] Concession- or authority-specific overrides for NHAI / state PWD / Railway
      still require project-by-project tuning inside `OWNER_PROFILES`.
- [ ] Bill-of-quantity cross references to the item codes in `bill_generator.py`.

### Tests
- [ ] DXF structural tests — assert presence of title-block, typical section
      entity counts, layer names consistency.
- [ ] Standards regression tests with both compliant and non-compliant fixtures
      for every row of `STANDARD_CHECKLIST` and every authority profile.

---

## Smoke run

All checks performed in the sandbox at the time of writing:

```
py_compile (6 Python files)       — 0 diagnostics
pytest-style test_standards_metadata  → PASSED
pytest-style test_template_excel_enriched → PASSED
Smoke generator (simple_12m)          → standards_smoke.dxf produced
```

---

## Best next step (Phase 3)

If continuing the upgrade, the highest-value next items are:

1. Wire the phase two 7-sheet `DetailedSheetGenerator.generate_phase_two_package()`
   into the Streamlit / FastAPI entry points so users can download the package ZIP
   in one click.
2. Add the three remaining details sheets (bearing plan with clearances,
   drainage plan with outlets, barrier cross-sections).
3. Add DXF structural tests so every phase-two sheet can be programmatically
   verified against a reference fixture.
