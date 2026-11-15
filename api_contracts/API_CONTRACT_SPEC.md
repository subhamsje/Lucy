# COMPREHENSIVE API CONTRACT SPECIFICATION: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Architect:** Principal Backend Engineer & API Architect  
**Specification Standards:** OpenAPI 3.1.0 + RFC 7807 Problem Details + Typed WebSocket Sub-protocols  
**Target Locations:**  
- Backend Schemas: [`backend/app/schemas/api_models.py`](file:///Users/subham/code/Lucy/backend/app/schemas/api_models.py)  
- Frontend Interfaces: [`frontend/src/types/api.ts`](file:///Users/subham/code/Lucy/frontend/src/types/api.ts)  

---

## 1. UNIFIED TYPE ALIGNMENT & DATA CONTRACT MATRIX

To eliminate frontend-backend integration drift, every field name, enum constant, and unit is mirrored across Python Pydantic v2 and TypeScript:

| Entity / Domain | Python Type (Pydantic) | TypeScript Interface | Standard Unit |
| :--- | :--- | :--- | :--- |
| **Rank Tier** | `RankTier` Enum | `RankTier` Union | String identifier |
| **Mission Role** | `MissionRole` Enum | `MissionRole` Union | String identifier |
| **Chassis Class** | `ChassisClass` Enum | `ChassisClass` Union | String identifier |
| **Altitude** | `altitude_km: float` | `altitude_km: number` | Kilometers ($km$) |
| **Inclination** | `inclination_deg: float` | `inclination_deg: number` | Degrees ($^\circ$) |
| **Dry / Wet Mass** | `dry_mass_kg`, `wet_mass_kg` | `dry_mass_kg`, `wet_mass_kg` | Kilograms ($kg$) |
| **Power Gen / Load** | `day_power_generation_w` | `day_power_generation_w` | Watts ($W$) |
| **Battery DoD** | `battery_depth_of_discharge_pct` | `battery_depth_of_discharge_pct` | Percentage ($0 - 100\%$) |
| **RF Link Margin** | `link_margin_db: float` | `link_margin_db: number` | Decibels ($dB$) |
| **Data Generation** | `daily_data_generation_mb` | `daily_data_generation_mb` | Megabytes per day |
| **CapEx Cost** | `total_cost_usd: float` | `total_cost_usd: number` | USD Currency (\$) |

---

## 2. REST API ENDPOINTS SPECIFICATION

All REST routes are prefixed under `/api/v1`.

### 2.1 Spacecraft Design & Validation Endpoints

#### `POST /api/v1/spacecraft/validate`
* **Purpose:** Evaluates an assembled spacecraft configuration against AIAA mass growth rules, power energy balance, thermal dissipation, and fairing envelope fit.
* **Request Payload Example:**
```json
{
  "scenario_id": "SCEN-01-EO-SENTINEL",
  "name": "Ignis Mk.1",
  "chassis_class": "SMALLSAT_LEO",
  "launch_vehicle_id": "LV-ELECTRON-01",
  "orbit": {
    "altitude_km": 550.0,
    "inclination_deg": 97.6,
    "eccentricity": 0.001
  },
  "installed_component_ids": [
    "INST-OPT-02",
    "EPS-SOL-02",
    "EPS-BAT-02",
    "ANT-X-02",
    "OBC-RAD-02",
    "PROP-HYD-02",
    "ADCS-RW-02",
    "TCS-PIPE-02",
    "STR-CFRP-02",
    "MEM-SSD-02"
  ]
}
```
* **Response Payload Example (`200 OK`):**
```json
{
  "is_certified": true,
  "status_summary": "ALL_SUBSYSTEMS_CERTIFIED",
  "resource_budgets": {
    "dry_mass_kg": 138.5,
    "mass_growth_allowance_kg": 27.7,
    "propellant_mass_kg": 35.0,
    "wet_mass_kg": 201.2,
    "launcher_capacity_kg": 250.0,
    "mass_margin_pct": 19.52,
    "day_power_generation_w": 380.0,
    "night_power_load_w": 65.0,
    "battery_capacity_wh": 750.0,
    "eclipse_duration_min": 35.2,
    "battery_depth_of_discharge_pct": 28.4,
    "rf_downlink_rate_mbps": 120.0,
    "link_margin_db": 15.4,
    "storage_capacity_gb": 512.0,
    "daily_data_generation_mb": 185000.0,
    "total_cost_usd": 24200000.0,
    "budget_cap_usd": 35000000.0,
    "budget_remaining_usd": 10800000.0,
    "is_flight_certified": true
  },
  "rule_violations": [],
  "compliance_warnings": [
    "Battery DoD is 28.4% during peak eclipse; approaching 30.0% nominal recommended limit."
  ]
}
```

---

### 2.2 Simulation Execution Endpoints

#### `POST /api/v1/simulation/execute`
* **Purpose:** Runs the multi-orbit numerical flight simulation, applying orbital decay, eclipse cycles, stochastic anomalies, and scoring calculations.
* **Request Payload Example:**
```json
{
  "scenario_id": "SCEN-01-EO-SENTINEL",
  "difficulty": "SPECIALIST",
  "simulation_seed": 4281920,
  "spacecraft_config": {
    "name": "Ignis Sentinel",
    "scenario_id": "SCEN-01-EO-SENTINEL",
    "chassis_class": "SMALLSAT_LEO",
    "launch_vehicle_id": "LV-ELECTRON-01",
    "orbit": {
      "altitude_km": 550.0,
      "inclination_deg": 97.6,
      "eccentricity": 0.001
    },
    "installed_component_ids": [
      "INST-OPT-02", "EPS-SOL-02", "EPS-BAT-02", "ANT-X-02",
      "OBC-RAD-02", "PROP-HYD-02", "ADCS-RW-02", "TCS-PIPE-02", "STR-CFRP-02", "MEM-SSD-02"
    ]
  }
}
```
* **Response Payload Example (`200 OK`):**
```json
{
  "session_id": "SIM-84912-EO",
  "scenario_id": "SCEN-01-EO-SENTINEL",
  "outcome": "SUCCESS",
  "total_science_gb": 1450.0,
  "operational_days_survived": 180,
  "final_eir_score": 950,
  "honor_grade": "A+ (MASTER ARCHITECT)",
  "score_breakdown": {
    "objective_fulfillment": 250.0,
    "science_achievement": 187.5,
    "mass_margin_rigor": 114.0,
    "energy_efficiency": 60.0,
    "budget_efficiency": 61.7,
    "comms_performance": 80.0,
    "lifetime_survival": 70.0,
    "hardware_health": 47.0,
    "propulsion_sustainability": 40.0,
    "team_collaboration": 40.0
  },
  "anomalies_encountered": [
    {
      "event_id": "EVT-CME-01",
      "name": "Coronal Mass Ejection",
      "met_day": 42,
      "mitigated_by_player": true
    }
  ],
  "telemetry_time_series": [
    {
      "met_seconds": 0.0,
      "orbit_number": 1,
      "true_anomaly_deg": 0.0,
      "is_in_eclipse": false,
      "battery_soc_pct": 100.0,
      "bus_temperature_c": 18.5,
      "data_buffer_used_gb": 0.0,
      "reaction_wheel_rpm": 1200.0,
      "current_downlink_rate_mbps": 0.0,
      "cumulative_science_gb": 0.0
    }
  ],
  "verification_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

## 3. WEBSOCKET REAL-TIME CONTRACT & EVENTS

Connection Endpoint: `ws://localhost:8000/ws/mission/{room_id}?callsign={callsign}`

### 3.1 Event Taxonomy
1. `CLAIM_ROLE`: Sent by client to claim a specific CDF seat (`MISSION_DIRECTOR`, `SCIENCE_OFFICER`, etc.).
2. `ROLE_ASSIGNED`: Broadcast by server indicating that a player successfully claimed a seat.
3. `COMPONENT_MUTATION`: Sent by authorized specialist to add or remove a component.
4. `STATE_DELTA`: Broadcast by server with authoritative updated budgets and margin gauges.
5. `FRR_VOTE`: Sent by specialist to cast their Flight Readiness Review approval vote.
6. `FRR_STATUS`: Broadcast by server when all 4 specialists have approved launch.
7. `TELEMETRY_FRAME`: Broadcast by server during Flight Operations carrying real-time orbit state.
8. `ANOMALY_TRIGGERED`: Broadcast by server when space weather or operational threshold is breached.
9. `ANOMALY_RESOLVED`: Broadcast by server when an operator executes an action checklist item.

### 3.2 WebSocket Mutation Message Example (`Client -> Server`)
```json
{
  "type": "COMPONENT_MUTATION",
  "room_id": "ORBIT-729",
  "sender_callsign": "Dr_Vance",
  "role": "SCIENCE_OFFICER",
  "timestamp_utc": "2026-11-14T22:38:15Z",
  "payload": {
    "action": "ADD",
    "component_id": "INST-OPT-02"
  }
}
```

---

## 4. ARCHITECTURAL SUMMARY

1. **Deterministic Contracts:** Pydantic models in Python and TypeScript interfaces share identical field names and types, eliminating parsing and deserialization bugs.
2. **Authoritative Calculation:** All physical calculations and validation rules are executed exclusively on the backend to guarantee academic integrity.
3. **Low-Latency WebSockets:** Real-time state synchronization is decoupled into small JSON deltas with $<50\text{ ms}$ broadcast latency.
