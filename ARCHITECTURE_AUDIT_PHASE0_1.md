# Architecture Audit — Phase 0 & 1
<!-- Principal Architect: Kiro AI | Date: 2026-04-01 | Scope: Full workspace -->

---

## Phase 0 — Baseline Status

### Smoke Test Results
| Test | Result |
|------|--------|
| `python -m pytest test_ultimate_app.py` | ✅ 2/2 PASSED |
| Core pipeline: Excel → DXF (sample_input.xlsx) | ✅ 72 KB DXF generated |
| Module import: `BridgeGADGenerator` | ✅ Clean |
| Module import: `api.py` (FastAPI) | ✅ Clean |

### Fixes Applied in This Session
| ID | File | Fix |
|----|------|-----|
| FutureWarning | `enhanced_io_utils.py:208-209` | `row[0]` → `row.iloc[0]`, `row[1]` → `row.iloc[1]` |
| PytestReturnNotNone | `test_ultimate_app.py` | `return bool` → `assert`, `return tuple` → `assert` |

### Pre-existing Fixes (already in codebase)
| ID | File | Status |
|----|------|--------|
| KERO-001 | `api.py` | ✅ `allow_credentials=False` |
| KERO-002 | `telemetry.py` | ✅ Opt-in via `BRIDGE_GAD_TELEMETRY=1` |
| KERO-003 | `api.py` | ✅ `Path(filename).name` sanitisation |
| KERO-004 | `streamlit_app_ultimate.py` | ✅ PII moved to env vars |
| BOLT-001 | `streamlit_app_ultimate.py` | ✅ Real export logic (Excel/CSV/HTML/ZIP) |
| BOLT-002 | `app_lean.py` | ✅ `tempfile.TemporaryDirectory` |
| BOLT-003 | `core.py` | ✅ `compute_load`/`two_opt` moved to `routing.py` |
| BOLT-004 | `streamlit_app_ultimate.py` | ✅ Single read into `_df_raw`, seek(0) |
| CURSOR-001 | `requirements.txt` | ✅ Conflicts removed |
| CURSOR-002 | `bridge_generator.py` | ✅ Dead branch fixed |
| CURSOR-003 | `parameters.py` | ✅ `Optional[float] = None` |
| CURSOR-004 | `advanced_features.py` | ✅ Empty ndarray guard |
| GENSPARK-001 | `core.py` | ✅ Config optional, falls back to defaults |
| QODER-001 | `requirements.txt` | ✅ `pygame` removed |
| QODER-002 | `streamlit_app_ultimate.py` | ✅ `@st.cache_resource` on heavy imports |
| QODER-005 | `telemetry.py` | ✅ Debounced flush at exit |
| REPLIT-001 | `core.py` | ✅ Excel read no longer commented out |
| REPLIT-002 | `bridge_generator.py` | ✅ `generate_complete_drawing` exists |
| REPLIT-004 | `api.py` | ✅ Correct MIME types |
| REPLIT-005 | `test_ultimate_app.py` | ✅ Correct import |
| WARP-001 | `requirements.txt` | ✅ Single source of truth |
| WARP-004 | `plugin_registry.py` | ✅ Lazy `import requests` |
| WINDSURF-004 | `streamlit_app_ultimate.py` | ✅ Explicit filter map |

---

## Phase 1 — Architecture Summary

### Repository Structure
```
Bridge_GAD_Yogendra_Borse-main/   ← Main workspace (this repo)
├── src/bridge_gad/               ← Core Python package
│   ├── bridge_generator.py       ← PRIMARY: Excel → DXF engine (1200+ lines)
│   ├── core.py                   ← BridgeDrawing wrapper + generate_bridge_drawing()
│   ├── api.py                    ← FastAPI REST endpoint (/predict, /health)
│   ├── advanced_features.py      ← Templates, QA checker, 3D viz, comparator
│   ├── ai_optimizer.py           ← AI design optimizer + report generator
│   ├── multi_sheet_generator.py  ← 4-sheet detailed drawing package
│   ├── parameters.py             ← BridgeParameters dataclass + validation
│   ├── drawing_generator.py      ← Strategy-pattern drawing dispatcher
│   ├── enhanced_io_utils.py      ← Smart Excel/OCR/unstructured input parser
│   ├── telemetry.py              ← Opt-in usage telemetry
│   ├── plugin_registry.py        ← Plugin discovery + lazy update check
│   └── ...                       ← CLI, config, geometry, mesh, output formats
├── streamlit_app_ultimate.py     ← PRIMARY UI: 10-tab Streamlit app
├── app_lean.py                   ← Lean fallback UI (2-mode, minimal deps)
├── inputs/                       ← 7 sample Excel input files
├── outputs/                      ← Generated DXF/PDF/PNG outputs
├── docs/                         ← User manual (MD + PDF)
├── BridgeCanvas/                 ← Archive: earlier Replit-era versions
└── tests / pyproject.toml        ← pytest config, 2 tests passing
```

### Frontend / Backend Boundaries
| Layer | Technology | Status |
|-------|-----------|--------|
| UI | Streamlit (Python) | ✅ Production-ready |
| REST API | FastAPI + uvicorn | ✅ Functional |
| Drawing Engine | ezdxf + custom geometry | ✅ Core working |
| Background Tasks | None (synchronous) | ⚠️ Blocking on large inputs |
| State Management | `st.session_state` | ✅ Adequate for Streamlit |

### Input Modes Supported
| Mode | Status |
|------|--------|
| Structured Excel (3-col: Value/Variable/Description) | ✅ Working |
| Hybrid (Excel + smart fallback parsing) | ✅ `SmartInputProcessor` |
| Unstructured (OCR/images) | ⚠️ Hooks exist, not fully wired |

### Security Posture
| Item | Status |
|------|--------|
| CORS wildcard + no credentials | ✅ Fixed |
| Path traversal on upload | ✅ Fixed (`Path.name` sanitisation) |
| PII in source | ✅ Fixed (env vars) |
| Telemetry consent | ✅ Fixed (opt-in) |
| Plugin update MITM | ⚠️ No TLS pinning (low risk for internal tool) |

---

## Best Feature Matrix

| Feature | Location | Stability | Maintainability | Decision |
|---------|----------|-----------|-----------------|----------|
| Excel → DXF engine | `bridge_generator.py` | ✅ High | ✅ High | **KEEP — primary engine** |
| 10-tab Streamlit UI | `streamlit_app_ultimate.py` | ✅ High | ✅ High | **KEEP — primary UI** |
| Lean fallback UI | `app_lean.py` | ✅ High | ✅ High | **KEEP — lightweight entry point** |
| FastAPI REST | `api.py` | ✅ High | ✅ High | **KEEP — API layer** |
| Smart input parser | `enhanced_io_utils.py` | ✅ Medium | ✅ High | **KEEP — handles messy inputs** |
| 3D visualizer | `advanced_features.py` | ✅ Medium | ✅ Medium | **KEEP — Plotly 3D** |
| AI optimizer | `ai_optimizer.py` | ⚠️ Medium | ⚠️ Medium | **KEEP — extend later** |
| 4-sheet generator | `multi_sheet_generator.py` | ✅ Medium | ✅ Medium | **KEEP** |
| Plugin system | `plugin_registry.py` | ⚠️ Low | ⚠️ Low | **SIMPLIFY — over-engineered** |
| Telemetry | `telemetry.py` | ✅ Fixed | ✅ High | **KEEP — opt-in only** |
| BridgeCanvas archive | `BridgeCanvas/` | ⚠️ Legacy | ❌ Low | **ARCHIVE — do not merge** |
| `routing.py` (two_opt) | `routing.py` | ❌ Unrelated | ❌ Low | **REMOVE — not bridge code** |
| 40+ status MD files | root | N/A | ❌ Noise | **REMOVE from main branch** |

---

## Remaining Open Issues (Prioritised)

### High Priority
1. **BEAM bridge type** — `drawing_generator.py` beam strategies delegate to slab (CURSOR-005). No UI warning.
2. **Background jobs** — Large Excel files block the Streamlit main thread. Need async/ARQ for Phase 7.
3. **PDF export from DXF** — `output_formats.py` needs verification that DXF→PDF conversion works end-to-end.

### Medium Priority
4. **WINDSURF-001** — Hero header uses `unsafe_allow_html` bypassing accessibility tree.
5. **WINDSURF-002** — Bill input fields use `label_visibility="collapsed"` (no accessible names).
6. **WINDSURF-003** — Contrast ratio on metric cards below WCAG AA.
7. **REPLIT-003** — Draft load is a stub (selectbox renders but no load action).
8. **LOVABLE-001** — Tabs 4–7 (Quality/3D/Compare/AI) need verification they render content.

### Low Priority
9. **WARP-002** — Three deploy scripts; no canonical `Makefile`.
10. **WARP-003** — 40+ status MD files committed to repo root.
11. **QODER-003** — `generate_3d_mesh` uses list.append loop; vectorise for large bridges.

---

## Next Phase Recommendations

**Phase 2 (Architecture Design):** The current structure is already close to the target layout. Recommended reorganisation:
```
/frontend  → streamlit_app_ultimate.py + app_lean.py
/backend   → src/bridge_gad/api.py + core.py
/engine    → src/bridge_gad/bridge_generator.py + drawing_generator.py
/worker    → Add ARQ worker for async job processing
/tests     → Move test_ultimate_app.py here, add more tests
/docker    → Add Dockerfile + docker-compose.yml
/scripts   → Consolidate deploy scripts into Makefile
/docs      → Already exists
/configs   → config.yaml + .env.example
```

**Phase 7 (Background Jobs):** Recommend ARQ over Celery — simpler async-native setup, no Redis broker required for single-server deployments. Add SSE endpoint for real-time job status.
