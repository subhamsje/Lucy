# GAMEPLAY SYSTEMS DESIGN DOCUMENT: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Author:** Senior Game Systems Designer & Spacecraft Systems Engineer  
**Target Project:** `code/lucy` (/Users/subham/.gemini/antigravity/scratch/code/lucy)  
**Core Motto:** *Every Gram Has a Consequence; Every Watt Demands an Orbit.*

---

## 1. GAMEPLAY ARCHITECTURE & SYSTEM OVERVIEW

The game is structured as a **Concurrent Engineering Simulation** split into two interlocking loops:
1. **Design & Integration Loop (Phase A/B/C/D):** Turn-less, reactive sandbox where player actions update coupled physical and financial margins in real time.
2. **Operations & Telemetry Loop (Phase E):** Time-warped, discrete-event orbital simulation where physical laws and operational schedules dictate telemetry yield, component degradation, and anomaly survival.

```
       ┌─────────────────────────────────────────────────────────────┐
       │             PHASE 1: MISSION DIRECTIVE & ORBIT              │
       │    Select Target Body • Set Primary & Secondary Science     │
       │    Choose Orbit (LEO, SSO, Molniya, Lunar Polar, Mars)      │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             PHASE 2: CONCURRENT SPACECRAFT CAD              │
       │  Payload (Sensors) ──> Bus Sizing (EPS, ADCS, TCS, C&DH)    │
       │             Propulsion ──> Structural Envelopes             │
       │      *Continuous Live Feedback via AIAA Margin Gauges*      │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             PHASE 3: LAUNCH INTEGRATION & REVIEW            │
       │   Select Launch Vehicle Tier • Fairing & Mass Margin Gate   │
       │   Flight Readiness Review (FRR) Certification Clearance     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             PHASE 4: FLIGHT OPERATIONS SIMULATION           │
       │  Time-Warp Engine (1x - 1000x) • Sunlit / Eclipse Cycles    │
       │  Instrument Duty Cycling • Ground Station Pass Downlinks    │
       │  Dynamic Anomalies & Spacecraft Safe-Mode Contingencies     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             PHASE 5: POST-FLIGHT DOSSIER & DEBRIEF          │
       │  Science Yield Scored • Component Health • Cost ROI         │
       │  Root Cause Failure Analysis • Engineering Badges & Certs   │
       └─────────────────────────────────────────────────────────────┘
```

---

## 2. DEEP SYSTEM MECHANICS SPECIFICATION (THE 15 FOUNDATIONAL SYSTEMS)

---

### MECHANIC 1: Player Progression & Aerospace Career Tiers

#### What the Player Does:
Players advance through an aerospace career path across 4 Certification Ranks:
1. **Junior Payload Engineer:** Fixed bus templates; selects scientific sensors, balances power draw, and manages data downlink for simple CubeSat missions.
2. **Subsystem Lead (Power/Thermal/ADCS):** Unlocks custom bus fabrication, battery chemistry selection, radiator sizing, and reaction wheel specification.
3. **Mission Systems Engineer (Flight Director):** Unlocks planetary transfer trajectories, deep-space communication delays, launch vehicle contract negotiations, and multi-instrument duty scheduling.
4. **Director of Space Flight (Master Architect):** Unlocks Sandbox Mode, custom anomaly injection, custom mission builder, and 4-player cooperative NASA CDF rooms.

#### What the Game Calculates:
* **Engineering Integrity Rating (EIR):** A composite score computed across completed missions:
  $$\text{EIR} = 0.40 \cdot S_{\text{science}} + 0.30 \cdot M_{\text{margin\_compliance}} + 0.20 \cdot B_{\text{budget\_efficiency}} + 0.10 \cdot R_{\text{reliability}}$$
* Unlocks are gated strictly by **Engineering Integrity**, never by grind time or micro-actions.

#### What Changes in the Simulation:
Advancing rank introduces realistic aerospace friction:
* At higher ranks, component tolerances become tighter, launch vehicle mass margins are audited more strictly (AIAA S-120 standard drops from 30% allowance to 15%), and environmental perturbations ($J_2$ drag, solar radiation pressure, deep-space cosmic radiation) are simulated with greater fidelity.

#### What Feedback the Player Receives:
* Career Dossier showing mission flight logs, launch badges, failure post-mortems, and certification stamps.
* Audible flight director radio callouts ("Systems certified for Flight Readiness Review").

#### Educational Lesson:
Teaches how flight heritage and NASA Technology Readiness Levels (TRL 1 through TRL 9) govern real aerospace engineering: experimental parts carry lower initial cost or higher theoretical output, but pose higher risk of in-flight failure.

---

### MECHANIC 2: Mission Selection & Scenario Directives

#### What the Player Does:
Selects from a roster of realistic mission scenarios or creates a custom charter:
* **Scenario A: "Ignis Sentinel" (Earth Observation - LEO/SSO):** High-resolution wildfire infrared tracking. Tight ground station passes, heavy data generation, frequent eclipses.
* **Scenario B: "Aura Helios" (Space Weather - Lagrange L1 / GEO):** Continuous solar observation, intense cosmic radiation, zero eclipse, continuous high-gain antenna tracking.
* **Scenario C: "Selene Sub-Surface" (Lunar South Pole Prospector):** Lunar polar orbit, search for water ice in permanently shadowed craters, extreme thermal gradients ($40\text{ K}$ to $390\text{ K}$), radar altimeter high peak power.
* **Scenario D: "Ares Relay" (Mars Atmospheric Scout):** Interplanetary transfer, high $\Delta v$ insertion, communication round-trip latency of $4\text{ to }22\text{ minutes}$, autonomous safe-mode operation required.

#### What the Game Calculates:
* Ambient orbital parameters: solar irradiance flux $S = S_0 (r_E / r)^2$, local gravity parameter $\mu$, planetary occultation geometry, and radiation dose rate.
* Minimum Science Threshold ($D_{\text{min}}$, in Gigabits of valid telemetry) and hard Budget Cap ($\$M$).

#### What Changes in the Simulation:
* Dynamic orbital background environment: solar panel output is adjusted for distance to the Sun (e.g., at Mars, solar flux drops to $\approx 589\text{ W/m}^2$, cutting solar array efficiency by more than half).

#### What Feedback the Player Receives:
* Mission Charter Dossier displaying primary science objectives, secondary stretch goals, financial budget ceiling, and orbital target profile.

#### Educational Lesson:
Spacecraft are not generic; every satellite is a bespoke instrument platform tuned specifically to its target orbital environment.

---

### MECHANIC 3: Difficulty Levels & Simulation Realism

#### What the Player Does:
Chooses between three operational paradigms:
1. **Flight Cadet (Assisted):** Auto-calculates structural mass; warning popups prevent invalid launches; simplified 2-state thermal model; zero random orbital anomalies.
2. **Mission Specialist (Standard Systems):** Manual mass margins (AIAA S-120); full thermal equilibrium equations; battery depth-of-discharge degradation simulated; deterministic anomaly events.
3. **Flight Director (Hardcore Realism):** Stochastic solar storm anomalies; component thermal shock failures; RF link degradation during atmospheric rain fade; launch vehicle vibration load tests; strict mission abort penalties.

#### What the Game Calculates:
* Error margins, component failure probabilities, and penalty severity for margin violations.

#### What Changes in the Simulation:
Higher difficulty reduces allowable engineering tolerances:
$$\text{Margin}_{\text{safety}} = \begin{cases} 30\% & \text{Cadet} \\ 15\% & \text{Specialist} \\ 5\% & \text{Flight Director} \end{cases}$$

#### What Feedback the Player Receives:
* UI theme shifts from educational green highlights to austere, high-contrast NASA/JPL telemetry dark-mode terminal.

#### Educational Lesson:
Demonstrates the cost of reliability: higher reliability and tighter margins require either massive budgets or conservative, heavier spacecraft components.

---

### MECHANIC 4: Mission Objectives & The Science Scoring Engine

#### What the Player Does:
Selects Primary and Secondary scientific objectives:
* Primary Objective: e.g., "Map $80\%$ of equatorial fire zones at $< 15\text{ m}$ Ground Sample Distance (GSD) over a 90-day operational phase."
* Secondary Objectives: e.g., "Downlink continuous space weather magnetosphere telemetry," or "Achieve $> 95\%$ battery state-of-health at end of mission."

#### What the Game Calculates:
* **Science Return Rate ($S_R$):**
  $$S_R = \sum_{k} \left[ \text{DataVolume}_k \cdot \text{QualityFactor}(\text{GSD}, \text{PointingError}) \cdot \text{TargetVisibilityFactor} \right]$$
* **Ground Resolution vs. Altitude:**
  $$\text{GSD} = \frac{\text{PixelPitch} \cdot h}{f_{\text{focal\_length}}}$$
  If altitude $h$ is too high, GSD fails the threshold and observations yield $0$ science points.

#### What Changes in the Simulation:
* Scientific value accumulates only when:
  1. The instrument is powered on.
  2. The target zone is within the sensor's field of view and lighting conditions.
  3. Spacecraft attitude jitter is below the sensor's maximum allowable jitter.
  4. Data has been successfully downlinked to a ground station (un-downlinked data in storage awards 0 points).

#### What Feedback the Player Receives:
* Live Science Yield Counter on the mission operations HUD; animated "Data Packet Downlinked" telemetry pulses.

#### Educational Lesson:
Data collection is useless without downlink; taking beautiful images in space means nothing if your transmitter cannot beam them to Earth before memory fills up.

---

### MECHANIC 5 & 6: Spacecraft Assembly & Component Configuration

#### What the Player Does:
In the **Spacecraft CAD & Systems Studio**, players select and configure components across 8 subsystems:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SPACECRAFT COMPONENT SELECTION MATRIX                │
├─────────────────┬──────────────────────────────────────────────────────┤
│ Subsystem       │ Available Component Choices                          │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 1. Payload      │ Optical Multispectral Camera, Synthetic Aperture     │
│                 │ Radar (SAR), IR Sounder, Magnetometer, Altimeter    │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 2. Electrical   │ Silicon vs. GaAs Triple-Junction Solar Panels;       │
│    Power (EPS)  │ Body-Mounted vs. Deployable Tracking Wings;          │
│                 │ Li-ion vs. Lithium-Sulfur Battery Packs (Wh capacity)│
├─────────────────┼──────────────────────────────────────────────────────┤
│ 3. Propulsion   │ Cold Gas Thruster, Hydrazine Monopropellant,        │
│                 │ Bipropellant MMH/NTO, Xenon Hall-Effect Ion Thruster │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 4. ADCS         │ Coarse Sun Sensors, Star Trackers (High Precision),  │
│                 │ Magnetorquers (LEO only), Reaction Wheels (0.1–2 Nms)│
├─────────────────┼──────────────────────────────────────────────────────┤
│ 5. TT&C Comms   │ S-Band Patch (Omni), X-Band Horn, Ka-Band Steerable  │
│                 │ High-Gain Dish; RF Power Amplifiers (2W to 50W)      │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 6. Thermal      │ Passive MLI Blankets, Surface Radiators (m²),       │
│                 │ Active Heat Pipes, Internal Survival Heaters         │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 7. C&DH         │ Rad-Tolerant Microprocessor, Solid-State Storage     │
│                 │ Capacity (64 GB to 2 TB)                             │
├─────────────────┼──────────────────────────────────────────────────────┤
│ 8. Structure    │ Aluminum Honeycomb vs. Carbon Fiber (CFRP) Bus       │
└─────────────────┴──────────────────────────────────────────────────────┘
```

#### What the Game Calculates:
* **Coupled Mass Compounding:**
  $$m_{\text{dry}} = \sum m_{\text{payload}} + \sum m_{\text{subsystems}} + m_{\text{structure}}$$
  $$m_{\text{structure}} = 0.22 \cdot \left( \sum m_{\text{payload}} + \sum m_{\text{subsystems}} \right)$$
* **Coupled Power Draw Balance:**
  $$P_{\text{total\_load}} = P_{\text{bus\_quiescent}} + \sum (P_{\text{sensor}} \cdot \text{DutyCycle}) + P_{\text{transmitter\_RF}} + P_{\text{heaters}}$$
* **Thermal Equilibrium:**
  $$T_{\text{equilibrium}} = \left( \frac{Q_{\text{solar}} + Q_{\text{albedo}} + P_{\text{total\_load}}}{\epsilon \sigma A_{\text{radiator}}} \right)^{1/4}$$

#### What Changes in the Simulation:
* 3D Satellite Model updates procedurally: adding larger solar wings expands the physical mesh; adding a high-gain dish attaches a steerable parabolic dish to the bus.
* Structural mass increases automatically as heavier instruments are installed.

#### What Feedback the Player Receives:
* **The AIAA Margin Dashboard:**
  * Mass Margin Gauge: `Nominal Dry Mass + 20% MGA <= Mass Cap` (Green / Amber / Red).
  * Power Margin Gauge: `Day Generation >= Night Consumption / Discharge Efficiency`.
  * Thermal Status: Estimated operating temperature display with blue (cold risk), green (nominal), and red (overheating) indicators.

#### Educational Lesson:
Teaches the fundamental aerospace reality of **Mass Compounding**: adding a $10\text{ kg}$ sensor requires more structure to hold it, more battery to power it, more radiator to cool it, and more propellant to move it—turning a $10\text{ kg}$ addition into a $25\text{ kg}$ gross dry mass penalty.

---

### MECHANIC 7: Launch Vehicle Selection & Fairing Envelope Integration

#### What the Player Does:
Selects an orbital launch provider from 4 realistic launcher archetypes:
1. **Micro-Launcher (e.g., Rocket Lab Electron class):** Low cost (\$7M), strict payload limit ($250\text{ kg}$ to LEO), narrow fairing ($1.2\text{ m}$ diameter).
2. **ESPA Rideshare Slot (e.g., Falcon 9 Transporter):** Very low cost (\$2.5M), high capacity ($450\text{ kg}$), but zero orbit choice (fixed $525\text{ km}$ SSO at 10:30 AM descending node).
3. **Dedicated Medium-Lift (e.g., Falcon 9 / Vulcan class):** Standard cost (\$65M), massive payload ($12,000\text{ kg}$ to SSO), generous $4.6\text{ m}$ fairing.
4. **Heavy Deep-Space Lift (e.g., Ariane 64 class):** High cost (\$130M), capable of direct interplanetary injection ($C_3 > 25\text{ km}^2/\text{s}^2$).

#### What the Game Calculates:
* **Fairing Volumetric Enclosure Check:**
  $$\text{Stowed Diameter} \le D_{\text{fairing}} \quad \text{and} \quad \text{Stowed Height} \le H_{\text{fairing}}$$
* **Launcher Lift Curve Margin:**
  $$\text{Margin}_{\text{lift}} = \frac{M_{\text{launcher\_capacity}}(h, i) - m_{\text{wet}}}{M_{\text{launcher\_capacity}}(h, i)} \times 100\% \ge 15\%$$

#### What Changes in the Simulation:
* If mass exceeds capacity, launch fails on the pad.
* If stowed geometry exceeds fairing volume, integration is rejected by the range safety officer.

#### What Feedback the Player Receives:
* **Fairing Fit Visualizer:** 3D wireframe cross-section showing the folded spacecraft inside the rocket nose cone. Components clipping the red fairing line turn red.
* Launch Cost automatically debits the mission budget ledger.

#### Educational Lesson:
Teaches the trade-off between **Dedicated Launches** (expensive, custom orbit) vs. **Rideshare Launches** (affordable, but forces the spacecraft into a non-optimal orbit that requires onboard propulsion to correct).

---

### MECHANIC 8: Orbit Selection & Astrodynamics Parameters

#### What the Player Does:
Configures the orbital profile:
* **Altitude ($h$, in $km$):** e.g., $350\text{ km}$ (high resolution, high drag decay) vs. $800\text{ km}$ (lower resolution, zero drag, high space radiation).
* **Inclination ($i$, in degrees):** Equatorial ($0^\circ$), Mid-latitude ($28.5^\circ$), Sun-Synchronous ($97.8^\circ$), Polar ($90^\circ$).
* **Eccentricity ($e$):** Circular ($e = 0.0$) vs. Elliptical ($e > 0.3$).

#### What the Game Calculates:
* Orbital Period: $T = 2\pi \sqrt{\frac{(R_E + h)^3}{\mu_E}}$.
* Eclipse Duration:
  $$T_{\text{eclipse}} = \frac{T}{\pi} \arcsin\left(\frac{R_E}{R_E + h}\right) \quad (\text{for zero beta angle})$$
* Atmospheric Lifetime & Stationkeeping Fuel:
  $$\Delta v_{\text{drag/yr}} = \pi \cdot \left(\frac{C_D A}{m_{\text{wet}}}\right) \cdot \rho(h) \cdot v_{\text{orbit}}^2 \cdot \text{SecondsPerYear}$$

#### What Changes in the Simulation:
* The 3D orbital track and 2D ground track map update dynamically.
* Eclipses calculate solar array illumination state (1 = 100% Sun, 0 = Umbra/Shadow).

#### What Feedback the Player Receives:
* Ground Track visualization showing swath coverage lines over Earth geography.
* Orbit Summary Card showing: Orbit Period, Eclipses per Day, Daily Stationkeeping $\Delta v$, Ground Station Pass Frequency.

#### Educational Lesson:
Teaches why Sun-Synchronous Orbits (SSO) are ubiquitous for imaging satellites: nodal precession from Earth's oblateness ($J_2$) matches Earth's orbital rate around the Sun, keeping lighting angles constant for Earth observation.

---

### MECHANIC 9: Resource Management & Coupled Budget Telemetry

#### What the Player Does:
Allocates and balances 6 critical aerospace resource pools:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 6 SYSTEM RESOURCE POOLS                     │
├───────────────────┬────────────────────────────────────────────────────┤
│ Resource Pool     │ Governing Subsystem & Balancing Knobs              │
├───────────────────┼────────────────────────────────────────────────────┤
│ 1. Mass (kg)      │ Payload choice vs. Bus Structure vs. Propellant    │
├───────────────────┼────────────────────────────────────────────────────┤
│ 2. Energy (Wh)    │ Array Area + Battery Sizing vs. Sensor Duty-Cycle  │
├───────────────────┼────────────────────────────────────────────────────┤
│ 3. Thermal (W)    │ Waste heat vs. Radiator Area & Survival Heaters    │
├───────────────────┼────────────────────────────────────────────────────┤
│ 4. Data (Gbit)    │ Generation Rate vs. SSR Capacity vs. Downlink Rate │
├───────────────────┼────────────────────────────────────────────────────┤
│ 5. Delta-V (m/s)  │ Fuel Mass & Isp vs. Stationkeeping & Orbit Raising │
├───────────────────┼────────────────────────────────────────────────────┤
│ 6. Budget ($M)    │ Component Tiers + Launcher Class + Ground Ops      │
└───────────────────┴────────────────────────────────────────────────────┘
```

#### What the Game Calculates:
* In real time, any slider adjustment calculates downstream impacts across all 6 pools:
  $$\text{Increase Sensor Sampling Rate} \implies \text{Data Rate} \uparrow \implies \text{Transmitter RF Power} \uparrow \implies \text{Power Draw} \uparrow \implies \text{Battery Mass} \uparrow \implies \text{Structure Mass} \uparrow \implies \text{Launcher Margin} \downarrow$$

#### What Changes in the Simulation:
* The resource meters respond instantaneously. If any resource crosses $100\%$ capacity or violates safety margins, an audible warning chime sounds.

#### What Feedback the Player Receives:
* **The "Cascade Inspector":** Hovering over any component highlights all coupled resource impacts in green (positive margin) or red (negative penalty).

#### Educational Lesson:
There are no independent variables in aerospace systems engineering. Every subsystem decision is a negotiation with all other subsystems.

---

### MECHANIC 10: Mission Simulation & Time-Warp Flight Operations

#### What the Player Does:
Once design is certified, the player hits **"INITIALIZE FLIGHT OPS"**:
* Controls time-warp speed: `1x` (real-time telemetry), `10x`, `100x`, `1000x` (1 orbit = 5 seconds).
* Operates the **Spacecraft Command Console**:
  * Set instrument operational modes (`STANDBY`, `SURVEY`, `CALIBRATE`, `SLEW`).
  * Schedule ground station contact passes.
  * Execute orbit correction burns when drag decays the orbital altitude.

#### What the Game Calculates:
* Discrete time-step orbital propagation ($\Delta t = 1.0\text{ s}$ scaled by warp multiplier).
* Instantaneous battery state-of-charge:
  $$E_{\text{batt}}(t + \Delta t) = E_{\text{batt}}(t) + \left[ P_{\text{gen}}(t) - P_{\text{load}}(t) \right] \cdot \Delta t$$
* Downlink data transfer during ground station pass windows:
  $$D_{\text{buffer}}(t + \Delta t) = D_{\text{buffer}}(t) - R_{\text{downlink}} \cdot \Delta t$$

#### What Changes in the Simulation:
* The 3D viewport shows the satellite orbiting Earth, entering the shadow cone (solar panels stop glowing; night lights illuminate Earth below).
* Telemetry strip charts stream real-time voltage, temperature, buffer percentage, and reaction wheel RPM.

#### What Feedback the Player Receives:
* Real-time flight graphs: Voltage line chart, Thermal temperature curve, Data buffer gauge, Ground station LOS (Line of Sight) countdown timer.
* Mission Control voice synthesizers reporting pass acquisitions ("Acquisition of Signal at Svalbard Station").

#### Educational Lesson:
Teaches real flight operations: ground stations only have line-of-sight for 6 to 10 minutes per 90-minute orbit. All observation data must be stored onboard and dumped rapidly during those brief windows.

---

### MECHANIC 11: Unexpected Events & Space Environment Anomalies

#### What the Player Does:
Responds to active flight emergencies during simulation:
1. **Solar Particle Event (Coronal Mass Ejection):** High-energy protons strike the spacecraft.
   * *Player action:* Orient spacecraft into safe attitude; shut down unshielded payload electronics; absorb penalty in temporary science blackout.
2. **Reaction Wheel Saturation:** Wheels reach maximum $6000\text{ RPM}$ from environmental disturbance torques.
   * *Player action:* Fire thrusters or activate magnetorquers during an orbit pass to dump momentum; failure to do so causes loss of pointing lock.
3. **Severe Eclipse Battery Degradation:** Battery cell fails; capacity drops $20\%$.
   * *Player action:* Modify instrument duty cycle; disable secondary payload to prevent brownout during shadow transit.
4. **Micrometeorite Impact on Solar Wing:** Array area reduced by $12\%$.
   * *Player action:* Rebalance daily power budget; reschedule high-power SAR radar passes.

#### What the Game Calculates:
* Probability models based on Space Environment Indices (Kp index, Solar Activity cycle, Orbit Altitude).
* Subsystem degradation rates and immediate thermal/electrical equilibrium shifts.

#### What Changes in the Simulation:
* Simulation drops out of high time-warp back to `1x` automatically.
* Master Alarm klaxon sounds; telemetry graphs flash amber/red.

#### What Feedback the Player Receives:
* **Anomaly Diagnostic Card:** Displays telemetry readings, root cause indicators, and a timer to execute corrective action before safe-mode timeout.

#### Educational Lesson:
Space is a hostile environment. Engineering margins exist precisely to survive unforeseen anomalies without mission-terminating consequences.

---

### MECHANIC 12: Mission Failure, Safe Modes & Recovery

#### What the Player Does:
If an engineering threshold is completely violated:
* The spacecraft automatically triggers **SAFE MODE**:
  * Payload powered off completely.
  * Spacecraft sun-points arrays to maintain survival charge.
  * TT&C switches to low-rate S-band omnidirectional antenna.
* The player must execute a **Flight Recovery Sequence**:
  1. Diagnose telemetry error (e.g., thermal overheat, battery brownout, or reaction wheel desaturation).
  2. Upload corrective command sequence during the next ground station pass.
  3. Re-commission subsystems sequentially.

#### What the Game Calculates:
* **Failure States:**
  * *Catastrophic:* Battery drained to $0\%$ in eclipse $\implies$ Spacecraft freezes, loss of command receiver $\implies$ **Mission Lost**.
  * *Structural:* Launch vehicle static acceleration exceeds yield stress $\implies$ Spacecraft shatters during stage 1 max-Q $\implies$ **Mission Lost**.
  * *Degraded:* Thermal limit exceeded $\implies$ Optical sensor focal plane degraded $\implies$ Science quality multiplier reduced by $50\%$.

#### What Changes in the Simulation:
* Safe-mode locks out science accumulation until resolved.
* Mission clock continues running; ground pass contacts must be used for emergency recovery instead of scientific downlink.

#### What Feedback the Player Receives:
* Visual screen shake and warning overlays during launch structural failures.
* Post-Mortem Failure Investigation Report: Displays the exact second and formula that caused mission termination.

#### Educational Lesson:
Teaches the aerospace engineering principle of **FDIR (Fault Detection, Isolation, and Recovery)** and the role of autonomous onboard safe-modes.

---

### MECHANIC 13: Scoring Engine, Engineering Rubrics & Achievements

#### What the Player Does:
Completes the operational phase (e.g., 90 days, 180 days, or 1 year) and reviews the final **Mission Debrief**.

#### What the Game Calculates:
* **The Mission Success Score ($0 - 1000$ points):**
  $$\text{Score} = \underbrace{S_{\text{science}} \cdot 400}_{\text{Objective Fulfillment}} + \underbrace{\left(\frac{\text{Budget}_{\text{cap}} - \text{Cost}}{\text{Budget}_{\text{cap}}}\right) \cdot 200}_{\text{Fiscal Responsibility}} + \underbrace{\text{Margin}_{\text{compliance}} \cdot 200}_{\text{Engineering Rigor}} + \underbrace{\text{Reliability}_{\text{health}} \cdot 200}_{\text{Hardware Survival}}$$
* **Achievement Badges:**
  * *Ghost in the Machine:* Complete a mission using less than $50\%$ of allowable budget.
  * *Razor's Edge:* Successfully complete a mission with less than $3\%$ mass margin remaining.
  * *Sun-Gazer:* Maintain $100\%$ solar array illumination for an entire 90-day mission using dawn-dusk SSO.
  * *Deep Space Survivor:* Survive a major solar storm without triggering battery brownout.

#### What Changes in the Simulation:
* Generates a permanent **Mission Dossier PDF/Image** with spacecraft blueprint, orbit track, science yield graphs, and flight certification seal.

#### What Feedback the Player Receives:
* Mission Success Ceremony screen with breakdown charts and ranking on the global leaderboard.

#### Educational Lesson:
Reinforces that mission success is not just about raw performance—it is about delivering scientific objectives within cost, schedule, and safety envelopes.

---

### MECHANIC 14: Replayability & Sandbox Systems

#### What the Player Does:
* **Design Iteration Mode:** Instantly clone a completed or failed mission, modify a single subsystem (e.g., swap cold-gas for ion thrusters), and re-simulate to see the differential impact.
* **Sandbox Mode:** Unlocks infinite budget, experimental future propulsion (e.g., Nuclear Thermal Propulsion, Solar Sails), and custom planetary bodies.
* **Daily Engineering Challenge:** A procedurally generated mission scenario with unique constraint combinations (e.g., "Build an Earth observer with under \$15M budget using only rideshare launches").

#### What the Game Calculates:
* Delta-comparisons between Design V1 and Design V2, plotting performance improvements across mass, cost, and science yield.

#### What Changes in the Simulation:
* Players can run side-by-side comparative orbital simulations.

#### What Feedback the Player Receives:
* Comparative radar chart (spider graph) comparing Design Iteration A vs. Design Iteration B across all 6 resource dimensions.

#### Educational Lesson:
Reflects actual Phase-A trade studies conducted in aerospace conceptual design facilities: comparing architecture trade trees to find Pareto-optimal solutions.

---

### MECHANIC 15: Single-Player vs. 4-Player Cooperative Multiplayer Architecture

#### What the Player Does:
* **Single-Player Mode:** The player holds the "Master Console," toggling between Subsystem Tabs (Payload, Power, Thermal, Comms, Launch) with complete omniscient control.
* **4-Player Cooperative Flight Directorate:** Players connect via room code and claim one of 4 specialized aerospace seats:

```
┌────────────────────────────────────────────────────────────────────────┐
│             THE 4-PLAYER CONCURRENT DESIGN FACILITY (CDF)              │
├──────────────────────┬─────────────────────────────────────────────────┤
│ Specialist Role      │ Exclusive Control & Responsibility              │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 1. Systems & Launch  │ Controls total Mass Budget (MGA), Launcher      │
│    Director          │ Selection, Fairing Envelope, and Final Budget   │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 2. Science Principal │ Selects Science Instruments, sets Target Orbit  │
│    Investigator (PI) │ Resolution, and manages Science Yield goals     │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 3. Power & Thermal   │ Configures Solar Arrays, Battery packs (Wh),    │
│    Lead              │ Radiator Surface Area, and Heater allocations   │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 4. Flight Ops &      │ Selects Antenna Band (S/X/Ka), RF Power, Ground │
│    Comms Specialist  │ Station Network, and manages In-Flight Passes   │
└──────────────────────┴─────────────────────────────────────────────────┘
```

#### What the Game Calculates:
* **Live Cross-Role Negotiation Constraints:**
  * When the *Science PI* adds a Synthetic Aperture Radar, the *Power Lead's* panel immediately sounds an amber alarm: `"WARNING: Peak power demand exceeds array capacity by 450 W!"`
  * When the *Power Lead* increases battery capacity to compensate, the *Systems Director's* panel flashes: `"WARNING: Wet mass increased by 65 kg; launch vehicle margin reduced to 2%!"`
  * The *Systems Director* must either approve a launcher upgrade (increasing mission cost by \$40M) or force the *Science PI* to reduce radar duty-cycling.

#### What Changes in the Simulation:
* Changes made by any specialist broadcast via real-time WebSocket state updates to all connected consoles within 50 milliseconds.
* All 4 players must simultaneously click **"FLIGHT READINESS CERTIFIED"** before the mission can proceed to launch.
* During the Flight Operations phase, each player operates their dedicated subsystem panel during flight anomalies.

#### What Feedback the Player Receives:
* Live collaborative presence: player avatars, real-time subsystem locks, interactive chat/ping system on subsystem cards.

#### Educational Lesson:
Directly replicates the collaborative dynamics of the **NASA Jet Propulsion Laboratory Project Design Center (PDC)** and the **ESA Concurrent Design Facility (CDF)**, where real spacecraft are designed through multi-disciplinary negotiation and compromise.

---

## 3. GAMEPLAY BALANCE & COUPLING REFERENCE CHEAT-SHEET

To ensure engineering consistency, the table below defines the strict mathematical consequences of every player design knob:

| Player Action | Immediate Benefit | Direct Engineering Cost / Cascading Consequence |
| :--- | :--- | :--- |
| **Increase Camera Focal Length** | Improves Ground Sample Distance (GSD); higher science score. | Increases lens mass and camera length; requires higher precision ADCS pointing ($<0.02^\circ$); limits fairing fit. |
| **Select Ka-Band Comms** | $10\times$ higher data downlink throughput ($>300\text{ Mbps}$). | Narrow beam requires steerable dish ($+15\text{ kg}$); dish requires fine pointing lock; higher RF amplifier power ($+50\text{ W}$). |
| **Switch from Silicon to GaAs Solar** | Increases cell efficiency from $18\%$ to $29.5\%$; shrinks array area. | $4\times$ component cost; increases financial budget depletion. |
| **Lower Orbit Altitude (800 km $\to$ 400 km)** | Drastically increases sensor resolution and science return. | Massive increase in atmospheric drag; requires $5\times$ more stationkeeping propellant or orbital lifetime drops from 10 years to 6 months. |
| **Choose Low-Cost Rideshare Launch** | Saves up to $\$60\text{M}$ in launch expenses. | Fixed orbit and fixed launch date; zero mission flexibility; requires large onboard $\Delta v$ to reach desired operational orbit. |
| **Add Extra Battery Pack (Wh)** | Extends eclipse survival and allows higher instrument duty cycle. | Heavy mass penalty ($150\text{ Wh/kg}$); eats into launch vehicle margin; requires larger structural bus. |
| **Install Hydrazine Stationkeeping** | High thrust for rapid orbit maneuvers and de-orbit disposal. | Toxic propellant overhead; heavy propellant tanks; lower $I_{\text{sp}} (220\text{ s})$ compared to electric propulsion. |
| **Install Xenon Ion Thruster** | Ultra-high $I_{\text{sp}} (2500\text{ s})$; negligible propellant mass needed. | Ultra-low thrust ($0.05\text{ N}$); requires massive electrical power ($1.5\text{ kW}$); cannot execute fast avoidance maneuvers. |
