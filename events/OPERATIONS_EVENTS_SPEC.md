# FLIGHT OPERATIONS & EVENT-DRIVEN ANOMALY SYSTEM: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Domain:** Spacecraft Flight Operations, Reliability Engineering, Discrete-Event Simulation  
**Target Repository:** `/Users/subham/code/Lucy/events`  
**Core Motto:** *No Blind Failure. Every Anomaly Has an Early-Warning Signature, a Physical Root Cause, and an Engineering Path to Recovery.*

---

## 1. DESIGN PHILOSOPHY & DETERMINISTIC ENGINE ARCHITECTURE

### 1.1 The Anti-Frustration Rule
In real aerospace operations (and in good simulation game design), catastrophic failures rarely happen out of nowhere. They result from **unmitigated margin erosion**—a high battery Depth-of-Discharge (DoD) ignored over 50 orbits, or thermal radiators pointed toward the Sun during observation slews.
* **Deterministic Seeds (`PRNG`):** Every mission simulation takes a 64-bit integer seed (e.g., `seed = 4281920`). Two students with the exact same spacecraft design running the same seed will encounter the exact same environmental perturbations at the exact same simulation second.
* **Early-Warning Telemetry Signatures (The 3-Stage Alert Model):**
  1. **Telemetry Advisory (Green $\to$ Amber):** Subtle trend anomaly (e.g., battery temperature rising $0.4^\circ C/\text{orbit}$).
  2. **Master Caution (Amber):** Threshold crossed (e.g., reaction wheel reached $5500\text{ RPM}$ out of $6000\text{ RPM}$ limit).
  3. **Critical Anomaly (Ruby):** Automated Safe Mode triggered; time-warp drops to $1\times$; player has an action window to diagnose and intervene.

```
       ┌─────────────────────────────────────────────────────────────┐
       │             REPRODUCIBLE EVENT TIMELINE ENGINE              │
       │    PRNG Seed -> Environmental Triggers + Operational Stress │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             TELEMETRY DRIFT & THRESHOLD DETECTOR            │
       │    Monitors: Voltage, Temperature, RPM, Storage, RF Link    │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                │                                           │
                ▼                                           ▼
┌───────────────────────────────┐           ┌───────────────────────────────┐
│     NOMINAL DEGRADATION       │           │   ACUTE ANOMALY EVENT         │
│  Continuous lifecycle aging   │           │  (Solar Storm, Micrometeorite)│
│  (Cell wear, solar dust loss) │           │  Time-Warp Drop to 1x + Alarm │
└───────────────┬───────────────┘           └───────────────┬───────────────┘
                │                                           │
                └─────────────────────┬─────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             FAULT DETECTION, ISOLATION & RECOVERY           │
       │  Player Decisions: Slew Bus, Dump Momentum, Duty-Cycle Cut  │
       │  Autonomous Onboard Safe-Mode Fallback                      │
       └─────────────────────────────────────────────────────────────┘
```

---

## 2. THE 10 DETAILED FLIGHT OPERATIONS ANOMALIES

---

### EVENT 1: Solar Particle Event (Coronal Mass Ejection)

```
       Sun ☉ ═══════► (Proton Flux Wave) ═══════► [Spacecraft Bus]
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
         [Unshielded Payload Electronics]                             [Photovoltaic Solar Cells]
            Single-Event Upsets (SEU)                                  Lattice Displacement Damage
            (Memory Bitflips, CPU Reset)                                (-15% to -25% Power Output)
```

* **Trigger Conditions:** Spacecraft is outside the protective magnetosphere (e.g., interplanetary cruise, Lunar orbit, or high-inclination polar pass) during elevated space weather activity index ($Kp \ge 7$).
* **Probability Model:**
  $$P(\text{CME} \mid t) = 1.0 - \exp\left(-\lambda_{\text{solar}} \cdot \Delta t\right) \quad \text{where } \lambda_{\text{solar}} \propto \text{SolarCyclePhase}$$
* **Affected Subsystems:** `ONBOARD_COMPUTER` (SEUs / bitflips), `SCIENTIFIC_INSTRUMENT` (focal plane noise), `ELECTRICAL_POWER` (solar cell lattice degradation).
* **Resource Impact:** Immediate $15\%\text{--}25\%$ permanent drop in solar array power generation ($P_{\text{gen}}$); transient telemetry corruption.
* **Available Player Decisions:**
  1. *Action A: Command "Survival Safe Attitude":* Slew spacecraft so that the thick structural bus shield faces the incoming solar proton flux vector.
  2. *Action B: Payload Electronic Power-Down:* Temporarily switch high-sensitivity instruments from `ACTIVE` to `DE-ENERGIZED STANDBY`.
  3. *Action C: Hardware Watchdog Memory Scrub:* Initiate an ECC memory scrub cycle on the flight computer.
* **Immediate Consequences:** Science observations blacked out for the duration of the storm ($2\text{ to }6\text{ simulated hours}$).
* **Long-Term Consequences:** Reduced total power generation budget for the rest of the mission, requiring revised instrument duty-cycling.
* **Recovery Options:** Re-commission payloads sequentially once background radiation drops below safe thresholds.
* **Mission Failure Conditions:** Leaving unshielded electronics powered on during peak proton flux causes latchup $\implies$ unrecoverable onboard computer freeze $\implies$ **Mission Lost**.

---

### EVENT 2: Accelerated Battery Depth-of-Discharge Degradation

* **Trigger Conditions:** Player operates spacecraft with regular Depth-of-Discharge (DoD) $> 35\%$ in LEO for more than 40 consecutive orbits.
* **Probability Model:** Deterministic physical wear equation:
  $$\Delta C_{\text{batt}} = C_0 \cdot \beta \cdot \left(\frac{\text{DoD}}{100}\right)^{1.8} \cdot N_{\text{cycles}}$$
* **Affected Subsystems:** `BATTERY` (State of Health $SOH$).
* **Resource Impact:** Maximum energy capacity drops from $750\text{ Wh} \to 520\text{ Wh}$.
* **Available Player Decisions:**
  1. *Action A: Reduce Payload Night Ops:* Forbid high-draw instrument operation during the 35-minute eclipse period.
  2. *Action B: Lower Heaters Setpoint:* Reduce internal survival heaters by $5^\circ C$ to conserve milliamp-hours during shadow transit.
  3. *Action C: Altitude Boost:* Fire thrusters to raise orbit altitude, reducing atmospheric drag and slightly lengthening orbital periods.
* **Immediate Consequences:** Battery Depth-of-Discharge stabilizes within safe limits ($< 25\%$).
* **Long-Term Consequences:** Lower total daily science telemetry output; higher sensitivity to cold eclipse phases.
* **Recovery Options:** Recondition battery cells by executing a slow, controlled top-off charge cycle during a continuous-sunlight orbit arc.
* **Mission Failure Conditions:** Battery voltage drops below minimum bus threshold ($V_{\text{bus}} < 21\text{ V}$) during eclipse $\implies$ low-voltage brownout $\implies$ **Mission Lost**.

---

### EVENT 3: Ground Station Communication Blackout & Link Drop

* **Trigger Conditions:** Spacecraft ground track passes over ground station during intense atmospheric precipitation (rain fade on Ka-band) or during planetary occultation (Moon/Mars backside).
* **Probability Model:** Deterministic geometric line-of-sight calculation combined with local weather attenuation model:
  $$\text{Margin}_{\text{link}} = \left(\frac{E_b}{N_0}\right) - \text{RainAttenuation}(f) < 3.0\text{ dB}$$
* **Affected Subsystems:** `COMMUNICATION_ANTENNA`, `DATA_STORAGE`.
* **Resource Impact:** Downlink data throughput drops from $120\text{ Mbps} \to 0\text{ Mbps}$ for the duration of the pass.
* **Available Player Decisions:**
  1. *Action A: Frequency Band Fallback:* Drop carrier from Ka/X-band down to low-rate S-band (higher penetration, lower bit rate).
  2. *Action B: Buffer Data to SSR:* Store un-downlinked science packets in the onboard Solid-State Recorder and schedule a double-dump on the next station (e.g., Svalbard pass).
  3. *Action C: Ground Network Cross-Booking:* Purchase an emergency pass on a partner ground network (costs $\$45\text{k}$ CapEx).
* **Immediate Consequences:** Science telemetry remains buffered onboard; risk of storage saturation increases if subsequent passes fail.
* **Long-Term Consequences:** Slight delay in scientific data yield scoring.
* **Recovery Options:** Downlink buffered telemetry at maximum bitrate during the next clear sky contact window.
* **Mission Failure Conditions:** Solid-State Recorder fills to $100\%$ capacity; new science observations overwrite old unsent data $\implies$ severe score penalty.

---

### EVENT 4: Optical Sensor Focal-Plane Contamination & Jitter Degradation

* **Trigger Conditions:** Spacecraft executes an orbit-raising thruster burn while the optical camera aperture door is open (plume impingement), or reaction wheel micro-vibrations exceed 15 arcseconds/sec.
* **Probability Model:** Deterministic thruster firing rule and ADCS jitter coupling:
  $$\text{QualityMultiplier} = \max\left(0.1, 1.0 - \frac{\theta_{\text{jitter}}}{20.0}\right)$$
* **Affected Subsystems:** `SCIENTIFIC_INSTRUMENT` (Optical Camera).
* **Resource Impact:** Imagery spatial resolution degrades; Ground Sample Distance effectively worsens from $0.8\text{ m} \to 4.5\text{ m}$.
* **Available Player Decisions:**
  1. *Action A: Camera Focal-Plane Bakeout:* Turn on internal sensor heaters to $45^\circ C$ for 3 orbits to boil off outgassed volatile contaminants.
  2. *Action B: Detune Reaction Wheel RPM:* Shift reaction wheel operating speeds away from the structural resonance frequency (avoiding harmonic jitter).
  3. *Action C: Thruster Retargeting:* Close protective lens cover during propulsion firings.
* **Immediate Consequences:** Camera out of commission for 5 simulated hours during the thermal bakeout cycle.
* **Long-Term Consequences:** Restores $95\%$ of original optical sharpness once bakeout is complete.
* **Recovery Options:** Focal-plane calibration pass over an established ground radiometric calibration target.
* **Mission Failure Conditions:** Permanent lens contamination reduces science value below minimum mission charter threshold $\implies$ **Mission Partial Failure**.

---

### EVENT 5: Reaction Wheel Momentum Saturation

* **Trigger Conditions:** Continuous environmental disturbance torques (aerodynamic drag, solar radiation pressure, gravity gradient) cause reaction wheels to spin up to maximum mechanical speed ($6000\text{ RPM}$).
* **Probability Model:** Continuous angular momentum integration:
  $$H(t) = \int \tau_{\text{disturb}} \, dt \ge H_{\text{max}} \quad (1.5\text{ N}\cdot\text{m}\cdot\text{s})$$
* **Affected Subsystems:** `ATTITUDE_CONTROL`.
* **Resource Impact:** Spacecraft loses 3-axis stabilization capability; starts tumbling at $0.5\text{ deg/sec}$.
* **Available Player Decisions:**
  1. *Action A: Thruster Momentum Dump:* Fire reaction control thrusters (expends $0.15\text{ kg}$ hydrazine or cold gas) to counteract wheel momentum while wheels decelerate.
  2. *Action B: Magnetic Desaturation (LEO Only):* Activate magnetorquer rods to dump momentum against Earth's geomagnetic field (consumes zero propellant, but takes 1.5 orbits).
  3. *Action C: Gravity Gradient Trim:* Adjust spacecraft equilibrium orientation to balance atmospheric drag torques.
* **Immediate Consequences:** Solar panels lose optimal sun-tracking vector while tumbling; power generation drops by $40\%$ until desaturated.
* **Long-Term Consequences:** Minor depletion of reaction control propellant if thrusters are used.
* **Recovery Options:** Re-acquire Sun lock using coarse sun sensors, then re-initialize fine pointing with star trackers.
* **Mission Failure Conditions:** Wheels remain saturated $\implies$ spacecraft tumbles uncontrollably $\implies$ solar panels face away from Sun $\implies$ battery death in $< 2\text{ orbits}$.

---

### EVENT 6: Unexpected Internal Bus Power Surge (Parasitic Draw)

* **Trigger Conditions:** Payload instrument or radio transmitter develops an internal electrical short or uncalibrated high parasitic quiescent current.
* **Probability Model:** Stochastic component wear model scaled by component TRL:
  $$\lambda = (10 - \text{TRL}) \times 0.002 \text{ per orbit}$$
* **Affected Subsystems:** `ELECTRICAL_POWER`, `C&DH`.
* **Resource Impact:** Quiescent power consumption increases unexpectedly by $+35\text{ W}$, eroding the positive daytime power margin.
* **Available Player Decisions:**
  1. *Action A: Power Distribution Bus Isolation:* Open solid-state power switches to cycle the suspect payload power line.
  2. *Action B: Downclock Onboard Computer:* Shift flight computer from $200\text{ MHz} \to 50\text{ MHz}$ low-power standby mode (saves $12\text{ W}$).
  3. *Action C: Deploy Secondary Array:* If tracking arrays are installed, command an aggressive off-pointing angle to maximize solar capture.
* **Immediate Consequences:** Drops overall power draw back within the solar array's generation capacity.
* **Long-Term Consequences:** Limits the player's ability to run multiple scientific instruments simultaneously.
* **Recovery Options:** Software patch upload to isolate the faulty sensor component.
* **Mission Failure Conditions:** Power surge drains battery during night pass without detection $\implies$ bus undervoltage shutdown.

---

### EVENT 7: Solid-State Recorder Memory Saturation (Data Buffer Overflow)

* **Trigger Conditions:** Science instruments continue gathering data while ground station contacts are skipped or downlinks fail, filling the Solid-State Recorder to $100\%$.
* **Probability Model:** Deterministic conservation of data equation:
  $$D(t) = D_0 + \int (\text{DataRate}_{\text{gen}} - \text{DataRate}_{\text{downlink}}) \, dt \ge \text{Capacity}_{\text{SSR}}$$
* **Affected Subsystems:** `DATA_STORAGE`, `SCIENTIFIC_INSTRUMENT`.
* **Resource Impact:** Storage memory full ($64/64\text{ GB}$).
* **Available Player Decisions:**
  1. *Action A: Autonomous Ingestion Lockout:* Flight computer automatically halts new observation passes to protect existing un-downlinked data.
  2. *Action B: Onboard Lossy Compression:* Activate edge AI processor to compress buffered images at a $4:1$ ratio, freeing $45\text{ GB}$ instantly at the cost of minor image noise.
  3. *Action C: Priority Packet Pruning:* Purge low-priority housekeeping logs to preserve high-value scientific imagery.
* **Immediate Consequences:** New science data collection is halted until the buffer is dumped.
* **Long-Term Consequences:** Minor lost observation opportunities during the overflow period.
* **Recovery Options:** Execute high-rate Ka-band pass over a primary ground station to clear the buffer.
* **Mission Failure Conditions:** FIFO memory overwrites un-downlinked data $\implies$ permanent loss of mission-critical observations.

---

### EVENT 8: Thermal Management Overheat (Radiator Sun-Lock Anomaly)

* **Trigger Conditions:** Spacecraft slews into an attitude that exposes optical radiators directly to solar irradiance ($S_0 = 1361\text{ W/m}^2$) while instruments run at peak power.
* **Probability Model:** Real-time thermal radiative balance equation:
  $$T_{\text{bus}} = \left(\frac{Q_{\text{in}} + P_{\text{dissipated}}}{\epsilon \sigma A_{\text{rad}}}\right)^{1/4} \ge T_{\text{max\_operating}} \quad (+45^\circ C)$$
* **Affected Subsystems:** `THERMAL_MANAGEMENT`, `BATTERY`, `SCIENTIFIC_INSTRUMENT`.
* **Resource Impact:** Bus temperature climbs rapidly from $+20^\circ C \to +58^\circ C$.
* **Available Player Decisions:**
  1. *Action A: Immediate Nadir Roll:* Command an emergency attitude roll to orient radiators toward deep-space cold sink ($3\text{ K}$).
  2. *Action B: Active Louver Modulation:* Open thermal louvers to maximum heat dissipation aperture.
  3. *Action C: Instrument Emergency Shutdown:* Instantly de-energize internal electronics to eliminate internal heat dissipation.
* **Immediate Consequences:** Temperature stabilizes and cools at approximately $1.5^\circ C/\text{minute}$.
* **Long-Term Consequences:** If caught within 3 minutes, zero hardware damage; if delayed, sensor noise increases permanently.
* **Recovery Options:** Return to nominal thermal balance attitude and verify sensor noise calibration.
* **Mission Failure Conditions:** Internal temperatures exceed $+70^\circ C \implies$ battery electrolyte boiling and explosive cell venting $\implies$ **Mission Terminated**.

---

### EVENT 9: Propulsion Thruster Valve Leak or Catalytic Bed Degradation

* **Trigger Conditions:** Hydrazine monopropellant thruster executes multiple cold-starts without pre-heating the catalytic decomposition bed ($T_{\text{bed}} < 120^\circ C$).
* **Probability Model:** Cumulative cold-start counter:
  $$\Delta I_{\text{sp}} = I_{\text{sp}, 0} \cdot (1.0 - 0.08 \times N_{\text{cold\_starts}})$$
* **Affected Subsystems:** `PROPULSION_SYSTEM`.
* **Resource Impact:** Specific impulse drops from $224\text{ s} \to 175\text{ s}$; propellant consumption per $\Delta v$ meter increases by $28\%$.
* **Available Player Decisions:**
  1. *Action A: Pre-Burn Bed Heater Cycle:* Always command catalytic bed heaters on for 15 minutes prior to thruster firing.
  2. *Action B: Mission Trajectory Re-optimization:* Re-calculate remaining orbital stationkeeping burns using conservative low-thrust burns.
  3. *Action C: Switch to Cold-Gas Secondary:* Decommission damaged hydrazine thruster and use cold-gas thrusters for attitude desaturation.
* **Immediate Consequences:** Preserves remaining propellant efficiency.
* **Long-Term Consequences:** Limits the spacecraft's capability to perform major orbit-raising maneuvers.
* **Recovery Options:** Maintain strict thermal heater protocols for all future engine burns.
* **Mission Failure Conditions:** Total propellant depletion before completing end-of-life de-orbit disposal burn.

---

### EVENT 10: Launch Window Postponement & Range Safety Delay

* **Trigger Conditions:** Ground weather at launch site (high upper-level winds) or payload integration check flags a non-compliant mass margin prior to launch.
* **Probability Model:** Launch site meteorological probability curve ($P(\text{delay}) \approx 18\%$).
* **Affected Subsystems:** `MISSION_SCHEDULE`, `FINANCIAL_BUDGET`.
* **Resource Impact:** Launch delayed by 7 to 14 days; adds $\$150\text{k}$ in ground-hold and battery trickle-charging facility costs.
* **Available Player Decisions:**
  1. *Action A: Accept Delay & Recalibrate:* Wait out the weather window; use the delay to run additional software diagnostics.
  2. *Action B: Pay for Rapid Turnaround Scrub:* Expedite payload re-fueling and range safety re-filing (costs $\$450\text{k}$).
  3. *Action C: Orbit Target Adjustment:* If launching into a planetary window (e.g., Mars), recalculate departure $C_3$ trajectory to accommodate a late departure date.
* **Immediate Consequences:** Mission clock pushed back; minor budget reduction.
* **Long-Term Consequences:** Requires tighter financial discipline during on-orbit operations.
* **Recovery Options:** Seamless transition to nominal flight upon launch clearance.
* **Mission Failure Conditions:** For planetary missions, missing the 30-day departure window results in a 26-month launch delay $\implies$ mission cancellation.

---

## 3. EVENT SYSTEM DATA SCHEMA & PYTHON ENGINE

The event engine is implemented as a clean, deterministic state-machine in:
[`backend/app/simulation_engine/anomalies.py`](file:///Users/subham/code/Lucy/events/anomalies.py)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MissionEventInstance",
  "type": "object",
  "required": [
    "event_id", "name", "category", "severity", "timestamp_met",
    "telemetry_symptoms", "available_actions", "timeout_seconds"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "name": { "type": "string" },
    "category": { "type": "string", "enum": ["SPACE_WEATHER", "POWER", "THERMAL", "ADCS", "COMMS", "PROPULSION"] },
    "severity": { "type": "string", "enum": ["ADVISORY", "CAUTION", "CRITICAL"] },
    "timestamp_met": { "type": "string" },
    "telemetry_symptoms": { "type": "object" },
    "available_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action_id", "label", "description", "resource_cost"],
        "properties": {
          "action_id": { "type": "string" },
          "label": { "type": "string" },
          "description": { "type": "string" },
          "resource_cost": { "type": "object" }
        }
      }
    },
    "timeout_seconds": { "type": "number" }
  }
}
```

---

## 4. SUMMARY OF FLIGHT OPERATIONS EVENT SYSTEM

1. **True Engineering Decision-Making:** Every anomaly presents the player with 3 distinct aerospace-grounded options (e.g., *slew bus, bakeout focal plane, dump momentum, compress data*).
2. **Deterministic & Fair:** Events are driven by seedable pseudo-random models and physical operational stress, eliminating arbitrary "game over" moments.
3. **Deep Educational Integration:** Teaches real NASA/JPL flight rules: how solar weather degrades panels, why reaction wheels saturate, and how autonomous safe modes rescue spacecraft from catastrophic loss.
