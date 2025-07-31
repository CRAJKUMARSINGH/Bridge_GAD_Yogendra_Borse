# Bridge-GAD Road-Map Prompt (share-ready)

Below is a **turn-key GitHub issue / README section** you can paste directly into the repo to broadcast the agreed-upon plan to contributors and stakeholders.

---

## 🚀 Road-Map: From `originallist.txt` to Production-Grade Bridge-GAD

> *This issue summarises the full engineering plan.  
> Each box becomes its own GitHub issue when work starts.*

### ✅ Phase 0 – Repository Hygiene *(½ day)*
- [ ] Fork & protect `main`, add `LICENSE`, `.gitignore`, `README.md`  
- [ ] Add JSON-Schema validator for `originallist.txt` in CI

### ✅ Phase 1 – Core Engine *(2–3 days)*
- [ ] Create `src/` layout (`parser.py`, `geometry.py`, `drawer.py`, `exporter.py`)  
- [ ] 100 % unit-test coverage with `pytest`  
- [ ] CLI: `python -m bridge_gad draw --input originallist.txt --format dxf --scale 50`

### ✅ Phase 2 – Desktop GUI *(3–4 days)*
- [ ] Qt (PySide6) or Electron front-end  
- [ ] Zoom, pan, property table, save DXF/PDF  
- [ ] Auto-build signed installers via GitHub Actions

### ✅ Phase 3 – Web API & SPA *(5–7 days)*
- [ ] FastAPI back-end (`/elements`, `/draw`, `/export`)  
- [ ] Docker image & CI push to GHCR  
- [ ] React + Konva SPA (PWA) deployed on Vercel  
- [ ] Cypress e2e tests on every PR

### ✅ Phase 4 – Collaboration & Versioning *(1 week)*
- [ ] PostgreSQL + SQLModel for projects & revisions  
- [ ] JWT auth (GitHub / Google OAuth)  
- [ ] Real-time multi-user editing via WebSocket

### ✅ Phase 5 – Advanced Engineering *(rolling)*
- [ ] Parametric template wizard  
- [ ] Clash detection & BoM generation  
- [ ] IFC4 export for BIM workflows

### ✅ Phase 6 – Cloud SaaS *(2 weeks)*
- [ ] Stripe metering & org workspaces  
- [ ] RBAC, usage analytics, SOC-2 checklist  
- [ ] Public REST + GraphQL API

### ✅ Phase 7 – Ecosystem / Plug-ins *(post-MVP)*
- [ ] Revit Add-in  
- [ ] Excel Add-in (bidirectional sync)  
- [ ] Community plug-in marketplace

---

### 📅 Milestones
| Milestone | Target Date | Definition of Done |
|-----------|-------------|--------------------|
| **M0** | Day 0 | Repository hygiene complete |
| **M1** | Day 3 | CLI v0.1 tagged & released |
| **M2** | Day 7 | Desktop beta installers |
| **M3** | Day 14 | Web MVP live (no auth) |
| **M4** | Day 30 | Auth + multi-user + DXF |
| **M5** | Day 60 | SaaS public launch |

---

### 🛠️ Tech Stack
| Tier | Tech |
|---|---|
| **Core engine** | Python ≥ 3.11 (`shapely`, `ezdxf`, `trimesh`) |
| **Web API** | FastAPI → Docker → AWS ECS Fargate |
| **Front-end** | React + Konva + Three.js (PWA) |
| **Desktop** | PySide6 OR Electron |
| **CI/CD** | GitHub Actions → Vercel (front) / Render (back) |
| **Infra** | Terraform, RDS Postgres, S3, Redis |

---

### ⚠️ Risk Register
- **Unit mismatch** → enforce schema + UI selector  
- **Large files** → streaming parser + LOD renderer  
- **Browser memory** → tiled canvas + WebGL

---

**Next step:** convert this issue into individual GitHub issues using the checkbox list above.  
Happy building! 🚧
