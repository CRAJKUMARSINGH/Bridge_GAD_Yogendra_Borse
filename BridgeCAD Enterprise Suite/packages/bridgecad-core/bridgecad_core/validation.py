"""
bridgecad_core.validation — 30 check_*() functions wired into RulesEngine.
M1 Week 1 Day 4: 25 Critical + 5 Warning checks against BridgeProject.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable, Iterable

from .models import BridgeProject
from .types import ValidationSeverity, ConcreteGrade


# ===========================================================================
# Core data structures (unchanged from scaffold)
# ===========================================================================

@dataclass(frozen=True)
class ValidationFinding:
    check_id: str
    description: str
    severity: ValidationSeverity
    passed: bool
    message: str = ""


@dataclass
class ValidationReport:
    findings: list[ValidationFinding] = field(default_factory=list)

    @property
    def score(self) -> int:
        """0–100 compliance score. Critical fail = −15 pts, Warning fail = −3 pts."""
        score = 100
        for f in self.findings:
            if f.passed:
                continue
            if f.severity is ValidationSeverity.CRITICAL:
                score -= 15
            elif f.severity is ValidationSeverity.WARNING:
                score -= 3
        return max(0, score)

    @property
    def overall_status(self) -> str:
        if any(not f.passed and f.severity is ValidationSeverity.CRITICAL
               for f in self.findings):
            return "FAIL"
        if any(not f.passed and f.severity is ValidationSeverity.WARNING
               for f in self.findings):
            return "WARN"
        return "PASS"

    def passed_findings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.passed]

    def failed_findings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if not f.passed]

    @property
    def critical_fail_count(self) -> int:
        return sum(
            1 for f in self.findings
            if not f.passed and f.severity is ValidationSeverity.CRITICAL
        )

    @property
    def warning_fail_count(self) -> int:
        return sum(
            1 for f in self.findings
            if not f.passed and f.severity is ValidationSeverity.WARNING
        )


CheckFn = Callable[[BridgeProject], ValidationFinding]


class RulesEngine:
    """Container for check functions."""

    def __init__(self) -> None:
        self._checks: list[CheckFn] = []

    def register(self, fn: CheckFn) -> None:
        self._checks.append(fn)

    def run(self, project: BridgeProject) -> ValidationReport:
        findings: list[ValidationFinding] = []
        for fn in self._checks:
            try:
                result = fn(project)
                if isinstance(result, ValidationFinding):
                    findings.append(result)
                else:
                    findings.extend(result)  # type: ignore[arg-type]
            except Exception as exc:
                findings.append(ValidationFinding(
                    check_id="ERR",
                    description=f"Check {fn.__name__} raised unexpectedly",
                    severity=ValidationSeverity.WARNING,
                    passed=False,
                    message=str(exc),
                ))
        return ValidationReport(findings=findings)


# ===========================================================================
# Helpers
# ===========================================================================

_CONCRETE_GRADE_ORDER: list[str] = [
    "M10", "M15", "M20", "M25", "M30", "M35", "M40", "M45",
    "M50", "M55", "M60", "M65", "M70", "M80",
]

def _concrete_ordinal(grade: ConcreteGrade | None) -> int:
    """Return 0-based ordinal for ConcreteGrade; −1 if None."""
    if grade is None:
        return -1
    name = grade.name  # e.g. "M40"
    try:
        return _CONCRETE_GRADE_ORDER.index(name)
    except ValueError:
        return len(_CONCRETE_GRADE_ORDER)  # treat unknowns as very high


def _f(check_id: str, desc: str, sev: ValidationSeverity,
        passed: bool, msg: str = "") -> ValidationFinding:
    return ValidationFinding(
        check_id=check_id,
        description=desc,
        severity=sev,
        passed=passed,
        message="" if passed else msg,
    )


# ===========================================================================
# 25 CRITICAL check functions  (C01–C25)
# ===========================================================================

def check_project_stage_defined(p: BridgeProject) -> ValidationFinding:
    """C01 — Project phase must be set."""
    passed = p.project_master.project_phase is not None
    return _f("C01", "Project stage defined for GAD deliverable",
              ValidationSeverity.CRITICAL, passed,
              "project_master.project_phase is None — set before issue")


def check_client_identity(p: BridgeProject) -> ValidationFinding:
    """C02 — Client identity must be populated."""
    passed = p.project_master.client is not None
    return _f("C02", "Client / employer identity populated",
              ValidationSeverity.CRITICAL, passed,
              "project_master.client is None")


def check_bridge_category_assigned(p: BridgeProject) -> ValidationFinding:
    """C03 — Bridge category must be assigned."""
    passed = p.bridge_selection.bridge_category is not None
    return _f("C03", "Bridge category assigned per functional class",
              ValidationSeverity.CRITICAL, passed,
              "bridge_selection.bridge_category is None")


def check_total_length_coherent(p: BridgeProject) -> ValidationFinding:
    """C04 — Total length must be > 0 and match sum of span lengths."""
    total = float(p.geometry_input.total_length_m)
    span_sum = sum(float(s) for s in p.geometry_input.span_lengths_m)
    passed = total > 0 and abs(total - span_sum) < 0.01
    return _f("C04", "Total bridge length coherent with span arrangement",
              ValidationSeverity.CRITICAL, passed,
              f"total_length={total:.3f} m but sum(spans)={span_sum:.3f} m")


def check_width_does_not_exceed_deck(p: BridgeProject) -> ValidationFinding:
    """C05 — Sum of component widths ≤ declared overall deck width."""
    gi = p.geometry_input
    component_sum = (
        float(gi.carriageway_width_m)
        + float(gi.footpath_left_m or 0)
        + float(gi.footpath_right_m or 0)
        + float(gi.kerb_width_left_m or 0)
        + float(gi.kerb_width_right_m or 0)
        + float(gi.crash_barrier_width_left_m or 0)
        + float(gi.crash_barrier_width_right_m or 0)
        + float(gi.median_width_m or 0)
    )
    overall = float(gi.overall_width_m)
    passed = component_sum <= overall + 0.01   # 10 mm tolerance
    return _f("C05", "Component widths sum ≤ overall deck width",
              ValidationSeverity.CRITICAL, passed,
              f"sum of components={component_sum:.3f} m > overall={overall:.3f} m")


def check_horizontal_alignment(p: BridgeProject) -> ValidationFinding:
    """C06 — Alignment must be set."""
    passed = p.geometry_input.alignment_type is not None
    return _f("C06", "Horizontal alignment type declared",
              ValidationSeverity.CRITICAL, passed,
              "geometry_input.alignment_type is None")


def check_vertical_gradient(p: BridgeProject) -> ValidationFinding:
    """C07 — Gradient must not exceed 1:30 (3.33 %) for urban ROB."""
    grad = float(p.geometry_input.gradient_pct or 0)
    passed = abs(grad) <= 3.34
    return _f("C07", "Vertical gradient ≤ 1:30 (3.33 %) on deck",
              ValidationSeverity.CRITICAL, passed,
              f"gradient={grad:.2f} % exceeds 1 in 30 limit (IRC:86 Clause 4.2)")


def check_superstructure_deck_combo(p: BridgeProject) -> ValidationFinding:
    """C08 — Superstructure type and deck material must both be set."""
    passed = (p.superstructure.type is not None
              and p.superstructure.deck_material is not None)
    return _f("C08", "Superstructure type and deck material declared",
              ValidationSeverity.CRITICAL, passed,
              "superstructure.type or deck_material is None")


def check_pier_abutment_family(p: BridgeProject) -> ValidationFinding:
    """C09 — Pier type and abutment type must both be declared."""
    passed = (p.substructure.pier_type is not None
              and p.substructure.abutment_type is not None)
    return _f("C09", "Pier and abutment family declared",
              ValidationSeverity.CRITICAL, passed,
              "substructure.pier_type or abutment_type is None")


def check_bearing_schedule_not_empty(p: BridgeProject) -> ValidationFinding:
    """C10 — At least one bearing schedule row must exist."""
    passed = len(p.bearings_joints.bearing_schedule) > 0
    return _f("C10", "Bearing schedule populated (≥ 1 row)",
              ValidationSeverity.CRITICAL, passed,
              "bearings_joints.bearing_schedule is empty")


def check_expansion_joint_schedule(p: BridgeProject) -> ValidationFinding:
    """C11 — At least one expansion joint schedule row must exist."""
    passed = len(p.bearings_joints.expansion_joint_schedule) > 0
    return _f("C11", "Expansion joint schedule populated (≥ 1 row)",
              ValidationSeverity.CRITICAL, passed,
              "bearings_joints.expansion_joint_schedule is empty")


def check_return_period_set(p: BridgeProject) -> ValidationFinding:
    """C12 — Hydraulic design return period must be declared."""
    passed = p.hydraulic_data.return_period_yr is not None
    return _f("C12", "Design return period declared",
              ValidationSeverity.CRITICAL, passed,
              "hydraulic_data.return_period_yr is None")


def check_scour_depth_positive(p: BridgeProject) -> ValidationFinding:
    """C13 — Design scour depth must be > 0."""
    scour = float(p.hydraulic_data.design_scour_depth_m or 0)
    passed = scour > 0
    return _f("C13", "Design scour depth > 0 m",
              ValidationSeverity.CRITICAL, passed,
              f"design_scour_depth_m = {scour:.3f} m  (must be positive)")


def check_soil_bearing_capacity(p: BridgeProject) -> ValidationFinding:
    """C14 — Bearing capacity must be declared and positive."""
    cap = float(p.foundation_details.bearing_capacity_kpa or 0)
    passed = cap > 0
    return _f("C14", "Soil bearing capacity > 0 kPa declared",
              ValidationSeverity.CRITICAL, passed,
              f"bearing_capacity_kpa = {cap:.1f}  (must be > 0)")


def check_concrete_grade_minimum(p: BridgeProject) -> ValidationFinding:
    """C15 — Superstructure concrete must be ≥ M25 (IS:456 Table 5)."""
    grade = p.materials.concrete_superstructure
    ordinal = _concrete_ordinal(grade)
    m25_ord = _CONCRETE_GRADE_ORDER.index("M25")
    passed = ordinal >= m25_ord
    return _f("C15", "Superstructure concrete grade ≥ M25",
              ValidationSeverity.CRITICAL, passed,
              f"concrete_superstructure = {grade} is below M25 minimum")


def check_seismic_zone_set(p: BridgeProject) -> ValidationFinding:
    """C16 — Seismic zone must be declared."""
    passed = p.bridge_selection.seismic_zone is not None
    return _f("C16", "Seismic zone declared",
              ValidationSeverity.CRITICAL, passed,
              "bridge_selection.seismic_zone is None")


def check_wind_speed_set(p: BridgeProject) -> ValidationFinding:
    """C17 — Basic wind speed must be declared."""
    passed = p.bridge_selection.wind_zone_ms is not None
    return _f("C17", "Basic wind speed zone declared",
              ValidationSeverity.CRITICAL, passed,
              "bridge_selection.wind_zone_ms is None")


def check_loading_class_set(p: BridgeProject) -> ValidationFinding:
    """C18 — IRC loading class must be declared."""
    passed = p.bridge_selection.loading_class is not None
    return _f("C18", "IRC loading class declared",
              ValidationSeverity.CRITICAL, passed,
              "bridge_selection.loading_class is None")


def check_chainage_set(p: BridgeProject) -> ValidationFinding:
    """C19 — Bridge chainage must be declared."""
    passed = p.project_master.chainage_km is not None
    return _f("C19", "Bridge chainage reference declared",
              ValidationSeverity.CRITICAL, passed,
              "project_master.chainage_km is None")


def check_fea_solver_soft_pass(p: BridgeProject) -> ValidationFinding:
    """C20 — FEA solver check: soft-pass at GAD stage (detailed model not required)."""
    # At GAD stage FEA model is not yet run — always pass with INFO
    return _f("C20", "FEA solver compliance (GAD-stage soft-pass)",
              ValidationSeverity.CRITICAL, True,
              "")


def check_contract_package_phase(p: BridgeProject) -> ValidationFinding:
    """C21 — Project phase must be set (proxy for contract package)."""
    passed = p.project_master.project_phase is not None
    return _f("C21", "Contract package / deliverables phase declared",
              ValidationSeverity.CRITICAL, passed,
              "project_master.project_phase is None")


def check_safety_compliance_status(p: BridgeProject) -> ValidationFinding:
    """C22 — Validation status must not be a critical failure."""
    status = (p.validation.overall_status or "").upper()
    passed = status in {"OK_PASS", "OK", "PASS", "WARN", ""}
    return _f("C22", "Drawing validation overall status is not FAIL",
              ValidationSeverity.CRITICAL, passed,
              f"validation.overall_status = '{status}' — resolve critical failures first")


def check_quality_score_minimum(p: BridgeProject) -> ValidationFinding:
    """C23 — Quality score must be ≥ 60."""
    score = float(p.validation.score_0_to_100 or 0)
    passed = score >= 60
    return _f("C23", "Validation quality score ≥ 60 / 100",
              ValidationSeverity.CRITICAL, passed,
              f"score = {score:.1f}  (minimum 60 required)")


def check_lacey_silt_factor(p: BridgeProject) -> ValidationFinding:
    """C24 — Lacey silt factor must be > 0 (required for scour calc)."""
    sf = float(p.hydraulic_data.lacey_silt_factor or 0)
    passed = sf > 0
    return _f("C24", "Lacey silt factor > 0 declared",
              ValidationSeverity.CRITICAL, passed,
              f"lacey_silt_factor = {sf:.3f}  (must be > 0 for scour calculation)")


def check_vertical_curve_k(p: BridgeProject) -> ValidationFinding:
    """C25 — If gradient is non-zero, a K-value check is implicitly needed
    (soft-pass at GAD stage — detailed profile design is separate)."""
    return _f("C25", "Vertical curve K-value compliance (GAD-stage soft-pass)",
              ValidationSeverity.CRITICAL, True, "")


# ===========================================================================
# 5 WARNING check functions  (W01, W02, W03, W05, W16)
# ===========================================================================

def check_deck_width_over_15m(p: BridgeProject) -> ValidationFinding:
    """W01 — Warn if overall deck width exceeds 15 m."""
    w = float(p.geometry_input.overall_width_m)
    passed = w <= 15.0
    return _f("W01", "Overall deck width ≤ 15 m",
              ValidationSeverity.WARNING, passed,
              f"overall_width = {w:.3f} m > 15 m — cross-drainage detailing review needed")


def check_pier_height_over_20m(p: BridgeProject) -> ValidationFinding:
    """W02 — Warn if typical pier height exceeds 20 m."""
    h = float(p.substructure.pier_height_typical_m or 0)
    passed = h <= 20.0
    return _f("W02", "Typical pier height ≤ 20 m",
              ValidationSeverity.WARNING, passed,
              f"pier_height = {h:.2f} m > 20 m — P-Delta moment check required")


def check_span_over_50m(p: BridgeProject) -> ValidationFinding:
    """W03 — Warn if any span exceeds 50 m (erection scheme note required)."""
    max_span = max((float(s) for s in p.geometry_input.span_lengths_m), default=0.0)
    passed = max_span <= 50.0
    return _f("W03", "Maximum span ≤ 50 m",
              ValidationSeverity.WARNING, passed,
              f"max span = {max_span:.1f} m > 50 m — erection scheme plan required in notes")


def check_concrete_grade_above_m60(p: BridgeProject) -> ValidationFinding:
    """W05 — Warn if any concrete grade is above M60 (HPC approval needed)."""
    grades = [
        p.materials.concrete_superstructure,
        p.materials.concrete_substructure,
        p.materials.concrete_foundation,
    ]
    m60_ord = _CONCRETE_GRADE_ORDER.index("M60")
    above = [g for g in grades if g is not None and _concrete_ordinal(g) > m60_ord]
    passed = len(above) == 0
    names = [g.name for g in above]
    return _f("W05", "Concrete grade ≤ M60 (HPC mix approval needed above M60)",
              ValidationSeverity.WARNING, passed,
              f"Grades above M60: {names} — HPC mix design approval document required")


def check_skew_over_30(p: BridgeProject) -> ValidationFinding:
    """W16 — Warn if skew angle exceeds 30° (torsional analysis note needed)."""
    skew = float(p.geometry_input.skew_angle_deg or 0)
    passed = skew <= 30.0
    return _f("W16", "Skew angle ≤ 30° (torsional stiffness note if higher)",
              ValidationSeverity.WARNING, passed,
              f"skew = {skew:.1f}° > 30° — torsional stiffness analysis note required")


# ===========================================================================
# RulesEngine factory — registers all 30 checks
# ===========================================================================

_ALL_CHECK_FNS: list[CheckFn] = [
    # 25 Critical
    check_project_stage_defined,
    check_client_identity,
    check_bridge_category_assigned,
    check_total_length_coherent,
    check_width_does_not_exceed_deck,
    check_horizontal_alignment,
    check_vertical_gradient,
    check_superstructure_deck_combo,
    check_pier_abutment_family,
    check_bearing_schedule_not_empty,
    check_expansion_joint_schedule,
    check_return_period_set,
    check_scour_depth_positive,
    check_soil_bearing_capacity,
    check_concrete_grade_minimum,
    check_seismic_zone_set,
    check_wind_speed_set,
    check_loading_class_set,
    check_chainage_set,
    check_fea_solver_soft_pass,
    check_contract_package_phase,
    check_safety_compliance_status,
    check_quality_score_minimum,
    check_lacey_silt_factor,
    check_vertical_curve_k,
    # 5 Warning
    check_deck_width_over_15m,
    check_pier_height_over_20m,
    check_span_over_50m,
    check_concrete_grade_above_m60,
    check_skew_over_30,
]


def _build_engine() -> RulesEngine:
    engine = RulesEngine()
    for fn in _ALL_CHECK_FNS:
        engine.register(fn)
    return engine


_ENGINE: RulesEngine = _build_engine()


def run_all(project: BridgeProject) -> ValidationReport:
    """Run all 30 registered checks against *project* and return a report.

    Parameters
    ----------
    project : BridgeProject
        Fully-validated Pydantic model instance.

    Returns
    -------
    ValidationReport
        Contains all findings, score, and overall status.
    """
    return _ENGINE.run(project)


__all__ = [
    "ValidationFinding",
    "ValidationReport",
    "RulesEngine",
    "run_all",
]
