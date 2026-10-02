# ⚙️ BRIDGECAD ENTERPRISE SUITE — 2 OCTOBER PROGRAM

---

## 🔍 WHAT'S BEEN BUILT (CURRENT STATE AS OF 2 OCT)

### 1. **bridgecad-core — FOUNDATIONAL TYPES & MODELS ✅ STRONG**
- **168 Enum classes** registered in `ENUM_REGISTRY` — Sections 1–10 fully covered
- Mixin classes: `LabeledEnum`, `UnitHaverEnum`, `RangeBoundedEnum`
- **17 Pydantic V2 model classes** in `models.py`: all 14 sheets + aggregate `BridgeProject`
- Full type safety: `Decimal`, range bounds, pattern regex, computed fields (`total_length_m`, `overall_width_m`), `model_validator` for span consistency + IRC span range [1m, 150m]
- **150 validation rules** in `validation_registry.py` — C01–C25 (Critical IRC clauses), W01–W75 (Warnings), I01–I50 (Best Practice)
- **4 geometry modules** with real implementations:
  - `plan.py` — `BridgePlanGeometry` (skew-aware deck corners, pier centrelines, bearing positions)
  - `long_section.py` — `LongSectionGeometry` (HFL/LWL/scour/soffit/top-of-deck RLs, ground profile, freeboard)
  - `cross_section.py` — `CrossSectionGeometry` (parabolic camber `camber_y_at_x()`, half-width zone offsets)
  - `foundation.py` — `PileGroupLayout` (N×M pile grid, pile cap, well circle, open-footing steps)
- `validation.py` `RulesEngine` + `ValidationReport` with 0–100 scoring (Critical −15, Warning −3)

### 2. **bridgecad-draw — 7-SHEET DRAWING ENGINE ✅ GOOD SCAFFOLD**
- `sheet1_plan.py` — Most complete: deck outline, piers, abutments, bearings, centreline, chainage tags, span dims, width dim, north arrow, scale bar, title block, A1 border
- Sheets 2–7 scaffolded: `sheet2_long_section`, `sheet3_cross_section`, `sheet4_foundation`, `sheet5_pier_abutment_details`, `sheet6_bearings_joints`, `sheet7_bill_of_quantities`
- 5 output engines: `dxf_engine`, `pdf_engine`, `svg_engine`, `png_engine`, `three_engine`
- `primitives.py` — line/polyline/rect/circle/text/hatch/dim/north_arrow/scale_bar/chainage_tag
- `layers.py` IRC:SP-55 layer registry, `titleblocks.py` border/title/revision strip, `booklet.py` 7-sheet compiler

### 3. **bridgecad-io — EXCEL ↔ MODEL ROUND TRIP ✅ PARSED**
- `excel_reader.py` — 14-sheet parser, `_sheet_to_dict`, `_coerce`, `_lookup_enum` (name OR value match)
- `excel_template.py` creates styled workbook, `excel_writer.py` round-trip output, `json_adapter.py` + `csv_adapter.py`

### 4. **Sister Packages (Scaffolded ✅)**
- **bridgecad-bill**: CSV/Excel/HTML/PDF formatters, processor, rates_db, statements — BUT `quantities.extract_quantities()` is STUB, returns empty `BillOfQuantities()`
- **bridgecad-qa**: compliance, recommendations, reports, rules_engine
- **bridgecad-export**: booklet/bundler/orchestrator/versioner
- **bridgecad-plugins**: 10 bridge-type plugins (RCC T-Beam, PSC I-Girder, PSC Box, Solid Slab, Voided Slab, Steel Composite, Arch, Box Culvert, Pipe Culvert, Cable-Stayed)
- **bridgecad-ai**: estimator, comparator, optimizer, param_suggester
- **bridgecad-infra**: auth/cache/db/logging/metrics/queue/repositories/storage
- **Apps**: FastAPI gateway, CLI console, Streamlit UI, React+TS Web console

### 5. **28 E2E FIXTURES (REAL BRIDGES FROM SCRIBD)**
Minor/simple, Continuous, PSC girders, T-beam, Culverts, Arch 24m, Well foundation, Viaducts, Major bridges

### 6. **STANDARDS YAML + PDF OUTPUTS**
`standards/irc_05_hydraulic.yaml`, `irc_21_structural.yaml`, `irc_sp55_drawing.yaml`, `morth_rates_2024.yaml`, `state_pwd_multipliers.yaml`

---

## 🚨 THE BLOCKING BUG — 0 / 28 FIXTURES PARSE

All 28 fixtures fail `BridgeProject(**data['project'])` validation. Root cause is fixture enum convention vs enum deserialisation convention mismatch:

Pydantic V2 matches StrEnum by VALUE, not by NAME. All JSON fixtures use `Enum.NAME` as serialised string. ~70% of enums follow `name != value` design (e.g., `LANE_2 = "2_LANE"`, `IRC_112_2020 = "IRC:112-2020"`, `METER = "m"`). Everything fails at the gate.

Additional gaps:
- `quantities.extract_quantities()` empty stub → no Sheet 7 BOQ
- Sheets 2–6 drawing logic minimal scaffold
- Validation registry `applies_to` filter may drop unknown classes silently
- Excel template generator (formulas + dropdowns + formatting + INSTRUCTIONS) not confirmed
- Plugin runner wiring draw_overrides.py into sheet generators

---

## 🎯 PHASE 1 — UNBLOCK THE PIPELINE (2 OCT — HIGHEST PRIORITY)
Goal: Get ALL 28 fixtures parsing clean + Sheet 1 DXF produced for 5 core fixtures

### P1.1 — Add enum name+value matching validator to LabeledEnum mixin
Add `__get_pydantic_core_schema__` classmethod so all 168 enums automatically accept:
- Case-insensitive exact Enum.value match
- Case-insensitive exact Enum.name match
- Normalised underscore↔colon/hyphen

### P1.2 — Parse all 28 fixtures and fix remaining errors
Target: 28/28 pass `BridgeProject(**data['project'])`

### P1.3 — Run pytest tests/test_types.py (371 cases)
Target: 100% pass

### P1.4 — Produce Sheet 1 DXF for simple_12m
Using existing `sheet1_plan.generate` → smoke-test output file size, layers count

### P1.5 — Run RulesEngine on simple_12m and report QA score
Confirm Critical/Warn/Info rules actually fire against real data

---

## 🎯 PHASE 2 — SOLIDIFY CORE LOGIC (Week 1 wrap-up)
Goal: Geometry → 7 Sheets → BOQ all produce real output for simple_12m

6. Implement `extract_quantities()` for RCC T-Beam
7. Sheet 2 Long Section draw
8. Sheet 3 Cross Section draw
9. Sheet 4 Foundation draw
10. Sheet 5 Pier/Abutment elevation draw
11. Sheet 6 Bearings/Joints
12. Sheet 7 BOQ

---

## 🎯 PHASE 3 — EXCEL ROUND-TRIP & UI INTEGRATION
13. Excel template generator from txt-plan spec (14 sheets + formulas + dropdowns + conditional formatting + INSTRUCTIONS)
14. Round-trip test: generate template → fill → excel_reader → equality check vs JSON
15. Export orchestrator: single call → bundle.zip (7 DXF + 7 PDF + booklet + BOQ xlsx + QA report + manifest)
16. Streamlit UI wire-up

---

## 🎯 PHASE 4 — PLUGIN SYSTEM & 10 BRIDGE TYPES
17. Plugin runner applies draw_overrides.py per SuperstructureType
18. Box Culvert plugin
19. Well Foundation plugin
20. PSC Box Girder plugin
21. Skew bridge regression test
22. Arch 24m plugin

---

## 🎯 PHASE 5 — QA, BILL RATES, COMMERCIAL BUNDLE
23. bridgecad_qa.compliance IRC SP-55 checker
24. bridgecad-bill rates_db integration (MORTH + State PWD multipliers)
25. bridgecad-ai.param_suggester default-value inference
26. docker-compose full stack health check
27. 28-fixture regression run final pass
