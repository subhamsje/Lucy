# UI/UX ARCHITECTURE & SCREEN-BY-SCREEN SPECIFICATION: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Design Director:** Principal Product Designer & Game UI/UX Systems Architect  
**Visual Style:** Professional NASA/ESA Mission Control + Engineering CAD Simulator (High-density, low-clutter, data-focused)

---

## 1. DESIGN SYSTEM & ERGONOMIC FOUNDATIONS

### 1.1 Aesthetic Tone & Visual Metaphor
The interface reflects a modern **Aerospace Operations & Concurrent Design Facility (CDF)** console (comparable to NASA JPL Mission Control, SpaceX Starbase Terminal, and ESA ESTEC Concurrent Design Facility).
* **Color Psychology:** Deep space obsidian background (`#0A0D14`) minimizes eye strain during extended simulation sessions.
* **Functional Color Coding:** Strict NASA standard telemetry hues (Emerald `#10B981` = Nominal, Amber `#F59E0B` = Caution, Ruby `#EF4444` = Critical/Violation, Cyan `#0EA5E9` = Active Telemetry Carrier).
* **High Information Density:** Dense monospace tabular data paired with clean vector SVG margin bars, avoiding cartoonish skeuomorphism or gratuitous sci-fi holographic clutter.

### 1.2 Global Navigation & Persistent Status Bar
Every screen inside an active mission session displays the persistent **Mission Systems Header**:
```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [● LIVE CDF] MISSION: IGNIS-SENTINEL (LEO-550) │ CLOCK: T+000:04:12:35 │ WARP: 10x [▶][▶▶][⏸]         │
│ DRY MASS: 342.5 kg (MGA +18.4%) │ POWER BAL: +42.5 W │ DATA: 45.2/256 GB │ BUDGET: $18.4M / $35.0M     │
│ TEAM: [SYST: You] [SCI: Online] [PWR: Online] [OPS: Waiting]                │ [HELP / DICTIONARY] [ABORT]│
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. THE 20 DETAILED SCREEN SPECIFICATIONS

---

### SCREEN 1: Landing Page (Mission Control Gateway)
* **Layout:** Centered aerospace terminal viewport with an interactive 3D WebGL rotating orbital Earth in dark mode. Subdued starfield with faint orbit ground tracks.
* **Navigation:** `[ENTER SIMULATOR]`, `[DAILY CHALLENGE]`, `[CAREER DOSSIER]`, `[SYSTEM SETTINGS]`.
* **Main Interactions:**
  * One-click start into Quick Start Cadet mission.
  * Room code input field for multiplayer join.
  * Orbital globe allows mouse drag to inspect real satellites in orbit.
* **Information Hierarchy:**
  1. System Title: `ORBITAL ARCHITECT // Mission Control Directorate`.
  2. Live simulation status ticker (active missions, global leaderboard champion).
  3. Action buttons (Primary: Emerald `START MISSION`, Secondary: Outlined `MULTIPLAYER`).
* **Data Displayed:** Game version (`v1.0.0-PROD`), active player count, local UTC timestamp, user certification rank.
* **Loading State:** Faint orbital vector radar sweep animation (`INITIALIZING ASTRODYNAMICS ENGINE...`).
* **Empty State:** First-time user greeting with certification badge `RANK 0: CADET APPLICANT`.
* **Error State:** Network offline modal: `OFFLINE TELEMETRY MODE ACTIVE (Local simulation verified)`.
* **Responsive Behavior:** On tablets/small viewports, collapses 3D globe to static orbital ground-track canvas; primary CTA remains thumb-accessible.

---

### SCREEN 2: Player Onboarding & Flight Directorate Induction
* **Layout:** Multi-step modal overlay presenting the "NASA Concurrent Design Facility" charter.
* **Navigation:** `[BACK]`, `[NEXT STEP]`, `[SKIP BRIEFING]`, `[CERTIFY INDUCTION]`.
* **Main Interactions:**
  * Role selection interactive carousel (Systems Lead, Science PI, Power Lead, Flight Controller).
  * Interactive 30-second sandbox mini-game: "Balance the Mass vs. Power Gauge".
* **Information Hierarchy:**
  1. Welcome Directive from Space Flight Operations.
  2. The 3 Laws of Orbital Design: Mass Compounding, Eclipse Energy Deficit, and Link Margin.
  3. Subsystem responsibility breakdown.
* **Data Displayed:** Candidate callsign, selected flight role, starting clearance level.
* **Loading State:** Sequential teletype text reveal mimicking teleprinter feeds.
* **Empty/Error State:** Form validation flags invalid callsigns (regex: alphanumeric, 3–12 chars).

---

### SCREEN 3: Mission Selection (The Flight Manifest)
* **Layout:** Left panel (1/3 width): Filterable list of 6 scenarios categorized by destination. Right panel (2/3 width): Target destination 3D preview, orbital trajectory visualization, and environmental threat badges.
* **Navigation:** Scenario cards click to select; bottom-right CTA: `[ACCEPT CHARTER & CONFIGURE ORBIT]`.
* **Main Interactions:**
  * Filter pills: `All`, `Earth LEO/SSO`, `Lunar`, `Mars`, `Deep Space`, `Commercial GEO`.
  * Difficulty toggle: `Cadet (Assisted)`, `Specialist (Standard)`, `Flight Director (Hardcore)`.
* **Information Hierarchy:**
  1. Mission title and operational category.
  2. Target body preview with orbital parameter chips (Altitude, Period, Eclipse %).
  3. Mission constraints bar: Budget Cap (\$M), Minimum Science (GB), Duration (Days).
  4. Environmental Hazard tags (e.g., `MASCON PERTURBATION`, `VAN ALLEN BELT`, `20-MIN LATENCY`).
* **Data Displayed:** 6 scenario cards with difficulty indicators, budget ceilings, and success rewards.
* **Loading State:** Skeleton wireframe cards with animated gradient shimmer.
* **Empty State:** "No scenarios matching filter criteria" with one-click reset.

---

### SCREEN 4: Mission Briefing (The Flight Charter)
* **Layout:** Split-screen dossier. Left: Official NASA/ESA-style mission charter document with signatures and stamps. Right: Primary target telemetry, scientific objectives checklist, and payload recommendations.
* **Navigation:** `[< BACK TO MANIFEST]`, `[EXPORT PDF CHARTER]`, `[INITIALIZE CONCURRENT DESIGN >]`.
* **Main Interactions:**
  * Expandable scientific objectives accordion explaining why specific spectral bands or instruments are required.
  * Interactive timeline preview showing expected mission milestones (Launch $\to$ TLI $\to$ Orbit Insertion $\to$ Science Phase).
* **Information Hierarchy:**
  1. Primary Objective Banner (High-contrast bold font).
  2. Secondary Stretch Goals.
  3. Minimum Acceptance Criteria (GB of telemetry, ground resolution).
  4. Operational Hazard Mitigation Notes.
* **Data Displayed:** Target orbital parameters, launch window dates, allowable CapEx budget envelope.

---

### SCREEN 5: Mission Requirements Dashboard (The Systems Matrix)
* **Layout:** High-density 4-column engineering matrix summarizing the target requirements against current design values.
* **Navigation:** Subsystem tabs along the top; persistent bottom bar shows margin clearance status.
* **Main Interactions:**
  * Hovering over any requirement displays the mathematical tolerance formula.
  * "Auto-Allocate Margins" helper button (for Cadet difficulty).
* **Information Hierarchy:**
  1. System Margin Health Summary (4 radial dials: Mass Margin, Power Margin, Link Margin, Budget Margin).
  2. Target Requirement vs. Current Allocated table.
  3. Critical Path Warnings ticker.
* **Data Displayed:**
  * Mass Growth Allowance ($20\%$ standard required).
  * Eclipse Duration ($T_{\text{eclipse}}$ calculated from altitude).
  * Required Ground Sample Distance vs. Camera Focal Length.
* **Feedback States:** Dynamic color indicators (Green: Margin $\ge 15\%$, Amber: $0\% \le \text{Margin} < 15\%$, Red: Violation).

---

### SCREEN 6: Spacecraft Assembly Environment (The 3D CAD Studio)
* **Layout:**
  * Left sidebar (280px): Subsystem component selector and active installed component inventory.
  * Center viewport (Fluid 3D): Procedural 3D spacecraft model with interactive orbit/zoom/pan controls.
  * Right sidebar (320px): Live AIAA Margin Gauges and Subsystem Telemetry impact monitors.
  * Bottom drawer: Expandable Component Spec Inspector.
* **Navigation:** Subsystem icons along the left rail (`PAY`, `EPS`, `PROP`, `ADCS`, `TTC`, `TCS`, `CDH`, `STR`).
* **Main Interactions:**
  * Click component card to mount into the spacecraft chassis.
  * 3D exploded view toggle (`[EXPAND] / [STOWED]`).
  * Click on any 3D mounted module to open its parameter tuning slider (e.g., adjust battery capacity or antenna dish diameter).
* **Information Hierarchy:**
  1. Center 3D Spacecraft Canvas with dimension bounding box ($L \times W \times H$).
  2. Persistent Live Margin Gauges on the right.
  3. Action buttons: `[RUN SIMULATION TEST]`, `[VALIDATE FOR LAUNCH]`.
* **Data Displayed:** Total dry mass, wet mass, structural mass compounding, center of gravity indicator.
* **Loading State:** 3D wireframe mesh assembly animation.

---

### SCREEN 7: Component Selection Interface
* **Layout:** Filterable card grid within the left/bottom studio panels.
* **Navigation:** Tier filter tabs (`BASIC`, `INTERMEDIATE`, `ADVANCED`), sort dropdown (Cost, Mass, Power, TRL).
* **Main Interactions:**
  * "Compare Mode": Select any 2 components to view side-by-side delta bars (Mass $\Delta$, Power $\Delta$, Cost $\Delta$).
  * One-click "Mount / Replace" action.
* **Information Hierarchy:**
  1. Component Name and Subsystem Code (e.g., `INST-OPT-02 // Panchromatic Telescope`).
  2. Key specifications bar (Mass: $48\text{ kg}$ | Power: $115\text{ W}$ | Cost: $\$14.5\text{M}$).
  3. Advantages and Disadvantages bullets.
  4. Prerequisite badges (e.g., `Requires Precision Star Tracker ADCS-ST-03`).
* **Error State:** Incompatible items display a locked badge with exact conflict reason (e.g., `INCOMPATIBLE: Exceeds 12U CubeSat chassis mass limit`).

---

### SCREEN 8: Spacecraft 3D Visualization (Procedural Digital Twin)
* **Layout:** Fullscreen 3D WebGL / Three.js viewport with floating HUD overlays.
* **Navigation:** Camera viewpoint presets: `Nadir View`, `Solar Panel Sun-Vector`, `Antenna Earth-Vector`, `Fairing Stowed Wireframe`.
* **Main Interactions:**
  * Free orbit, pan, and zoom via mouse/touch controls.
  * Toggle "Solar Vector Ray" (shows angle of incidence $\cos\theta$).
  * Toggle "Thermal Heat Map" (renders red hot-spots on high-dissipation components and blue on radiators).
  * Toggle "Fairing Envelope" (overlays transparent nose-cone cylinder).
* **Information Hierarchy:**
  1. 3D Model with component selection halos.
  2. Corner HUD widgets: Spacecraft Dimensions, Center of Mass ($x, y, z$), Moments of Inertia ($I_{xx}, I_{yy}, I_{zz}$).
* **Performance:** Maintains smooth 60 FPS on integrated graphics via instanced geometries.

---

### SCREEN 9: Resource Management Dashboard (Coupled Energy & Margin Balances)
* **Layout:** Split telemetry console with 6 interactive resource balance cards.
* **Navigation:** Tabbed sub-views: `Mass Budget`, `Energy Balance (Day/Night)`, `Link Budget (RF)`, `Thermal Balance`, `Data Memory Flow`.
* **Main Interactions:**
  * Day/Night Slider: Drag simulated orbital position from sunlit phase to shadow to observe real-time battery discharge curve.
  * Duty Cycle Sliders: Adjust payload operational percentage ($10\%\text{--}100\%$) to test if solar arrays can maintain positive net energy balance.
* **Information Hierarchy:**
  1. Real-time balance equation (e.g., $P_{\text{gen}} \cdot T_{\text{sun}} \ge P_{\text{eclipse}} \cdot T_{\text{eclipse}} / \eta$).
  2. Dynamic line chart showing 3 continuous orbits of projected battery State-of-Charge (SoC).
  3. Downlink margin gauge displaying RF $E_b/N_0$ vs. $3.0\text{ dB}$ threshold.
* **Data Displayed:** Numerical watts generated, watts consumed, thermal dissipation, battery depth-of-discharge percentage.

---

### SCREEN 10: Launch Vehicle Selection (Fairing & Lift Integration)
* **Layout:** Left panel (40%): Comparison of 4 launch vehicle tiers (Electron Micro, Rideshare ESPA, Medium-Lift Falcon 9, Heavy-Lift Ariane 6). Right panel (60%): 3D rocket fairing cross-section with the stowed spacecraft positioned inside.
* **Navigation:** Click launcher card to bind contract; bottom button: `[CONFIRM LAUNCH INTEGRATION]`.
* **Main Interactions:**
  * Stowed vs. Deployed toggle button to verify solar panels fold cleanly within the fairing static line.
  * Slider for target orbit altitude adjusting launcher payload capacity curve in real time.
* **Information Hierarchy:**
  1. Launcher Name and Provider Class.
  2. Lift Capacity vs. Spacecraft Wet Mass margin gauge.
  3. Launch Contract Cost (debited from mission budget).
  4. Fairing Dynamic Clearance Indicator (`PASS: 18cm clearance` or `VIOLATION: Clipping`).
* **Error State:** If wet mass exceeds rocket capacity, the lift gauge flashes red with: `PAYLOAD MASS EXCEEDS VEHICLE THRESHOLD BY +42.5 KG`.

---

### SCREEN 11: Orbital Configuration Interface (Astrodynamics Lab)
* **Layout:** Top half: 2D Mercator world map with animated orbital ground-track sine waves and ground station visibility cones (footprints). Bottom half: Orbital parameter adjustment sliders and physical summary card.
* **Navigation:** Preset orbit buttons (`LEO 400km`, `SSO 550km`, `Dawn-Dusk 650km`, `MEO`, `GEO`).
* **Main Interactions:**
  * Sliders for Altitude ($h$), Inclination ($i$), and Eccentricity ($e$).
  * Adjusting Inclination automatically computes the $J_2$ precession rate, displaying whether Sun-Synchronous condition is achieved.
* **Information Hierarchy:**
  1. Ground Track Map showing nadir swath coverage.
  2. Orbit Properties Panel: Period ($T$), Eclipse Duration ($T_{\text{eclipse}}$), Velocity ($v$), Daily Passes.
  3. Ground Station Network checklist (e.g., Svalbard, Troll, Goldstone, Madrid).
* **Data Displayed:** Real-time calculated values from `calculator.py` (e.g., $97.78^\circ$ for $600\text{ km}$ SSO).

---

### SCREEN 12: Pre-Launch Validation (The Flight Readiness Review - FRR)
* **Layout:** Formal aerospace checklist screen modeled after NASA Flight Readiness Review (FRR) sign-offs.
* **Navigation:** `[MODIFY DESIGN]`, `[RUN DIAGNOSTICS]`, `[GO FOR LAUNCH (CERTIFIED)]`.
* **Main Interactions:**
  * Interactive checklist where the user (or multiplayer team leads) stamps approval across 6 critical domains:
    1. Mass Growth Allowance Check ($\ge 15\%$).
    2. Energy Balance & Eclipse Battery Survival Check.
    3. Pointing Budget Compatibility ($\theta_{\text{adcs}} \le \theta_{\text{sensor}}$).
    4. Fairing Volume Enclosure Check.
    5. Link Margin Threshold ($\ge 3.0\text{ dB}$).
    6. CapEx Budget Ceiling Compliance.
* **Information Hierarchy:**
  1. Overall Flight Readiness Status Banner (`GO FOR FLIGHT` or `NO-GO: 2 VIOLATIONS DETECTED`).
  2. Domain Sign-Off cards with detailed diagnostic traces.
  3. Multi-seat team sign-off status indicators.
* **Error State:** Clicking any `NO-GO` card directly deep-links the player back to the exact subsystem studio screen that needs corrective adjustment.

---

### SCREEN 13: Launch Simulation & Staging Visualizer
* **Layout:** Fullscreen vertical telemetry split-screen: Left: 3D rocket ascent trajectory curve over Earth horizon. Right: Launch vehicle telemetry console (Altitude, Velocity, Dynamic Pressure Max-Q, Stage Separation).
* **Navigation:** Time progression slider; `[ABORT LAUNCH]` button.
* **Main Interactions:**
  * Watch rocket stage separation, fairing jettison, and spacecraft separation events.
  * Real-time acoustic and vibrational $g$-load stress gauge on spacecraft structure.
* **Information Hierarchy:**
  1. Central Ascent Trajectory Vector.
  2. Acceleration Gauge ($g$-load vs. spacecraft structural yield limit).
  3. Staging Events Log (`T+00:02:30 Stage 1 MECO`, `T+00:03:05 Fairing Jettison`).
* **Audio-Visual Effects:** Low-frequency engine rumble sound, camera shake scaling with dynamic pressure ($Q$), clean mechanical separation chime.

---

### SCREEN 14: Mission Control Center (Flight Operations Directorate)
* **Layout:** The primary simulation gameplay console. High-density 3-column command center:
  * Left Column (300px): Spacecraft Subsystem Health Status & Telecommand Sequencer.
  * Center Column (Fluid): 3D Orbit Tracker & Ground Station Line-of-Sight (LOS) Visualizer.
  * Right Column (320px): Live Telemetry Strip Charts & Science Data Yield Counter.
  * Bottom Bar: Time-Warp Speed Bar (`1x`, `10x`, `100x`, `1000x`, `PAUSE`).
* **Navigation:** Quick-switch tabs between `SUBSYSTEM HEALTH`, `SCIENCE SCHEDULE`, `PAYLOAD IMAGING`, `GROUND NETWORK`.
* **Main Interactions:**
  * Toggle time warp speed.
  * Click instrument to toggle operational modes (`STANDBY`, `SURVEY`, `CALIBRATE`).
  * Click ground station when in range to initiate manual or automated data downlink dump.
* **Information Hierarchy:**
  1. Central Orbital Viewport with Terminator Line (day/night shadow boundary).
  2. Ground Station AOS (Acquisition of Signal) countdown timer.
  3. Master Caution and Warning Annunciator Panel.
* **Data Displayed:** Mission Elapsed Time (MET), total science data collected (GB), battery SoC %, bus temperature.

---

### SCREEN 15: Real-Time Spacecraft Telemetry (The Strip-Chart Vault)
* **Layout:** Multi-channel real-time scrolling strip-chart oscilloscope display.
* **Navigation:** Channel toggles (`Bus Voltage`, `Battery DoD`, `Solar Generation`, `Rx/Tx Bitrate`, `Temperature`, `Reaction Wheel RPM`).
* **Main Interactions:**
  * Zoom and pan historical telemetry timelines.
  * Place measurement cursors to inspect specific event timestamps (e.g., exact minute of eclipse entry).
* **Information Hierarchy:**
  1. 4 synchronized time-series graphs with nominal/caution/warning threshold bands.
  2. Instantaneous numerical readout with standard deviation and peak metrics.
* **Visual Polish:** High-contrast neon traces with subtle grid reticles, updated synchronously with the simulation clock.

---

### SCREEN 16: Mission Event & Anomaly Management
* **Layout:** Modal alarm overlay that pauses high time-warp to $1\times$ and displays an urgent JPL Anomaly Resolution Card.
* **Navigation:** `[DIAGNOSE TELEMETRY]`, `[EXECUTE CONTINGENCY SCRIPT]`, `[ENTER SAFE MODE]`.
* **Main Interactions:**
  * Interactive Fault Tree diagnosis: player reviews erratic telemetry symptoms to pinpoint root cause (e.g., Solar Flare vs. Battery Cell Degradation vs. Reaction Wheel Saturation).
  * Action checklist with a 60-second execution countdown timer before irreversible safe-mode trigger.
* **Information Hierarchy:**
  1. Master Warning Klaxon and Alarm Title (`ANOMALY: SOLAR PROTON EVENT DETECTED`).
  2. Telemetry Deviation Summary (e.g., `Array efficiency -18%`, `Single-Event Upsets: 4`).
  3. Recommended Aerospace Remediation Options with success probabilities.
* **Audio Feedback:** Authentic dual-tone master caution beep with synthesizer alert voice.

---

### SCREEN 17: Mission Results (The Flight Dossier)
* **Layout:** Fullscreen celebration and debriefing presentation screen.
* **Navigation:** `[VIEW ENGINEERING AUDIT]`, `[SUBMIT TO LEADERBOARD]`, `[DESIGN ITERATION V2]`, `[MAIN MENU]`.
* **Main Interactions:**
  * Interactive radar chart comparing achieved performance across 6 axes (Science Yield, Cost Efficiency, Margin Compliance, Reliability, Duration, Trajectory Accuracy).
  * One-click "Export Flight Certificate (PNG/PDF)".
* **Information Hierarchy:**
  1. Mission Outcome Badge (`MISSION SUCCESS` in emerald or `MISSION PARTIAL / FAILED` in amber/red).
  2. Composite Score (e.g., `872 / 1000 - GRADE: A (FLIGHT QUALIFIED)`).
  3. Key Achievements Unlocked with glowing badges.
* **Visual Polish:** Subtle particle confetti on mission success; solemn telemetry static effect on failure.

---

### SCREEN 18: Engineering Performance Report (The Post-Mortem Audit)
* **Layout:** Deep technical breakdown document. Left: Subsystem lifecycle wear-and-tear grades. Right: Financial audit, propellant remaining, and science ROI analysis.
* **Navigation:** `[EXPORT JSON REPORT]`, `[CLONE DESIGN FOR RETRY]`.
* **Main Interactions:**
  * Expandable post-mortem accordions detailing exact root causes of any in-flight anomalies or failures.
  * Side-by-side comparison of planned design margins vs. actual in-flight telemetry extremes.
* **Information Hierarchy:**
  1. Executive Summary & Engineering Integrity Rating (EIR).
  2. Subsystem Reliability Degradation Table (Initial Health vs. End of Life Health).
  3. Cost-per-Megabyte Metric ($\$/\text{MB}$ science downlinked).
* **Educational Value:** Explicitly explains what engineering changes would turn a 700-point mission into a 950-point mission.

---

### SCREEN 19: Global Leaderboard & Mission Hall of Fame
* **Layout:** High-density tournament table with scenario filter tabs.
* **Navigation:** Scenario tabs (`Ignis Sentinel`, `Selene Core`, `Ares Echo`), time filter (`All-Time`, `This Week`, `Daily Challenge`).
* **Main Interactions:**
  * Click any leaderboard entry to load their spacecraft architecture in read-only 3D CAD inspector to learn from their design.
  * Filter by "Cost Leader" or "Maximum Science Yield".
* **Information Hierarchy:**
  1. Rank, Player Callsign, Certification Badge, Spacecraft Name.
  2. Total Science Yield (GB), Mission CapEx (\$M), Margin Rating, Final EIR Score.
* **Data Displayed:** Top 50 global records with verified hash integrity stamps.

---

### SCREEN 20: Multiplayer Collaboration Interface (The NASA CDF Team Room)
* **Layout:** 4-seat mission operations control room layout:
  * Top quadrant: Systems & Launch Director Seat.
  * Bottom-left: Science Principal Investigator Seat.
  * Bottom-center: Power & Thermal Lead Seat.
  * Bottom-right: Flight Operations & Comms Specialist Seat.
* **Navigation:** `[CLAIM SEAT]`, `[TEAM VOICE/CHAT]`, `[VOTE FOR FLIGHT READY]`.
* **Main Interactions:**
  * Real-time multi-cursor and subsystem locking: when the Science Lead selects an instrument, the Power Lead's power gauge dynamically ripples in real time.
  * "Request Subsystem Margin" ping button (e.g., Science PI pings Power Lead: "Need +50 W for Radar pass").
  * Team FRR consensus vote: all 4 leads must press and hold their certification key to authorize launch.
* **Information Hierarchy:**
  1. 4 Seat Status cards with latency indicators, active user callsigns, and subsystem control locks.
  2. Shared Central 3D Spacecraft Canvas and Live Telemetry Bar.
  3. Integrated Mission Control Chat & Event Log.
* **Network Synchronization:** Seamless WebSocket sync (<50ms state updates) with instant graceful fallback to single-player seat-switcher mode if a teammate disconnects.

---

## 3. DESIGN SYSTEM TOKENS REFERENCE

The complete design tokens schema has been initialized in:
[`code/lucy/design_system/tokens.json`](file:///Users/subham/.gemini/antigravity/scratch/code/lucy/design_system/tokens.json)

```json
{
  "colors": {
    "background_primary": "#0A0D14",
    "background_surface": "#1B263B",
    "text_primary": "#F8FAFC",
    "telemetry_nominal": "#10B981",
    "telemetry_caution": "#F59E0B",
    "telemetry_warning": "#EF4444",
    "subsystem_payload": "#8B5CF6",
    "subsystem_power": "#FACC15"
  },
  "typography": {
    "font_display": "'Space Grotesk', sans-serif",
    "font_mono": "'JetBrains Mono', monospace"
  }
}
```

---

## 4. UI/UX SPECIFICATION SUMMARY

This design specification provides:
1. **Complete 20-Screen Architectural Coverage:** From initial gateway to multiplayer concurrent engineering and post-mission failure audits.
2. **Professional Aerospace Immersion:** Inspired by genuine flight control software rather than generic SaaS templates.
3. **Ergonomic Information Density:** Clean data tables, interactive 3D WebGL components, and real-time margin feedback.
4. **Zero-Ambiguity Engineering Feedback:** Color-coded telemetry, threshold lines, and educational tooltips on every aerospace parameter.
