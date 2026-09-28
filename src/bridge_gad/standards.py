from __future__ import annotations

"""Shared standards metadata for bridge GAD templates and checks.

This module does not claim code compliance by itself. It centralizes the
parameter vocabulary, practical descriptions, and submission checklist items
that the rest of the application can use consistently.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class ParameterSpec:
    """Describes a bridge input parameter used in templates and checks."""

    key: str
    description: str
    unit: str = ""
    category: str = "General"


@dataclass(frozen=True)
class OwnerProfile:
    """High-level owner/profile defaults for title blocks and review notes."""

    key: str
    owner: str
    drawing_standard: str
    design_live_load: str
    review_note: str


PARAMETER_SPECS: Dict[str, ParameterSpec] = {
    "PROJECT_NAME": ParameterSpec("PROJECT_NAME", "Project or bridge name shown on title block", category="Metadata"),
    "PROJECT_CODE": ParameterSpec("PROJECT_CODE", "Drawing or contract reference number", category="Metadata"),
    "DRAWING_NO": ParameterSpec("DRAWING_NO", "Unique drawing number", category="Metadata"),
    "DRAWING_STANDARD": ParameterSpec(
        "DRAWING_STANDARD",
        "Reference design and drawing basis, e.g. IRC/IS/MoRTH/NHAI project criteria",
        category="Metadata",
    ),
    "DESIGN_LIVE_LOAD": ParameterSpec("DESIGN_LIVE_LOAD", "Live load basis adopted for the bridge", category="Metadata"),
    "ROAD_CLASS": ParameterSpec("ROAD_CLASS", "Road category or project class", category="Metadata"),
    "REVISION": ParameterSpec("REVISION", "Drawing revision identifier", category="Metadata"),
    "DRAWN_BY": ParameterSpec("DRAWN_BY", "Prepared by", category="Metadata"),
    "CHECKED_BY": ParameterSpec("CHECKED_BY", "Checked by", category="Metadata"),
    "APPROVED_BY": ParameterSpec("APPROVED_BY", "Approved by", category="Metadata"),
    "SHEET_NO": ParameterSpec("SHEET_NO", "Current sheet number", category="Metadata"),
    "TOTAL_SHEETS": ParameterSpec("TOTAL_SHEETS", "Total number of sheets in the package", category="Metadata"),
    "COMPANY_NAME": ParameterSpec("COMPANY_NAME", "Consultant or organization name", category="Metadata"),
    "COMPANY_FULL": ParameterSpec("COMPANY_FULL", "Secondary organization description", category="Metadata"),
    "ADDRESS": ParameterSpec("ADDRESS", "Office address for title block", category="Metadata"),
    "EMAIL": ParameterSpec("EMAIL", "Contact email for title block", category="Metadata"),
    "MOBILE": ParameterSpec("MOBILE", "Contact phone for title block", category="Metadata"),
    "OWNER_PROFILE": ParameterSpec("OWNER_PROFILE", "Owner or authority profile used for drawing defaults", category="Metadata"),
    "SCALE1": ParameterSpec("SCALE1", "Primary drawing scale denominator", category="Drawing"),
    "SCALE2": ParameterSpec("SCALE2", "Section/detail scale denominator", category="Drawing"),
    "LEFT": ParameterSpec("LEFT", "Starting chainage shown on drawing axis", "m", "Geometry"),
    "RIGHT": ParameterSpec("RIGHT", "Ending chainage shown on drawing axis", "m", "Geometry"),
    "XINCR": ParameterSpec("XINCR", "Chainage grid increment", "m", "Drawing"),
    "YINCR": ParameterSpec("YINCR", "Level grid increment", "m", "Drawing"),
    "DATUM": ParameterSpec("DATUM", "Reference datum level", "m", "Levels"),
    "TOPRL": ParameterSpec("TOPRL", "Top RL used for axis window", "m", "Levels"),
    "RTL": ParameterSpec("RTL", "Road top level / finished deck level", "m", "Levels"),
    "SOFL": ParameterSpec("SOFL", "Soffit level", "m", "Levels"),
    "NSPAN": ParameterSpec("NSPAN", "Number of spans", category="Geometry"),
    "SPAN1": ParameterSpec("SPAN1", "Typical span length", "m", "Geometry"),
    "LBRIDGE": ParameterSpec("LBRIDGE", "Overall bridge length between abutment faces", "m", "Geometry"),
    "SKEW": ParameterSpec("SKEW", "Skew angle", "deg", "Geometry"),
    "NOCH": ParameterSpec("NOCH", "Number of decimal places or chainage display precision", category="Drawing"),
    "LANES": ParameterSpec("LANES", "Number of traffic lanes", category="Roadway"),
    "CCBR": ParameterSpec("CCBR", "Clear carriageway width between kerbs/barriers", "m", "Roadway"),
    "FOOTPATHW": ParameterSpec("FOOTPATHW", "Footpath clear width on each side where provided", "m", "Roadway"),
    "MEDIANW": ParameterSpec("MEDIANW", "Median width if divided carriageway is shown", "m", "Roadway"),
    "KERBW": ParameterSpec("KERBW", "Kerb width", "m", "Roadway"),
    "KERBD": ParameterSpec("KERBD", "Kerb height/depth", "m", "Roadway"),
    "CROSSFALL": ParameterSpec("CROSSFALL", "Cross fall or camber expressed as decimal slope", "ratio", "Roadway"),
    "WCTH": ParameterSpec("WCTH", "Wearing course thickness", "m", "Roadway"),
    "CRASHB": ParameterSpec("CRASHB", "Crash barrier provided flag (1=yes, 0=no)", category="Safety"),
    "BARRIERH": ParameterSpec("BARRIERH", "Barrier or parapet height above deck", "m", "Safety"),
    "BARRIERT": ParameterSpec("BARRIERT", "Barrier type, e.g. RCC crash barrier / metal beam", category="Safety"),
    "UTILITYD": ParameterSpec("UTILITYD", "Utility duct width if reserved in deck section", "m", "Utilities"),
    "DRAINSP": ParameterSpec("DRAINSP", "Typical drainage spout spacing", "m", "Drainage"),
    "EXPJT": ParameterSpec("EXPJT", "Expansion joint movement gap shown in drawing", "m", "Roadway"),
    "BEARING_TYPE": ParameterSpec("BEARING_TYPE", "Bearing system shown in notes/title block", category="Bearings"),
    "BEARING_W": ParameterSpec("BEARING_W", "Indicative bearing seat width", "m", "Bearings"),
    "SLBTHC": ParameterSpec("SLBTHC", "Slab thickness at center", "m", "Superstructure"),
    "SLBTHE": ParameterSpec("SLBTHE", "Effective slab or deck thickness", "m", "Superstructure"),
    "SLBTHT": ParameterSpec("SLBTHT", "Slab thickness at edge", "m", "Superstructure"),
    "ABTL": ParameterSpec("ABTL", "Abutment face reference chainage", "m", "Substructure"),
    "ABTLEN": ParameterSpec("ABTLEN", "Abutment length in plan", "m", "Substructure"),
    "ALCW": ParameterSpec("ALCW", "Left abutment curtain wall width", "m", "Substructure"),
    "ALCD": ParameterSpec("ALCD", "Left abutment curtain wall depth", "m", "Substructure"),
    "ALFD": ParameterSpec("ALFD", "Left abutment foundation depth", "m", "Substructure"),
    "ALFO": ParameterSpec("ALFO", "Left abutment footing offset", "m", "Substructure"),
    "ALFB": ParameterSpec("ALFB", "Left abutment front batter", "deg", "Substructure"),
    "ALTB": ParameterSpec("ALTB", "Left abutment top batter", "deg", "Substructure"),
    "ALBB": ParameterSpec("ALBB", "Left abutment back batter", "deg", "Substructure"),
    "ALFBL": ParameterSpec("ALFBL", "Left abutment front batter level", "m", "Substructure"),
    "ALTBL": ParameterSpec("ALTBL", "Left abutment top batter level", "m", "Substructure"),
    "ALBBL": ParameterSpec("ALBBL", "Left abutment back batter level", "m", "Substructure"),
    "ALFBR": ParameterSpec("ALFBR", "Left abutment front batter return level", "m", "Substructure"),
    "ALTBR": ParameterSpec("ALTBR", "Left abutment top batter return level", "m", "Substructure"),
    "ALBBR": ParameterSpec("ALBBR", "Left abutment back batter return level", "m", "Substructure"),
    "ARFL": ParameterSpec("ARFL", "Right abutment founding level", "m", "Substructure"),
    "ALFL": ParameterSpec("ALFL", "Left abutment founding level", "m", "Substructure"),
    "CAPT": ParameterSpec("CAPT", "Pier cap top level", "m", "Substructure"),
    "CAPB": ParameterSpec("CAPB", "Pier cap bottom level", "m", "Substructure"),
    "CAPW": ParameterSpec("CAPW", "Pier cap width", "m", "Substructure"),
    "PIERTW": ParameterSpec("PIERTW", "Pier top width", "m", "Substructure"),
    "PIERST": ParameterSpec("PIERST", "Pier section length in cross section", "m", "Substructure"),
    "PIERN": ParameterSpec("PIERN", "Number of intermediate piers", category="Substructure"),
    "BATTR": ParameterSpec("BATTR", "Pier batter", "deg", "Substructure"),
    "FUTRL": ParameterSpec("FUTRL", "Founding level / top of footing level", "m", "Foundation"),
    "FUTD": ParameterSpec("FUTD", "Footing depth", "m", "Foundation"),
    "FUTW": ParameterSpec("FUTW", "Footing width", "m", "Foundation"),
    "FUTL": ParameterSpec("FUTL", "Footing length", "m", "Foundation"),
    "DWTH": ParameterSpec("DWTH", "Dirt wall thickness", "m", "Substructure"),
    "LASLAB": ParameterSpec("LASLAB", "Approach slab length", "m", "Approach"),
    "APWTH": ParameterSpec("APWTH", "Approach slab width", "m", "Approach"),
    "APTHK": ParameterSpec("APTHK", "Approach slab thickness", "m", "Approach"),
    # ============================================================
    # PHASE 3 — Detail Sheets parametric vocabulary.
    # Values are *indicative proportions or placeholders only*.
    # Anything not directly derivable from the bridge inputs is
    # explicitly tagged TBC_BY_ENGINEER. Per technical-integrity
    # rule: we NEVER invent engineering data.
    # ============================================================
    # --- Bearings ---
    "BEARING_L": ParameterSpec(
        "BEARING_L",
        "Indicative bearing pad length along span — default 1.2×BEARING_W or TBC_BY_ENGINEER",
        "m", "Bearings",
    ),
    "BEARING_T": ParameterSpec(
        "BEARING_T",
        "Bearing pad / pot thickness (indicative). TBC_BY_ENGINEER from manufacturer data",
        "m", "Bearings",
    ),
    "BEARING_DOWEL_D": ParameterSpec(
        "BEARING_DOWEL_D",
        "Anchor / dowel bar diameter for bearing fixing. TBC_BY_ENGINEER",
        "mm", "Bearings",
    ),
    "BEARING_DOWEL_N": ParameterSpec(
        "BEARING_DOWEL_N",
        "Number of anchor dowels per bearing. TBC_BY_ENGINEER",
        category="Bearings",
    ),
    "BEARING_PAD_TYPE": ParameterSpec(
        "BEARING_PAD_TYPE",
        "Pad detail type: Elastomeric / POT / PQ / Spherical — used on BRG-DET title",
        category="Bearings",
    ),
    # --- Expansion Joints ---
    "EJ_TYPE": ParameterSpec(
        "EJ_TYPE",
        "Expansion joint system: SWSF (strip-seal) / Modular / Pourous / Sealed (note only)",
        category="Bearings",
    ),
    "EJ_SLOT_W": ParameterSpec(
        "EJ_SLOT_W",
        "Indicative slot / throat width for expansion joint detail. Default derived from EXPJT or TBC_BY_ENGINEER",
        "m", "Bearings",
    ),
    "EJ_SEALANT": ParameterSpec(
        "EJ_SEALANT",
        "Joint sealant or strip-seal membrane type. TBC_BY_ENGINEER / owner std",
        category="Bearings",
    ),
    # --- Wing / Return Walls ---
    "WING_W": ParameterSpec(
        "WING_W",
        "Wing wall stem thickness (indicative). TBC_BY_ENGINEER or derived",
        "m", "Substructure",
    ),
    "WING_L": ParameterSpec(
        "WING_L",
        "Wing wall return length measured from abutment face (indicative). TBC_BY_ENGINEER",
        "m", "Substructure",
    ),
    "WING_H": ParameterSpec(
        "WING_H",
        "Wing wall height above founding — default RTL minus footing top level",
        "m", "Substructure",
    ),
    "REBAR_MAIN_D": ParameterSpec(
        "REBAR_MAIN_D",
        "Wing / substructure main bar diameter. TBC_BY_ENGINEER",
        "mm", "Substructure",
    ),
    "REBAR_TIE_D": ParameterSpec(
        "REBAR_TIE_D",
        "Tie / stirrup diameter in wing wall stem. TBC_BY_ENGINEER",
        "mm", "Substructure",
    ),
    "REBAR_SPACING": ParameterSpec(
        "REBAR_SPACING",
        "Typical tie/stirrup spacing c/c. TBC_BY_ENGINEER",
        "mm", "Substructure",
    ),
    # --- Drainage Downtakes / Scuppers ---
    "SCUPPER_W": ParameterSpec(
        "SCUPPER_W",
        "Kerb inlet / scupper opening width. Indicative; TBC_BY_ENGINEER",
        "m", "Drainage",
    ),
    "DOWNPIPE_D": ParameterSpec(
        "DOWNPIPE_D",
        "Downpipe / downtake nominal diameter. TBC_BY_ENGINEER",
        "mm", "Drainage",
    ),
    "OUTLET_TYPE": ParameterSpec(
        "OUTLET_TYPE",
        "Outfall type: splash plate / hopper head / piped — note only",
        category="Drainage",
    ),
}


DEFAULT_METADATA: Dict[str, Any] = {
    "DRAWING_STANDARD": "IRC/MoRTH project criteria",
    "DESIGN_LIVE_LOAD": "To project design basis",
    "ROAD_CLASS": "Road bridge",
    "REVISION": "R0",
    "DRAWN_BY": "Design Cell",
    "CHECKED_BY": "Checker",
    "APPROVED_BY": "Approver",
    "SHEET_NO": "1",
    "TOTAL_SHEETS": "4",
    "COMPANY_NAME": "Bridge GAD Generator",
    "COMPANY_FULL": "Bridge Engineering Drawing Package",
    "OWNER_PROFILE": "IRC_MORTH",
}


STANDARD_CHECKLIST: List[str] = [
    "Index/location plan, north arrow, road alignment and waterway orientation",
    "General arrangement sheet set with plan, elevation, typical cross-section and key details",
    "Deck arrangement includes carriageway, kerbs, footpath/utility reservation where applicable",
    "Protective edge treatment identified as parapet or crash barrier with indicative height/type",
    "Expansion joints, bearings, drainage spouts and approach slabs covered in drawing notes",
    "Levels and chainages are tied to a declared datum and design live load basis",
    "Title block includes drawing number, revision, sheet number, drawn/checked/approved fields",
]


OWNER_PROFILES: Dict[str, OwnerProfile] = {
    "IRC_MORTH": OwnerProfile(
        key="IRC_MORTH",
        owner="IRC / MoRTH",
        drawing_standard="IRC/MoRTH project criteria",
        design_live_load="As per project design basis and governing IRC load case",
        review_note="Use for generic highway bridge submissions following IRC and MoRTH practice.",
    ),
    "NHAI": OwnerProfile(
        key="NHAI",
        owner="NHAI",
        drawing_standard="NHAI concession / MoRTH / IRC submission criteria",
        design_live_load="As per concession agreement and IRC live load basis",
        review_note="Add authority-specific title block and concession notes before issue.",
    ),
    "RAILWAY": OwnerProfile(
        key="RAILWAY",
        owner="Indian Railways / ROB-RUB",
        drawing_standard="Railway bridge submission criteria with IRC interface details",
        design_live_load="As per project basis for road over bridge / under bridge interface",
        review_note="Check railway clearances, approvals, and submission sheet sequence separately.",
    ),
    "ULB": OwnerProfile(
        key="ULB",
        owner="Urban Local Body / PWD",
        drawing_standard="Owner-specific urban bridge / PWD drawing practice",
        design_live_load="As per sanctioned urban road bridge design basis",
        review_note="Adapt title block and notes to the sanctioning authority template before release.",
    ),
}


PHASE_TWO_SHEETS: List[Dict[str, str]] = [
    {"Sheet No": "1", "Code": "IDX", "Title": "Drawing Index and Basis", "Purpose": "Sheet register, standards basis, key notes"},
    {"Sheet No": "2", "Code": "GAD", "Title": "General Arrangement Plan and Elevation", "Purpose": "Overall bridge geometry, spans, levels, chainages"},
    {"Sheet No": "3", "Code": "TYP", "Title": "Typical Cross Section", "Purpose": "Deck section, roadway furniture, utility reservation"},
    {"Sheet No": "4", "Code": "ABT", "Title": "Abutment Details", "Purpose": "Abutment elevation and footing arrangement"},
    {"Sheet No": "5", "Code": "PIER", "Title": "Pier and Footing Details", "Purpose": "Pier elevation and foundation detail"},
    {"Sheet No": "6", "Code": "BRG", "Title": "Bearing and Expansion Joint Notes", "Purpose": "Bearing type, movement joints, sheet notes"},
    {"Sheet No": "7", "Code": "DRN", "Title": "Drainage, Safety and Utility Notes", "Purpose": "Drainage spacing, barriers, utility duct and notes"},
]

PHASE_THREE_APPENDIX: List[Dict[str, str]] = [
    {"Sheet No": "8",  "Code": "BRG-DET", "Title": "Bearing Details — Plan and Section",     "Purpose": "Bearing pad / pot plan, section through seat, dowels, anchor bolts, TBC markers"},
    {"Sheet No": "9",  "Code": "EXPJ-DET","Title": "Expansion Joint Details",                "Purpose": "Strip-seal / modular joint section, filler board, sealant, movement gap"},
    {"Sheet No": "10", "Code": "WING-DET","Title": "Wing and Return Wall Details",           "Purpose": "Wing wall section, stem + base, reinforcement schedule, TBC markers"},
    {"Sheet No": "11", "Code": "DRN-DET", "Title": "Drainage Scupper and Downtake Details",  "Purpose": "Kerb scupper plan/section, downtake routing, downpipe/outlet details"},
]

PHASE_THREE_SHEETS: List[Dict[str, str]] = PHASE_TWO_SHEETS + PHASE_THREE_APPENDIX

PHASE_THREE_CODE_SET = {row["Code"] for row in PHASE_THREE_APPENDIX}


def get_parameter_spec(key: str) -> ParameterSpec:
    """Return metadata for a parameter, with a safe fallback for unknown keys."""

    return PARAMETER_SPECS.get(
        key,
        ParameterSpec(key=key, description=f"Project-specific parameter: {key}", category="Custom"),
    )


def get_parameter_description(key: str) -> str:
    """Return a human-readable description for the parameter."""

    return get_parameter_spec(key).description


def get_owner_profile(key: str | None) -> OwnerProfile:
    """Return a known owner profile, defaulting to IRC/MoRTH."""

    if not key:
        return OWNER_PROFILES["IRC_MORTH"]
    return OWNER_PROFILES.get(str(key).strip().upper(), OWNER_PROFILES["IRC_MORTH"])


def build_template_rows(parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build enriched rows for template Excel export."""

    rows: List[Dict[str, Any]] = []
    for key, value in parameters.items():
        spec = get_parameter_spec(key)
        rows.append(
            {
                "Value": value,
                "Variable": key,
                "Description": spec.description,
                "Unit": spec.unit,
                "Category": spec.category,
            }
        )
    return rows


def merge_with_metadata(parameters: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a template dict enriched with shared metadata defaults."""

    merged = dict(DEFAULT_METADATA)
    merged.update(overrides)
    merged.update(parameters)
    return merged


def checklist_rows(items: Iterable[str] | None = None) -> List[Dict[str, str]]:
    """Return checklist rows suitable for Excel export."""

    source = list(items or STANDARD_CHECKLIST)
    return [{"Checklist Item": item} for item in source]


def owner_profile_rows(items: Iterable[OwnerProfile] | None = None) -> List[Dict[str, str]]:
    """Return owner/profile rows suitable for Excel export."""

    profiles = list(items or OWNER_PROFILES.values())
    return [
        {
            "Profile Key": profile.key,
            "Owner": profile.owner,
            "Drawing Standard": profile.drawing_standard,
            "Design Live Load": profile.design_live_load,
            "Review Note": profile.review_note,
        }
        for profile in profiles
    ]


def phase_two_sheet_rows(items: Iterable[Dict[str, str]] | None = None) -> List[Dict[str, str]]:
    """Return sheet schedule rows for the phase two package."""

    return list(items or PHASE_TWO_SHEETS)


def phase_three_sheet_rows(items: Iterable[Dict[str, str]] | None = None) -> List[Dict[str, str]]:
    """Return sheet schedule rows for the phase three (11-sheet) package."""

    return list(items or PHASE_THREE_SHEETS)
