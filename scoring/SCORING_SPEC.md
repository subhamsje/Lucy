# MISSION EVALUATION & SCORING RUBRIC SPECIFICATION: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Domain:** Educational Game Scoring, Aerospace Mission Evaluation, Multi-Attribute Utility Analysis  
**Target Repository:** `/Users/subham/code/Lucy/scoring`  
**Core Motto:** *Value Delivered vs. Resources Consumed: A Cheap Satellite That Fails Science Scores Zero; An Expensive Flagship That Delivers Breakthroughs Triumphs.*

---

## 1. SCORING PHILOSOPHY & OBJECTIVE-ANCHORED EVALUATION

A common flaw in simulation games is over-indexing on budget: an empty 3U CubeSat with no instruments gets a high score simply because it was cheap.  
In `Orbital Architect`, **evaluation is strictly anchored to the Mission Charter's original primary objectives**:
1. **The Primary Objective Gate:** If a mission fails to achieve the minimum scientific data threshold ($D_{\text{downlinked}} < D_{\text{min}}$) or the spacecraft experiences catastrophic hardware loss, the mission fails regardless of budget savings.
2. **Multi-Attribute Utility (1,000 Point Baseline):** Performance is scored across 10 distinct aerospace dimensions, scaled by difficulty multipliers and objective fulfillment percentages.
3. **Pareto-Optimal Recognition:** High-cost flagship observatories and low-cost agile rideshares compete on fair, normalized terms via the **Mission Return-on-Investment (ROI)** metric.

---

## 2. THE COMPREHENSIVE 1,000-POINT SCORING FORMULA

The final mission score is computed using a multi-dimensional weighted formulation:

$$\text{Final Score} = \left[ \sum_{i=1}^{10} \left( W_i \cdot S_i \right) + \text{BonusPoints} - \text{Penalties} \right] \times \text{DifficultyMultiplier}$$

### 2.1 Weight Distribution Matrix (1,000 Base Points)

| Dimension | Max Points ($W_i$) | Governing Equation / Metric | What It Rewards |
| :--- | :---: | :--- | :--- |
| **1. Primary Objective Completion** | **250** | $250 \times \min\left(1.0, \frac{D_{\text{downlinked}}}{D_{\text{target}}}\right)$ | Delivering on the charter's core scientific promise. |
| **2. Scientific Achievement & Quality** | **150** | $150 \times \left( \frac{\text{GSD}_{\text{achieved}}}{\text{GSD}_{\text{target}}} \right)^{-1} \times Q_{\text{jitter}}$ | Sub-meter imagery, high-resolution radar, or spectrometer fidelity. |
| **3. Engineering Margin Rigor** | **120** | $120 \times \text{Clamp}\left(\frac{\text{MassMargin}_{\text{final}} - 5\%}{15\%}, 0, 1\right)$ | Respecting AIAA S-120 aerospace mass growth safety margins. |
| **4. Power & Energy Efficiency** | **100** | $100 \times \left[1.0 - \left(\frac{\text{DoD}_{\text{avg}}}{60\%}\right)\right] \times \eta_{\text{power}}$ | Sizing arrays and batteries to prevent deep discharge degradation. |
| **5. Budget & Cost Effectiveness** | **100** | $100 \times \min\left(1.0, \frac{\text{Budget}_{\text{cap}} - \text{Cost}}{\text{Budget}_{\text{cap}} \times 0.5}\right)$ | Accomplishing objectives efficiently without fiscal waste. |
| **6. Communications Performance** | **80** | $80 \times \min\left(1.0, \frac{\text{PassEfficiency}}{95\%}\right) \times \text{LinkMarginScore}$ | Zero buffer overflows; healthy RF link margin ($E_b/N_0 \ge 3\text{ dB}$). |
| **7. Mission Lifetime & Survival** | **70** | $70 \times \min\left(1.0, \frac{T_{\text{days\_survived}}}{T_{\text{charter\_days}}}\right)$ | Operating through the entire planned mission operational phase. |
| **8. Hardware Reliability & Health** | **50** | $50 \times \left(\frac{\text{SOH}_{\text{battery}} + \text{SOH}_{\text{payload}} + \text{SOH}_{\text{bus}}}{300\%}\right)$ | Returning the spacecraft with hardware health reserves intact. |
| **9. Propulsion / Orbit Efficiency** | **40** | $40 \times \min\left(1.0, \frac{\Delta v_{\text{remaining}}}{\Delta v_{\text{deorbit\_required}}}\right)$ | Retaining propellant reserve for safe end-of-life deorbit disposal. |
| **10. Team Collaboration (Co-op)** | **40** | $40 \times \left(1.0 - \frac{\text{RoleDisputes}}{10}\right) \times \text{UnanimousFRR}$ | Seamless cross-disciplinary coordination and unanimous FRR sign-off. |
| **TOTAL BASELINE** | **1,000** | | |

---

## 3. SUCCESS THRESHOLDS, BONUSES & PENALTIES

### 3.1 Outcome Classifications
* **Category 1: Full Flight Certification (Score: $750 - 1000+$):** Primary objectives 100% fulfilled; all engineering margins respected; hardware health $>80\%$ at end-of-life.
* **Category 2: Partial Mission Success (Score: $450 - 749$):** Primary science partially achieved ($>60\%$ data threshold); hardware survived but experienced degraded operations (e.g., optical noise, depleted battery).
* **Category 3: Mission Abort / Failure (Score: $0 - 449$):**
  * Battery dropped to $0\%$ in eclipse (spacecraft froze).
  * Launch vehicle structural load exceeded (rocket failure).
  * Downlinked telemetry $<50\%$ of minimum charter requirement.

### 3.2 Bonus Objective Points ($+150$ Points Max)
* **Under-Budget Pioneer ($+50$ pts):** Complete mission using less than $60\%$ of allowable CapEx budget.
* **Razor's Edge Excellence ($+40$ pts):** Maintain mass margin between $15\%$ and $18\%$ without violating launcher envelope.
* **Continuous Sun Tracker ($+30$ pts):** Maintain $100\%$ solar array illumination without entering shadow for an entire 180-day mission (Dawn-Dusk SSO).
* **Zero Propellant Drag Master ($+30$ pts):** Complete a LEO mission using aerodynamic body trim and magnetic torquers without burning chemical fuel.

### 3.3 Engineering Penalties (Deductions)
* **Single-Event Latchup / In-Flight Safe Mode ($ -40$ pts per event):** Spacecraft entered autonomous safe mode due to unmitigated anomaly.
* **Data Buffer Overflow ($ -1.5$ pts per GB lost):** Science data overwritten in SSR due to missed ground passes.
* **Space Debris Non-Compliance ($ -100$ pts):** Spacecraft left stranded in LEO at end of life without sufficient propellant to execute a 25-year deorbit burn per IADC guidelines.
* **Budget Overrun ($ -2.0$ pts per $\$100\text{k}$ over cap):** Programs exceeding budget cap incur severe penalties.

### 3.4 Difficulty Multipliers
$$\text{Multiplier} = \begin{cases} 0.85 & \text{Cadet (Assisted warnings, no random anomalies)} \\ 1.00 & \text{Specialist (Standard AIAA margins)} \\ 1.35 & \text{Flight Director (Stochastic space weather, strict thermal noise)} \end{cases}$$

---

## 4. WORKED SCORING EXAMPLES (3 DIVERSE ARCHITECTURES)

To demonstrate how the scoring system fairly evaluates different engineering solutions, here are 3 actual simulations of the **"Ignis Sentinel" Earth Observation Mission**:
* **Mission Charter Objective:** Minimum $400\text{ GB}$ downlinked, GSD $\le 15\text{ m}$, 180-day duration, Budget Cap: $\$35\text{M}$.

---

### Case Study A: The Ultra-Low-Cost 12U CubeSat Rideshare
* **Configuration:** $12\text{U}$ Aluminum bus (`STR-ALU-01`), Basic Imager (`INST-OPT-01`), Body Silicon panels (`EPS-SOL-01`), LiFePO4 battery (`EPS-BAT-01`), S-band omni patch (`ANT-S-01`), launched via ESPA rideshare (\$2.5M).
* **Performance:**
  * Downlinked Science: $410\text{ GB}$ (Just crossed the $400\text{ GB}$ threshold).
  * Resolution GSD: $15.0\text{ m}$ (Meets requirement).
  * Total Mission Cost: $\$5.2\text{M}$ (Massive $\$29.8\text{M}$ budget saving!).
  * Battery DoD: $38\%$ average (High wear; battery SOH dropped to $68\%$).
  * Downlink: S-band bottleneck required dumping data on every single ground pass.
* **Score Calculation:**
  $$\begin{aligned}
  S_{\text{objective}} &= 250 \times (410 / 400) = 250.0 \\
  S_{\text{science}} &= 150 \times (15.0 / 15.0) = 150.0 \\
  S_{\text{margin}} &= 120 \times 0.65 = 78.0 \\
  S_{\text{power}} &= 100 \times [1.0 - (38 / 60)] = 36.7 \\
  S_{\text{budget}} &= 100 \times 1.0 = 100.0 \quad (\text{Max budget score}) \\
  S_{\text{comms}} &= 80 \times 0.82 = 65.6 \\
  S_{\text{lifetime}} &= 70 \times (180 / 180) = 70.0 \\
  S_{\text{health}} &= 50 \times 0.68 = 34.0 \\
  S_{\text{propulsion}} &= 40 \times 0.0 = 0.0 \quad (\text{No deorbit engine}) \\
  \text{Bonus} &= +50 \text{ (Under-Budget Pioneer)} \\
  \text{Penalties} &= -100 \text{ (Space Debris Non-Compliance)} \\
  \text{Raw Total} &= 734.3 \times 1.00 = \mathbf{734\text{ Points (Grade: B - Partial Success)}}
  \end{aligned}$$
* **Evaluation:** High budget marks, but penalized for battery wear and zero deorbit capability.

---

### Case Study B: The High-Performance Dedicated SmallSat Flagship
* **Configuration:** Hexagonal CFRP bus (`STR-CFRP-02`), High-Res Panchromatic Telescope (`INST-OPT-02`), Deployable GaAs wings (`EPS-SOL-02`), Aerospace Li-ion battery (`EPS-BAT-02`), X-band horn (`ANT-X-02`), Hydrazine thruster (`PROP-HYD-02`), launched on dedicated Electron (\$7.5M).
* **Performance:**
  * Downlinked Science: $1,450\text{ GB}$ ($3.6\times$ charter target!).
  * Resolution GSD: $0.8\text{ m}$ (Sub-meter exceptional detail).
  * Total Mission Cost: $\$24.2\text{M}$ (Within $\$35\text{M}$ budget cap).
  * Battery DoD: $24\%$ average (Pristine health; $SOH = 94\%$).
  * Downlink: 120 Mbps X-band dumped data with $15\text{ dB}$ link margin.
  * Deorbit: Retained $65\text{ m/s}$ propellant for controlled end-of-life deorbit.
* **Score Calculation:**
  $$\begin{aligned}
  S_{\text{objective}} &= 250.0 \quad (\text{Maxed out}) \\
  S_{\text{science}} &= 150.0 \times 1.25 = 187.5 \quad (\text{Sub-meter bonus factor}) \\
  S_{\text{margin}} &= 120 \times 0.95 = 114.0 \\
  S_{\text{power}} &= 100 \times [1.0 - (24 / 60)] = 60.0 \\
  S_{\text{budget}} &= 100 \times [(35 - 24.2) / 17.5] = 61.7 \\
  S_{\text{comms}} &= 80 \times 1.0 = 80.0 \\
  S_{\text{lifetime}} &= 70 \times 1.0 = 70.0 \\
  S_{\text{health}} &= 50 \times 0.94 = 47.0 \\
  S_{\text{propulsion}} &= 40 \times 1.0 = 40.0 \\
  \text{Bonus} &= +40 \text{ (Razor's Edge Mass Margin)} \\
  \text{Penalties} &= 0.0 \\
  \text{Raw Total} &= 950.2 \times 1.00 = \mathbf{950\text{ Points (Grade: A+ - Master Architect)}}
  \end{aligned}$$
* **Evaluation:** Clear winner. Proves that spending more budget within the cap to achieve sub-meter resolution and full sustainability yields the highest aerospace engineering grade.

---

### Case Study C: The Over-Engineered Failed Mission
* **Configuration:** Phased Array SAR Radar (`INST-SAR-03`) mounted on a SmallSat chassis with undersized silicon solar panels and insufficient battery capacity.
* **Performance:**
  * Mission entered safe mode on Orbit 14 when SAR peak power ($1450\text{ W}$) drained batteries to $0\%$ during an eclipse transit.
  * Total Science Downlinked: $22\text{ GB}$ (Failed $400\text{ GB}$ threshold).
* **Score Calculation:**
  $$\text{Final Score} = \mathbf{0\text{ Points (Catastrophic Loss - Battery Brownout in Eclipse)}}$$

---

## 5. POST-MISSION DEBRIEF REPORT TEMPLATE (AUTOMATED DOSSIER)

When a simulation concludes, the engine automatically compiles a comprehensive flight report:

```markdown
================================================================================
           ORBITAL ARCHITECT // FLIGHT OPERATIONS EVALUATION REPORT
================================================================================
MISSION CALLSIGN: IGNIS-SENTINEL-FLIGHT-04            DATE: 2026-11-14T22:30Z
OPERATIONAL STATUS: FLIGHT CERTIFIED - FULL SUCCESS   DIFFICULTY: SPECIALIST (1.0x)
EIR COMPOSITE SCORE: 950 / 1000                      HONOR GRADE: A+
================================================================================

1. EXECUTIVE OVERVIEW
The Ignis Sentinel satellite completed its full 180-day operational phase in 
a 550 km Sun-Synchronous Orbit (97.6° inclination). The spacecraft satisfied all
primary mission directives, downlinking 1,450 GB of valid high-resolution 
terrestrial wildfire telemetry (362% of primary science charter requirement).

2. FINAL SPACECRAFT CONFIGURATION & PHYSICAL AUDIT
- Primary Chassis: STR-CFRP-02 (Hexagonal Carbon-Fiber Composite Bus)
- Primary Payload: INST-OPT-02 (0.8m Panchromatic High-Resolution Telescope)
- Power Subsystem: EPS-SOL-02 (380W Deployable GaAs) + EPS-BAT-02 (750Wh Li-ion)
- Communications:  ANT-X-02 (120 Mbps Medium-Gain X-Band Horn, Link Margin: +15.4 dB)
- Propulsion/ADCS: PROP-HYD-02 (Hydrazine Monoprop) + ADCS-RW-02 (0.08° Accuracy)
- Dry Mass / Wet Mass: 138.5 kg / 201.2 kg (AIAA S-120 Mass Growth Margin: 19.5%)
- Launch Vehicle:  Rocket Lab Electron (Lift Margin: +19.5% PASS, Fairing Fit: PASS)
- Total CapEx Cost: $24,200,000 USD (Budget Cap: $35,000,000 USD - Margin: $10.8M)

3. RESOURCE UTILIZATION & TELEMETRY PROFILE
- Battery Depth-of-Discharge: Nominal avg 24.2% (Peak eclipse: 28.4% - Limit: 30%)
- Battery State-of-Health at EOL: 94.2% (Low degradation)
- Solid-State Storage Buffer: Peak utilization 48.5% (Zero packet overflow)
- Propellant Remaining at EOL: 4.8 kg (Sufficient for controlled 25-yr deorbit)

4. IN-FLIGHT ANOMALY LOG & OPERATIONAL DECISIONS
- [T+042:14:22] Anomaly: Coronal Mass Ejection (Solar Particle Event)
  -> Action: Flight Operations commanded Survival Safe Attitude & Sensor Power-Down.
  -> Outcome: Zero electronics damage; array efficiency dropped 3.2% (Recovered).
- [T+115:08:10] Anomaly: Reaction Wheel Momentum Saturation (5,800 RPM)
  -> Action: Executed 4-second hydrazine thruster desaturation burn.
  -> Outcome: Angular momentum cleared; 3-axis pointing restored in 2 minutes.

5. LESSONS LEARNED & RECOMMENDATIONS FOR NEXT ATTEMPT
- What Worked: Deployable GaAs solar wings provided sufficient day margin to recharge
  the battery module from 28% DoD within 42 minutes of sunrise.
- Optimization Target: Upgrading to the Ka-band dish would allow double the science
  downlink in fewer ground passes, though it requires +40W additional RF power.
================================================================================
```

---

## 6. PYTHON SCORING ENGINE IMPLEMENTATION

The scoring rubric is implemented in:
[`backend/app/simulation_engine/scoring.py`](file:///Users/subham/code/Lucy/scoring/scoring_engine.py)

```python
from typing import Dict, Any

def calculate_mission_score(simulation_data: Dict[str, Any], scenario: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """Computes transparent multi-attribute mission score (0 - 1000+ points)."""
    
    # 1. Check Catastrophic Failure Gate
    if simulation_data.get("is_catastrophic_failure", False):
        return {
            "final_score": 0,
            "grade": "F (CATASTROPHIC LOSS)",
            "breakdown": {},
            "failure_reason": simulation_data.get("failure_reason", "Hardware lost")
        }

    # Extract metrics
    downlinked_gb = simulation_data.get("total_science_gb", 0.0)
    target_gb = scenario["scientific_requirements"]["primary_data_threshold_gb"]
    budget_cap = scenario["budget_cap_usd"]
    cost = simulation_data.get("total_cost_usd", budget_cap)
    dod_avg = simulation_data.get("avg_dod_pct", 30.0)
    mass_margin_pct = simulation_data.get("mass_margin_pct", 15.0)
    days_survived = simulation_data.get("days_survived", 0)
    target_days = scenario["mission_duration_days"]
    soh_pct = simulation_data.get("hardware_soh_pct", 100.0)
    deorbit_compliant = simulation_data.get("deorbit_compliant", True)

    # 2. Compute Weighted Sub-scores
    s_objective = 250.0 * min(1.0, downlinked_gb / target_gb)
    s_science = 150.0 * min(1.5, downlinked_gb / target_gb)
    s_margin = 120.0 * max(0.0, min(1.0, (mass_margin_pct - 5.0) / 15.0))
    s_power = 100.0 * max(0.0, 1.0 - (dod_avg / 60.0))
    s_budget = 100.0 * max(0.0, min(1.0, (budget_cap - cost) / (budget_cap * 0.5)))
    s_comms = 80.0 * (1.0 if simulation_data.get("buffer_overflows", 0) == 0 else 0.5)
    s_lifetime = 70.0 * min(1.0, days_survived / target_days)
    s_health = 50.0 * (soh_pct / 100.0)
    s_propulsion = 40.0 * (1.0 if deorbit_compliant else 0.0)
    s_team = 40.0

    raw_base = (s_objective + s_science + s_margin + s_power + s_budget + 
                s_comms + s_lifetime + s_health + s_propulsion + s_team)

    # 3. Bonuses & Penalties
    bonuses = 0.0
    penalties = 0.0
    if cost <= budget_cap * 0.6:
        bonuses += 50.0  # Under-budget bonus
    if not deorbit_compliant:
        penalties += 100.0  # Space debris penalty

    # 4. Multiplier
    multipliers = {"CADET": 0.85, "SPECIALIST": 1.00, "FLIGHT_DIRECTOR": 1.35}
    diff_mult = multipliers.get(difficulty, 1.00)

    final_score = int(max(0.0, (raw_base + bonuses - penalties) * diff_mult))

    # Grade allocation
    if final_score >= 900: grade = "A+ (MASTER ARCHITECT)"
    elif final_score >= 800: grade = "A (FLIGHT QUALIFIED)"
    elif final_score >= 700: grade = "B (COMMERCIAL GRADE)"
    elif final_score >= 500: grade = "C (PARTIAL SUCCESS)"
    else: grade = "D (SUB-OPTIMAL)"

    return {
        "final_score": final_score,
        "grade": grade,
        "breakdown": {
            "objective_fulfillment": round(s_objective, 1),
            "science_achievement": round(s_science, 1),
            "mass_margin_rigor": round(s_margin, 1),
            "energy_efficiency": round(s_power, 1),
            "budget_efficiency": round(s_budget, 1),
            "comms_performance": round(s_comms, 1),
            "lifetime_survival": round(s_lifetime, 1),
            "hardware_health": round(s_health, 1),
            "propulsion_sustainability": round(s_propulsion, 1),
            "team_collaboration": round(s_team, 1),
            "bonuses": bonuses,
            "penalties": penalties
        }
    }
```

---

## 7. SUMMARY OF SCORING SPECIFICATION

1. **Anti-Exploit Design:** Anchoring evaluation to the Primary Objective threshold eliminates "empty CubeSat" budget exploits.
2. **Transparent Multi-Attribute Rubric:** 10 clear aerospace dimensions with visible mathematical equations.
3. **Comprehensive Debrief Dossier:** Every simulation run generates a detailed debrief report outlining successes, in-flight decisions, and specific engineering recommendations.
