# M1 Week 1 Day 4 — Geometry Modules + Validation Engine Implementation

## Current State (after Day 3)
- `bridgecad_core/models.py` — 427 fields across 14 Pydantic sheet models. **ACCEPTED ★**
- `bridgecad_core/types.py` — 200+ enums, ENUM_REGISTRY ~180+ entries.
- `bridgecad_core/validation.py` — `RulesEngine` + `ValidationReport` scaffolded; `BridgeProject` import still disabled (stub `None`).
- `bridgecad_core/validation_registry.py` — 150 `RuleSpec` entries (25C + 75W + 50I). **No check functions wired yet.**
- `bridgecad_core/geometry/{plan,long_section,cross_section,foundation}.py` — all stubs (single comment line each).
- `bridgecad_core/standards/{irc_05,irc_21,irc_sp55,morth_specs}.py` — all stubs.
- `bridgecad_core/quantities.py` — `extract_quantities()` returns empty BoQ.

---

## Day 4 Goals
1. **Geometry modules** — implement real math in all 4 geometry files (~60–80 pure functions total).
2. **Validation engine wiring** — re-enable `BridgeProject` import in `validation.py`, implement 30 real `check_*()` functions (covering all 25 Critical + 5 Warning checks), register them into `RulesEngine`, expose as `run_all(project)`.
3. **day4_verify.py** — acceptance verifier: geometry smoke tests + validation engine smoke test against the Day 3 SAMPLE fixture.

---

## Files and Modules

| File | Changes |
|---|---|
| `bridgecad_core/geometry/plan.py` | Implement `BridgePlanGeometry` dataclass: skew-rotated deck corners, bearing positions, pier centrelines, abutment rear/front face |
| `bridgecad_core/geometry/long_section.py` | Implement `LongSectionGeometry`: HFL/LWL/scour level markers, soffit level, top-of-deck, ground profile interpolation |
| `bridgecad_core/geometry/cross_section.py` | Implement `CrossSectionGeometry`: parabolic camber, carriageway half-widths, kerb/footpath/parapet offsets |
| `bridgecad_core/geometry/foundation.py` | Implement `PileGroupLayout`: N×M grid, pile cap corners, well circle, open footing stepped outline |
| `bridgecad_core/validation.py` | Re-enable BridgeProject import; implement 30 `check_*()` functions; `run_all(project)` returns `ValidationReport` |
| `day4_verify.py` | New acceptance verifier: geometry + validation smoke checks (8 checks → ★ ACCEPTED ★) |

---

## Step 1 — geometry/plan.py

### `BridgePlanGeometry` dataclass
Inputs from `GeometryInput` + `BridgeSelection` fields on `BridgeProject`.

**Key outputs:**
- `deck_corners: list[tuple[float,float]]` — 4 corners (or more for skew) in drawing space (mm from datum)
- `pier_centrelines: list[tuple[float,float]]` — one per internal pier
- `bearing_positions: list[tuple[float,float]]` — all bearing pads
- `abutment_a1_face: tuple[float,float]` — A1 (chainage-start) abutment front face coordinate
- `abutment_a2_face: tuple[float,float]` — A2 (chainage-end) abutment front face coordinate

**Key formulas:**
```
# Deck corners (skew rotation around bridge centreline)
θ = skew_angle_deg * π/180
half_w = overall_width_m / 2        # computed field from GeometryInput
# A1 left corner: rotate(-θ) of (0, -half_w)
# A1 right corner: rotate(-θ) of (0, +half_w)
# A2 left/right: same rotation of (total_length_m, ±half_w)

# Pier centrelines (simply supported: 1 pier between each span pair)
for i in 1..N-1:
    x_pier = sum(span_lengths[:i])
    pier_positions.append((x_pier, 0.0))

# Bearing offsets from pier centreline (± girder_spacing/2 * girder_count)
# Abutment faces: A1 at x=0, A2 at x=total_length_m
```

---

## Step 2 — geometry/long_section.py

### `LongSectionGeometry` dataclass
Inputs from `HydraulicData` + `GeometryInput` + `FoundationDetails`.

**Key outputs:**
- `hfl_y: float` — drawing y for HFL line
- `lwl_y: float` — drawing y for LWL line
- `scour_level_y: float` — drawing y for design scour
- `soffit_y: float` — drawing y for bottom of deck/girder
- `top_of_deck_y: float` — drawing y for road surface
- `pile_tip_y: float` — drawing y for pile bottom
- `ground_profile_pts: list[tuple[float,float]]` — interpolated ground points along bridge length

**Key formulas:**
```python
# All y values use vscale = 1.0 (real-world metres, caller applies scale)
hfl_y = hfl_m
lwl_y = lwl_m
scour_level_y = scour_level_m
soffit_y = actual_soffit_level_m
top_of_deck_y = road_level_rl_m
pile_tip_y = pile_cutoff_level_m - pile_length_m

# Ground profile: linear interpolation between chainage_start and chainage_end
# using ground_level_rl at ends (project_master fields)
n_pts = 20
for i in range(n_pts+1):
    t = i / n_pts
    ch = chainage_start + t * total_length_m
    rl = ground_start + t * (ground_end - ground_start)
    ground_profile_pts.append((ch, rl))
```

---

## Step 3 — geometry/cross_section.py

### `CrossSectionGeometry` dataclass
Inputs from `GeometryInput` + `Superstructure`.

**Key outputs:**
- `half_width_offsets: list[float]` — x offsets from centreline for each zone boundary
- `zone_labels: list[str]` — label per zone: MEDIAN / CARRIAGEWAY / KERB / FOOTPATH / PARAPET
- `camber_y_at_x: callable` — parabolic function y(x) for camber profile
- `deck_slope_pct: float` — surface drainage slope
- `top_of_wearing_coat_y: float` — peak crown elevation
- `bottom_of_slab_y: float` — soffit of deck slab

**Parabolic camber formula (IRC:112 Clause 6.5):**
```python
# Parabolic: y(x) = camber_mm * (1 - (2x/L)²)  where x is from centreline
# Peak at centreline (x=0), zero at both edges (x=±L/2 = ±carriageway_width/2)
def camber_y_at_x(x_from_cl: float) -> float:
    half_cw = carriageway_width_m / 2
    return camber_mm * (1.0 - (x_from_cl / half_cw) ** 2)
```

**Half-width zones (left → right from CL):**
```
median/2 | CW/2 | kerb | footpath | parapet
```

---

## Step 4 — geometry/foundation.py

### `PileGroupLayout` dataclass

**Key outputs:**
- `pile_positions: list[tuple[float,float]]` — (x, y) of each pile centre
- `pile_cap_corners: list[tuple[float,float]]` — 4 corners of rectangular pile cap
- `well_outer_circle_r: float` — well foundation outer radius
- `open_footing_steps: list[tuple[float,float,float,float]]` — (x, y, w, h) per step

**NxM pile grid:**
```python
# Determine rows × cols from piles_per_pier
# Preferred aspect: approx square
rows = ceil(sqrt(piles_per_pier))
cols = ceil(piles_per_pier / rows)
for r in range(rows):
    for c in range(cols):
        x = (c - (cols-1)/2) * pile_spacing_m
        y = (r - (rows-1)/2) * pile_spacing_m
        pile_positions.append((x, y))
```

---

## Step 5 — validation.py (re-enable + 30 check functions)

### Re-enable BridgeProject import
Remove the `# TMP` comment block, restore:
```python
from .models import BridgeProject
```

### 30 check_*() functions covering all 25 Critical rules + 5 high-priority Warnings

Each check function signature:
```python
def check_XXX(p: BridgeProject) -> ValidationFinding:
    passed = <condition>
    return ValidationFinding(
        check_id="C01", description=..., severity=ValidationSeverity.CRITICAL,
        passed=passed, message="" if passed else "..."
    )
```

**25 Critical checks (map to C01-C25):**

| check fn | Rule | Field(s) checked |
|---|---|---|
| `check_project_stage_defined` | C01 | `project_master.project_phase` is not None |
| `check_client_identity` | C02 | `project_master.client` is not None |
| `check_bridge_category_assigned` | C03 | `bridge_selection.bridge_category` is not None |
| `check_total_length_coherent` | C04 | `total_bridge_length_m > 0` and `== sum(span_lengths)` |
| `check_width_does_not_exceed_deck` | C05 | `carriageway + footpath_L + footpath_R + kerb + crash_barrier <= overall_width_m` |
| `check_horizontal_alignment` | C06 | `AlignmentType.STRAIGHT` or (curve with radius implied) |
| `check_vertical_gradient` | C07 | `abs(gradient_pct) <= 3.33` (1 in 30) |
| `check_superstructure_deck_combo` | C08 | `deck_material` not None in `superstructure` |
| `check_pier_abutment_family` | C09 | `pier_type` and `abutment_type` both set |
| `check_bearing_foundation_compat` | C10 | `bearings_joints.bearing_schedule` not empty |
| `check_expansion_joint_compat` | C11 | `bearings_joints.expansion_joint_schedule` not empty |
| `check_return_period_method` | C12 | `hydraulic_data.return_period_yr` not None |
| `check_scour_design_flood` | C13 | `design_scour_depth_m > 0` |
| `check_soil_bearing_compat` | C14 | `bearing_capacity_kpa > 0` |
| `check_concrete_grade_min` | C15 | `concrete_superstructure` >= M25 (ordinal) |
| `check_seismic_importance` | C16 | `seismic_zone` + `wind_zone_ms` set in `bridge_selection` |
| `check_wind_importance` | C17 | `wind_zone_ms` not None |
| `check_load_combination` | C18 | `loading_class` not None |
| `check_chainage_reference` | C19 | `chainage_km` not None |
| `check_fea_solver_not_required` | C20 | always INFO-pass for D4 (FEA not yet modelled) |
| `check_contract_package` | C21 | `project_master.project_phase` is not None |
| `check_safety_compliance` | C22 | `validation.overall_status` in {OK_PASS, PASS} |
| `check_quality_class` | C23 | `validation.score_0_to_100 >= 60` |
| `check_lacey_k_vs_bank` | C24 | `hydraulic_data.lacey_silt_factor > 0` |
| `check_vertical_curve_k` | C25 | gradient > 0 always has a K-value (soft-pass) |

**5 Warning checks:**

| check fn | Rule | Condition |
|---|---|---|
| `check_deck_width_over_15m` | W01 | `overall_width_m <= 15` (else warn) |
| `check_pier_height_over_20m` | W02 | `pier_height_typical_m <= 20` (else warn) |
| `check_span_over_50m` | W03 | `max(span_lengths) <= 50` (else warn) |
| `check_concrete_grade_above_m60` | W05 | concrete grade ordinal <= M60 |
| `check_skew_over_30` | W16 | `skew_angle_deg <= 30` (else warn) |

### `run_all(project: BridgeProject) -> ValidationReport`
Registers all 30 checks in `RulesEngine`, runs them, returns `ValidationReport`.

---

## Step 6 — day4_verify.py

8 acceptance checks:

| Check | Description | Pass criteria |
|---|---|---|
| D4-C1 | Plan geometry: deck_corners count | == 4 |
| D4-C2 | Plan geometry: pier positions correct | 0 piers for single span (span_count=1) |
| D4-C3 | Long section: soffit > scour level | soffit_y > scour_level_y |
| D4-C4 | Long section: HFL < soffit | hfl_y < soffit_y |
| D4-C5 | Cross section: camber peak at CL | camber_y_at_x(0) == 30 mm |
| D4-C6 | Foundation: pile count == piles_per_pier | len(pile_positions) == 6 |
| D4-C7 | Validation: all 25 Critical pass on SAMPLE fixture | report.critical_fail_count == 0 |
| D4-C8 | Validation: score >= 60 on SAMPLE fixture | report.score >= 60 |

---

## Dependencies and Constraints
- **Pure Python / NumPy only** — no ezdxf, no pandas in geometry modules.
- **All geometry functions are pure** — inputs are Decimal/float Python scalars; outputs are float.
- **Decimal → float conversion** at geometry boundary: `float(model.field)`.
- **No circular imports** — geometry modules import only from `.models`, not from `validation`.
- **validation.py** fixes the `BridgeProject = None` stub with real import.
- **Pydantic v2** — `BridgeProject.model_fields` still works.

---

## Validation

| Check | Command | Pass criteria |
|---|---|---|
| py_compile all 4 geometry files | `python -m py_compile bridgecad_core/geometry/*.py` | Exit 0 |
| py_compile validation.py | `python -m py_compile bridgecad_core/validation.py` | Exit 0 |
| Full acceptance | `python day4_verify.py` | 8/8 PASS → ★ ACCEPTED ★ |

---

## Risks

| Risk | Handling |
|---|---|
| `from .models import BridgeProject` causes circular at validation import time | geometry modules do not import validation; order is types→models→geometry→validation |
| Decimal arithmetic in geometry → type errors | All inputs cast `float(x)` at entry point |
| pile grid count not matching piles_per_pier (rounding) | Grid is padded; check `len(pile_positions) >= piles_per_pier` |
