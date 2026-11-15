# TECHNICAL IMPLEMENTATION ROADMAP & WORK-BREAKDOWN STRUCTURE (WBS)
**Project Codename:** `ORBITAL ARCHITECT` (Directory: `/Users/subham/code/Lucy`)  
**Role:** Technical Project Manager & Engineering Lead  
**Document Version:** 1.0.0  
**Core Strategy:** *Working End-to-End Vertical Slice First $\to$ High-Fidelity Simulation Polish $\to$ Multiplayer Concurrency*

---

## 1. PROJECT SCOPE CATEGORIZATION (MVP VS. ENHANCEMENTS)

To ensure the team delivers a fully functioning, high-polish submission within hackathon constraints, features are partitioned into three delivery tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DELIVERY TIER BREAKDOWN                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: MUST-HAVE MVP (Hours 0 - 20)                                        │
│  - 3 Core Missions: Earth EO (SSO), Lunar Polar, Mars Relay.                │
│  - 15 Core Components (Basic & Intermediate tiers across all 8 subsystems). │
│  - Closed-form Astrodynamics (Keplerian orbits, SSO J2, Hohmann, Eclipse).  │
│  - Real-time AIAA S-120 Mass & Energy Balance Gauges.                       │
│  - 3D WebGL Orbital Canvas (Rotating Earth + Procedural Satellite Bus).     │
│  - 1,000-Point Scoring Engine & Automated Post-Flight Debrief Dossier.      │
│  - Full REST API + Single-Player "Director Console" Mode.                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: HIGH-VALUE ENHANCEMENTS (Hours 20 - 36)                             │
│  - Full 31-Component Catalog (incorporating Advanced Tier SAR & Ion).       │
│  - 4-Player Cooperative Real-Time WebSocket Rooms (Role Locks + FRR Vote).  │
│  - Event-Driven Anomaly Injection (Solar Flares, Reaction Wheel Saturation).│
│  - Rayleigh Atmosphere Rim Shader & Thermal Dissipation Heatmap Mode.       │
│  - Global Leaderboard with HMAC Cryptographic Verification Signatures.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: POST-HACKATHON FUTURE SCOPE                                         │
│  - N-Body Numerical Integrator with Lunar Mascon Gravitational Harmonics.   │
│  - WebRTC Peer-to-Peer Voice Communications in Multiplayer Room.            │
│  - Native Mobile Touch Controls via WebXR / Touch Gestures.                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. THE 15-STAGE WORK BREAKDOWN STRUCTURE (WBS)

---

### STAGE 1: Repository Initialization & Toolchain Setup
* **Task ID:** `TSK-01-REPO-INIT`
* **Description:** Initialize Git repository, directory scaffolding, Python virtual environment, Node.js toolchain, linting (ruff, eslint), and container orchestration (`docker-compose.yml`).
* **Dependencies:** None (Day 1, Hour 0).
* **Priority:** P0 (Blocker).
* **Estimated Effort:** 1.5 Hours.
* **Expected Deliverable:** Functional repo root with passing pre-commit hooks and containerized database.
* **Acceptance Criteria:** `docker compose up -d` boots Postgres 15 and initializes schema cleanly.
* **Responsible Role:** DevOps / Infrastructure Lead (Dev 4).

---

### STAGE 2: Frontend Foundation & Design System Scaffolding
* **Task ID:** `TSK-02-FE-FOUNDATION`
* **Description:** Scaffold React 18 + Vite + TypeScript application with Tailwind CSS, shadcn/ui components, and Lucide icons. Implement global obsidian design tokens (`tokens.json`).
* **Dependencies:** `TSK-01-REPO-INIT`.
* **Priority:** P0.
* **Estimated Effort:** 2.5 Hours.
* **Expected Deliverable:** Responsive shell with navigation bars, monospace typography, and layout containers.
* **Acceptance Criteria:** Application loads at `localhost:3000` with 0 console warnings; themes adhere to NASA telemetry palette.
* **Responsible Role:** Frontend Lead (Dev 1).

---

### STAGE 3: Backend Foundation & API Architecture
* **Task ID:** `TSK-03-BE-FOUNDATION`
* **Description:** Scaffold FastAPI application with structured routers (`/auth`, `/components`, `/spacecraft`, `/simulation`), global CORS middleware, error handling, and Pydantic v2 schemas.
* **Dependencies:** `TSK-01-REPO-INIT`.
* **Priority:** P0.
* **Estimated Effort:** 2.0 Hours.
* **Expected Deliverable:** Live FastAPI server running on `localhost:8000` with auto-generated Swagger UI at `/docs`.
* **Acceptance Criteria:** `GET /api/v1/health` returns `200 OK` with JSON status envelope.
* **Responsible Role:** Backend Lead (Dev 2).

---

### STAGE 4: Component Catalog & Relational Database Layer
* **Task ID:** `TSK-04-DATA-CATALOG`
* **Description:** Populate database with verified 31-component catalog across 10 subsystems and 3 tiers (`components_catalog.json`). Build automated validation script.
* **Dependencies:** `TSK-01-REPO-INIT`, `TSK-03-BE-FOUNDATION`.
* **Priority:** P0.
* **Estimated Effort:** 2.0 Hours.
* **Expected Deliverable:** `validate_catalog.py` passing 100% of physical non-negativity and prerequisite checks.
* **Acceptance Criteria:** `GET /api/v1/components` serves all 31 components with zero broken relational references.
* **Responsible Role:** Aerospace Systems Engineer (Dev 3).

---

### STAGE 5: Astrodynamics & Simulation Engine Core
* **Task ID:** `TSK-05-SIM-ASTRO`
* **Description:** Implement `OrbitalCalculator` in Python (`calculator.py`): Keplerian period, vis-viva velocity, eclipse duration geometry, $J_2$ Sun-Synchronous inclination, Hohmann transfers, and FSPL link margin.
* **Dependencies:** `TSK-03-BE-FOUNDATION`.
* **Priority:** P0.
* **Estimated Effort:** 3.5 Hours.
* **Expected Deliverable:** Analytical calculation suite matching NASA GMAT benchmarks within $<0.01\%$ error.
* **Acceptance Criteria:** `pytest testing/test_aerospace_verification.py` passes 100% of orbital conservation invariant tests.
* **Responsible Role:** Aerospace Systems Engineer (Dev 3).

---

### STAGE 6: Spacecraft Assembly Studio & Component Drawer UI
* **Task ID:** `TSK-06-UI-STUDIO`
* **Description:** Build the interactive assembly studio with category filter pills, component mount/remove toggles, tier badges, and side-by-side delta comparisons.
* **Dependencies:** `TSK-02-FE-FOUNDATION`, `TSK-04-DATA-CATALOG`.
* **Priority:** P0.
* **Estimated Effort:** 3.5 Hours.
* **Expected Deliverable:** Left-sidebar component selector updating local Zustand `useMissionStore`.
* **Acceptance Criteria:** Clicking "Mount" updates installed component array and triggers dynamic margin recalculations.
* **Responsible Role:** Frontend Lead (Dev 1).

---

### STAGE 7: Real-Time Resource Management & Margin Gauges
* **Task ID:** `TSK-07-RES-MARGINS`
* **Description:** Build the live AIAA Margin Gauges on the right sidebar: Mass Growth Allowance (+20%), Day/Night battery Depth-of-Discharge, RF Link Margin, and Budget remaining.
* **Dependencies:** `TSK-05-SIM-ASTRO`, `TSK-06-UI-STUDIO`.
* **Priority:** P0.
* **Estimated Effort:** 3.0 Hours.
* **Expected Deliverable:** Animated vector margin meters responding to slider adjustments in under 16ms (60 FPS).
* **Acceptance Criteria:** Exceeding mass or battery limits dynamically flips gauge colors from emerald to red.
* **Responsible Role:** Full-Stack Developer (Dev 2).

---

### STAGE 8: Mission Manifest & Orbital Selection Interface
* **Task ID:** `TSK-08-ORBIT-UI`
* **Description:** Build the mission scenario selector (6 scenarios) and orbital parameter inputs (Altitude, Inclination, Launcher class dropdown).
* **Dependencies:** `TSK-05-SIM-ASTRO`, `TSK-06-UI-STUDIO`.
* **Priority:** P0.
* **Estimated Effort:** 2.5 Hours.
* **Expected Deliverable:** Mission selection view connected to backend scenarios dataset (`mission_scenarios.json`).
* **Acceptance Criteria:** Changing altitude automatically recalculates orbital period and eclipse duration.
* **Responsible Role:** Frontend Lead (Dev 1).

---

### STAGE 9: Launch Simulation & Staging Visualizer
* **Task ID:** `TSK-09-LAUNCH-SIM`
* **Description:** Implement launch verification check (wet mass vs. rocket lift capacity) and staging animation sequence (Liftoff $\to$ MECO $\to$ Fairing Jettison $\to$ Spacecraft Separation).
* **Dependencies:** `TSK-07-RES-MARGINS`.
* **Priority:** P1.
* **Estimated Effort:** 2.5 Hours.
* **Expected Deliverable:** Launch sequence modal with acoustic $g$-load stress telemetry and staging event logs.
* **Acceptance Criteria:** Over-mass spacecraft triggers realistic structural buckle launch abort.
* **Responsible Role:** Full-Stack Developer (Dev 2).

---

### STAGE 10: Mission Operations Console & In-Flight Telemetry
* **Task ID:** `TSK-10-OPS-CONSOLE`
* **Description:** Build the real-time flight operations console: time-warp controls ($1\times$ to $1000\times$), streaming telemetry strip charts, ground station pass countdowns, and instrument duty toggles.
* **Dependencies:** `TSK-07-RES-MARGINS`.
* **Priority:** P0.
* **Estimated Effort:** 3.5 Hours.
* **Expected Deliverable:** Flight operations HUD streaming battery SoC, bus temperature, and ground station LOS contacts.
* **Acceptance Criteria:** Passing into Earth shadow reduces solar output to 0W and triggers battery discharge.
* **Responsible Role:** Full-Stack Developer (Dev 2).

---

### STAGE 11: 3D Scientific Visualization Engine (Three.js / R3F)
* **Task ID:** `TSK-11-3D-ENGINE`
* **Description:** Build the dual-scale 3D WebGL viewport: Earth planetary body, procedural modular spacecraft PBR mesh, and GPU-instanced `Line2` orbit ribbons.
* **Dependencies:** `TSK-02-FE-FOUNDATION`, `TSK-05-SIM-ASTRO`.
* **Priority:** P0.
* **Estimated Effort:** 4.5 Hours.
* **Expected Deliverable:** 60 FPS 3D canvas with CAD view, orbit view, exploded bus mode, and solar ray vector.
* **Acceptance Criteria:** Modifying orbit inclination tilts the 3D Keplerian ellipse in a single frame.
* **Responsible Role:** 3D Graphics / Visualization Specialist (Dev 4).

---

### STAGE 12: Mission Evaluation, Scoring & Debrief Dossier
* **Task ID:** `TSK-12-EVAL-SCORING`
* **Description:** Implement the 1,000-point multi-attribute scoring engine (`scoring.py`), failure gates, honor grades (A+, A, B, C, F), and downloadable JSON/PDF flight dossiers.
* **Dependencies:** `TSK-10-OPS-CONSOLE`.
* **Priority:** P0.
* **Estimated Effort:** 2.5 Hours.
* **Expected Deliverable:** Post-flight results modal with score breakdown radar chart and exportable flight report.
* **Acceptance Criteria:** Successfully fulfills the worked case studies (Flagship = 950 pts, CubeSat = 734 pts, Brownout = 0 pts).
* **Responsible Role:** Aerospace Systems Engineer (Dev 3).

---

### STAGE 13: Cooperative Multiplayer WebSocket Gateway
* **Task ID:** `TSK-13-MP-WEBSOCKET`
* **Description:** Implement room-based WebSocket gateway (`/ws/mission/{room_id}`), 4-seat role claims (Mission Director, Spacecraft Engineer, Science PI, Flight Ops), and single-writer mutation locks.
* **Dependencies:** `TSK-03-BE-FOUNDATION`, `TSK-07-RES-MARGINS`.
* **Priority:** P1 (High-Value Enhancement).
* **Estimated Effort:** 4.0 Hours.
* **Expected Deliverable:** Collaborative CDF room synchronizing design changes across 4 browsers in $<50\text{ ms}$.
* **Acceptance Criteria:** All 4 specialists must cast unanimous FRR approval votes to clear launch.
* **Responsible Role:** DevOps / Infrastructure Lead (Dev 4).

---

### STAGE 14: End-to-End Verification, Performance & Stress Testing
* **Task ID:** `TSK-14-TEST-HARNESS`
* **Description:** Execute the 10 critical failure mode tests (`TC-MASS-01` through `TC-ANOMALY-01`), Playwright UI integration tests, and WebSocket latency profiling.
* **Dependencies:** Stages 1 through 13.
* **Priority:** P0.
* **Estimated Effort:** 3.0 Hours.
* **Expected Deliverable:** Automated test report verifying 100% pass rate across physical invariants.
* **Acceptance Criteria:** Zero unhandled runtime exceptions; physical conservation laws hold over 1,000 orbits.
* **Responsible Role:** Aerospace Systems Engineer (Dev 3).

---

### STAGE 15: Production Hardening & Zero-Config Deployment
* **Task ID:** `TSK-15-DEPLOY-PROD`
* **Description:** Finalize production multi-stage Docker build, configure rate limiting, CORS lockdowns, static asset bundling, and verify zero-downtime execution.
* **Dependencies:** Stage 14.
* **Priority:** P0.
* **Estimated Effort:** 1.5 Hours.
* **Expected Deliverable:** One-command startup via `docker compose up -d` running live at `http://localhost:8000`.
* **Acceptance Criteria:** Clean startup in fresh cloud VM with zero manual configuration steps required.
* **Responsible Role:** DevOps / Infrastructure Lead (Dev 4).

---

## 3. THE CRITICAL PATH ANALYSIS

The minimum dependency chain determining project delivery time is:

$$\text{TSK-01} \longrightarrow \text{TSK-03} \longrightarrow \text{TSK-05} \longrightarrow \text{TSK-07} \longrightarrow \text{TSK-10} \longrightarrow \text{TSK-12} \longrightarrow \text{TSK-14} \longrightarrow \text{TSK-15}$$

```
Hours:  0      2      4      6      8      10     12     14     16     18     20     22     24
        ├──TSK-01──┤
               ├──TSK-03──┤
                      ├──TSK-05 (Astrodynamics)──┤
                                     ├──TSK-07 (Margins)──┤
                                                    ├──TSK-10 (Ops Console)──┤
                                                                   ├──TSK-12 (Scoring)──┤
                                                                                  ├──TSK-14──┤
                                                                                         ├──TSK-15──┤
```
*Total Critical Path Duration:* **20.5 Hours**. Working in parallel allows the 4-developer team to complete the full MVP plus multiplayer enhancements within 36 hours.

---

## 4. PARALLEL DEVELOPMENT PLAN (4 DEVELOPER ROLES)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             4-DEVELOPER CONCURRENT SPRINT MATRIX                                 │
├───────────────────┬───────────────────────────────────┬──────────────────────────────────────────┤
│ Developer Role    │ Phase 1: MVP Core (Hours 0 - 18)  │ Phase 2: Polish & Multiplayer (18 - 36) │
├───────────────────┼───────────────────────────────────┼──────────────────────────────────────────┤
│ DEV 1: Lead UI/UX │ - TSK-02: React Shell & Tokens    │ - TSK-08: Orbit Selection & Ground Map   │
│ & Frontend        │ - TSK-06: Spacecraft CAD Studio   │ - Subsystem Tooltip Aerospace Notebook   │
│                   │ - Component Selection Drawers     │ - Post-Mission Debrief Modal & Graphs    │
├───────────────────┼───────────────────────────────────┼──────────────────────────────────────────┤
│ DEV 2: Full-Stack │ - TSK-03: FastAPI API Scaffolding │ - TSK-09: Launch Staging Simulation      │
│ & Systems Engine  │ - TSK-07: Live Margin Calculation │ - TSK-10: Mission Operations HUD         │
│                   │ - REST Validation Endpoints       │ - Time-Warp State Controller             │
├───────────────────┼───────────────────────────────────┼──────────────────────────────────────────┤
│ DEV 3: Aerospace  │ - TSK-04: Component Catalog Data  │ - TSK-12: 1,000-Pt Scoring Rubric Engine │
│ Specialist & QA   │ - TSK-05: Keplerian Math Engine   │ - Operations Anomaly Generator           │
│                   │ - GMAT Benchmark Validation       │ - TSK-14: Aerospace V&V Test Suite       │
├───────────────────┼───────────────────────────────────┼──────────────────────────────────────────┤
│ DEV 4: 3D Graphics│ - TSK-01: Repo & Docker Compose   │ - Atmospheric Rayleigh Shader            │
│ & Infrastructure  │ - TSK-11: Three.js Earth & Orbit  │ - TSK-13: 4-Player WebSocket Gateway     │
│                   │ - Procedural Spacecraft PBR Model │ - TSK-15: Cloud Deployment & Hardening   │
└───────────────────┴───────────────────────────────────┴──────────────────────────────────────────┘
```

---

## 5. RISK MITIGATION & CONTINGENCY PROTOCOLS

1. **Risk: 3D WebGL Performance Glitches on Evaluator Machines:**
   * *Mitigation:* The 3D viewport includes a one-click **"Performance Fallback Mode"** that toggles off shadows and drops texture resolutions to 1K, guaranteeing 60 FPS on any basic laptop.
2. **Risk: WebSocket Multiplayer Network Latency / Desync During Live Demo:**
   * *Mitigation:* The architecture features an instantaneous **"Single-Player Multi-Seat Switcher"** toggle. If network drops, the flight director can switch between all 4 specialist seats on a single browser tab with zero loss of functionality.
3. **Risk: Mathematical Divergence in Astrodynamics Calculations:**
   * *Mitigation:* The engine uses analytical closed-form Keplerian equations for all baseline orbital tracks, strictly avoiding unstable numerical runaway while preserving physical fidelity.
