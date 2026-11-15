# Comprehensive Frontend Architecture Audit & Engineering Overhaul Plan
**Project:** NASA / JPL Orbital Architect (Space Mission Design & Flight Simulation Platform)
**Target Standard:** NASA-STD-3001, MIL-STD-1472, OpenMCT & Systems Tool Kit (STK) caliber.

---

## 1. Existing Problems Identified
1. **Navigation Completeness:** The existing UI only had 3 top tabs (`[01] FLIGHT DIRECTOR`, `[02] SPACECRAFT CAD`, `[03] ASTRODYNAMICS`). The prompt mandates an authentic, collapsible left navigation sidebar featuring 16 operational workstations:
   - Mission Overview / Landing Hero
   - Mission Selection & Briefing
   - Spacecraft Designer (CAD)
   - Payload & Scientific Instruments
   - Electrical Power Systems (EPS)
   - Propulsion & Stationkeeping
   - RF Communications & TTC
   - Orbit & Astrodynamic Trajectory
   - Launch Vehicle Configuration
   - Mission Simulation Environment
   - Mission Control Operations (OpenMCT)
   - Real-Time Telemetry & Strip-charts
   - Post-Mission Reports & Evaluation
   - Team Collaboration & Presence
   - Leaderboard & Archives
   - Settings & NASA Standards Calibration
2. **Top Persistent Taskbar:** Missing mission identifier tags, simulation clock controls, system health annunciators, active team presence pills, and documentation links.
3. **Bottom Persistent Telemetry Status Bar:** Missing authoritative backend heartbeat ping indicator, active mission name, current operation, system warning counters, and autosave timestamp.
4. **Interactive Completeness & Dead Elements:** Several filters, sliders, and buttons had simplified behavior without full parametric updates or state persistence.
5. **3D Fidelity & Precision:** The Three.js viewport needed multiple interactive camera angles, component hover raycasting and inspection overlays, exploded view mechanics, and high-precision technical wireframe rendering matching the NASA spacecraft reference schematic.

---

## 2. Required Architectural Corrections
1. **State Centralization:** Implement a robust, unified reactive state manager managing:
   - `activeWorkstation`: string ID of the active view.
   - `isSidebarExpanded`: boolean for collapsible sidebar with tooltips.
   - `missionCharter`: selected scenario object loaded from `/api/v1/scenarios`.
   - `spacecraftConfig`: assembled component IDs, chassis class, launch vehicle, orbital parameters.
   - `resourceBudgets`: AIAA S-120 Mass Growth Allowance, Battery DoD, RF Link Margin, Cost.
   - `simulationTelemetry`: live simulation state, current phase (Pre-launch -> In-flight -> Insertion -> Operations), events buffer, time-series arrays.
   - `collaborators`: team presence and multiplayer status.
2. **NASA-STD-3001 Design Tokens:** Strict non-rounded $0\text{px}$ industrial UI, `IBM Plex Mono` tabular numerals, restrained color palettes (Nominal Green `#00E676`, Caution Amber `#FFAB00`, Warning Crimson `#FF1744`, Carrier Cyan `#00E5FF`, Solar Gold `#FFD600`).
3. **Every Control Functional:** Ensure every tab, sidebar link, modal action, filter button, mount/demount switch, slider, speed toggle, anomaly directive, and export trigger executes real state updates and engineering validation calls.
