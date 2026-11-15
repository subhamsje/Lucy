"""
FastAPI Server for Orbital Architect (Lucy)
Refactored into clean modular architecture using independent MarginEngine, ScoringEngine, and AnomalyEngine.
"""

import os
import json
import uuid
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.app.schemas.api_models import (
    SpacecraftConfiguration,
    FeasibilityValidationResponse,
    SimulationExecutionRequest,
    SimulationExecutionResponse,
    SimulationOutcome
)
from backend.app.simulation_engine.margins import MarginEngine
from backend.app.simulation_engine.scoring import ScoringEngine
from backend.app.simulation_engine.anomalies import AnomalyEngine

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SCENARIOS_DIR = BASE_DIR / "scenarios"
STATIC_DIR = BASE_DIR / "backend" / "app" / "static"

from backend.app.api.agency import router as agency_router
from backend.app.api.multiplayer import router as multiplayer_router
from backend.app.api.solar_system import router as solar_system_router
from backend.app.api.missions import router as missions_router
from backend.app.api.mars_game import router as mars_router

app = FastAPI(
    title="Orbital Architect API",
    description="Interactive Space Mission Design & Systems Engineering Simulation Platform",
    version="1.0.0"
)

app.include_router(agency_router)
app.include_router(multiplayer_router)
app.include_router(solar_system_router)
app.include_router(missions_router)
app.include_router(mars_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Initial Datasets
def load_catalog() -> Dict[str, Any]:
    with open(DATA_DIR / "components_catalog.json", "r") as f:
        return json.load(f)

def load_rules() -> Dict[str, Any]:
    with open(DATA_DIR / "compatibility_rules.json", "r") as f:
        return json.load(f)

def load_scenarios() -> Dict[str, Any]:
    with open(SCENARIOS_DIR / "mission_scenarios.json", "r") as f:
        return json.load(f)

CATALOG = load_catalog()
RULES = load_rules()
SCENARIOS = load_scenarios()

from backend.app.api.missions import MISSION_CATALOGUE

def get_scenario_definition(scenario_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not scenario_id:
        return SCENARIOS["scenarios"][0] if SCENARIOS.get("scenarios") else None
        
    # 1. Direct match in SCENARIOS
    sc = next((s for s in SCENARIOS.get("scenarios", []) if s.get("id") == scenario_id), None)
    if sc:
        return sc
        
    # 2. Match from MISSION_CATALOGUE (the 20 master mission contracts)
    mission = next((m for m in MISSION_CATALOGUE if m.get("id") == scenario_id), None)
    if mission:
        orbit_text = mission.get("target_orbit", "")
        alt_km = 550.0
        inc_deg = 97.6
        if "35,786" in orbit_text or "GEO" in orbit_text:
            alt_km = 35786.0
            inc_deg = 0.0
        elif "km" in orbit_text:
            try:
                import re
                m_alt = re.search(r'(\d+[\d,]*)\s*km', orbit_text)
                if m_alt:
                    alt_km = float(m_alt.group(1).replace(',', ''))
                m_inc = re.search(r'([\d\.]+)°', orbit_text)
                if m_inc:
                    inc_deg = float(m_inc.group(1))
            except Exception:
                pass

        return {
            "id": mission["id"],
            "name": mission.get("name", mission["id"]),
            "category": mission.get("category", "EARTH_OBSERVATION"),
            "difficulty": mission.get("difficulty", "SPECIALIST"),
            "target_destination": mission.get("destination", "Earth Orbit"),
            "mission_objective": mission.get("description", "Execute scientific observation objectives."),
            "scientific_requirements": {
                "primary_data_threshold_gb": mission.get("science_threshold_gb", 450.0),
                "target_metrics": {}
            },
            "orbit_trajectory_options": [
                {
                    "name": mission.get("target_orbit", "Nominal Mission Orbit"),
                    "orbit_type": "Mission Orbit",
                    "altitude_km": alt_km,
                    "inclination_deg": inc_deg,
                    "eccentricity": 0.001,
                    "delta_v_insertion_ms": 120.0,
                    "pros": "Prescribed operational trajectory.",
                    "cons": "Standard space environmental exposure."
                }
            ],
            "required_spacecraft_capabilities": {
                "min_pointing_accuracy_deg": 0.05,
                "min_delta_v_ms": 80.0,
                "mandatory_subsystems": [
                    "SCIENTIFIC_INSTRUMENT",
                    "ELECTRICAL_POWER",
                    "COMMUNICATION_ANTENNA",
                    "DATA_STORAGE",
                    "ATTITUDE_CONTROL"
                ]
            },
            "mission_duration_days": mission.get("mission_lifetime_days", 180),
            "budget_cap_usd": mission.get("budget_usd", 35000000.0),
            "launch_constraints": {
                "compatible_launch_classes": ["MICRO_LAUNCHER", "RIDESHARE_ESPA", "MEDIUM_LIFT", "HEAVY_LIFT"],
                "launch_window_frequency_days": 1.0,
                "launcher_max_capacity_kg": mission.get("max_spacecraft_mass_kg", 5000.0)
            }
        }
        
    # 3. Fallback to default scenario
    if SCENARIOS.get("scenarios"):
        return SCENARIOS["scenarios"][0]
    return None

# In-memory session store
SAVED_DESIGNS: Dict[str, Any] = {}
SIMULATION_RESULTS: Dict[str, Any] = {}

# ==============================================================================
# REST API ROUTES
# ==============================================================================

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ONLINE",
        "version": "1.0.0",
        "astrodynamics_engine": "READY",
        "components_loaded": len(CATALOG["components"]),
        "scenarios_loaded": len(SCENARIOS["scenarios"])
    }

@app.get("/api/v1/components")
def get_components():
    return CATALOG

@app.get("/api/v1/scenarios")
def get_scenarios():
    return SCENARIOS

@app.post("/api/v1/spacecraft/validate", response_model=FeasibilityValidationResponse)
def validate_spacecraft(design: SpacecraftConfiguration):
    scenario = get_scenario_definition(design.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    margins = MarginEngine.evaluate_spacecraft_margins(
        design.dict(),
        scenario,
        CATALOG["components"],
        RULES
    )
    return margins

@app.post("/api/v1/spacecraft/save")
def save_spacecraft(design: SpacecraftConfiguration):
    design_id = design.id or f"DESIGN-{uuid.uuid4().hex[:8].upper()}"
    design_dict = design.dict()
    design_dict["id"] = design_id
    SAVED_DESIGNS[design_id] = design_dict
    return {"message": "Design saved successfully", "design_id": design_id, "data": design_dict}

@app.get("/api/v1/spacecraft/{design_id}")
def get_spacecraft(design_id: str):
    if design_id not in SAVED_DESIGNS:
        raise HTTPException(status_code=404, detail="Design not found")
    return SAVED_DESIGNS[design_id]

@app.post("/api/v1/simulation/execute", response_model=SimulationExecutionResponse)
def execute_simulation(req: SimulationExecutionRequest):
    cfg = req.spacecraft_config
    if not cfg:
        raise HTTPException(status_code=400, detail="Missing spacecraft configuration")

    scenario = get_scenario_definition(cfg.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Authoritative Margins Validation
    margins = MarginEngine.evaluate_spacecraft_margins(
        cfg.dict(),
        scenario,
        CATALOG["components"],
        RULES
    )
    budgets = margins["resource_budgets"]
    session_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

    # Check for Catastrophic Failure Gate
    is_catastrophic = False
    failure_reason = ""
    if not margins["is_certified"]:
        if budgets["wet_mass_kg"] > budgets["launcher_capacity_kg"]:
            is_catastrophic = True
            failure_reason = margins["rule_violations"][0]
        elif budgets["battery_depth_of_discharge_pct"] >= 100.0:
            is_catastrophic = True
            failure_reason = "Catastrophic Battery Depletion in Eclipse"

    if is_catastrophic:
        score_eval = ScoringEngine.calculate_mission_score(
            {"is_catastrophic_failure": True, "failure_reason": failure_reason},
            scenario,
            req.difficulty.value if hasattr(req.difficulty, "value") else str(req.difficulty)
        )
        return {
            "session_id": session_id,
            "scenario_id": cfg.scenario_id,
            "outcome": SimulationOutcome.CATASTROPHIC_FAILURE,
            "total_science_gb": 0.0,
            "operational_days_survived": 4,
            "final_eir_score": 0,
            "honor_grade": score_eval["honor_grade"],
            "score_breakdown": score_eval["score_breakdown"],
            "anomalies_encountered": [{"name": failure_reason, "met_day": 4, "severity": "CRITICAL"}],
            "telemetry_time_series": [],
            "verification_hash": f"CERT-{uuid.uuid4().hex[:16]}"
        }

    # Successful Multi-Orbit Flight Simulation
    duration_days = scenario["mission_duration_days"]
    daily_mb = budgets["daily_data_generation_mb"]
    # 85% operational efficiency accounting for stationkeeping and calibration
    total_science_gb = min(3500.0, (daily_mb * duration_days * 0.85) / 1024.0)
    
    # Check for anomalies
    anomalies = AnomalyEngine.generate_flight_anomalies(
        req.simulation_seed,
        cfg.scenario_id,
        cfg.orbit.altitude_km,
        cfg.orbit.inclination_deg,
        req.difficulty.value if hasattr(req.difficulty, "value") else str(req.difficulty)
    )

    # 1,000-point Scoring Evaluation
    score_eval = ScoringEngine.calculate_mission_score(
        {
            "is_catastrophic_failure": False,
            "total_science_gb": total_science_gb,
            "resource_budgets": budgets,
            "operational_days_survived": duration_days,
            "hardware_soh_pct": max(70.0, 100.0 - (budgets["battery_depth_of_discharge_pct"] * 0.6)),
            "deorbit_compliant": budgets["propellant_mass_kg"] >= 5.0
        },
        scenario,
        req.difficulty.value if hasattr(req.difficulty, "value") else str(req.difficulty)
    )

    # High-density 1-orbit telemetry time-series frame generation
    telemetry = []
    for step in range(12):
        t_sec = step * 480.0
        in_eclipse = (step >= 7 and step <= 10)
        soc = 100.0 - (step - 7) * 7.2 if in_eclipse else min(100.0, 78.0 + step * 2.8)
        telemetry.append({
            "met_seconds": t_sec,
            "orbit_number": 1,
            "true_anomaly_deg": round(step * 30.0, 1),
            "is_in_eclipse": in_eclipse,
            "battery_soc_pct": round(soc, 1),
            "bus_temperature_c": round(14.8 if in_eclipse else 23.2, 1),
            "data_buffer_used_gb": round(min(budgets["storage_capacity_gb"], step * 3.8), 1),
            "reaction_wheel_rpm": round(2200.0 + step * 35.0, 1),
            "current_downlink_rate_mbps": budgets["rf_downlink_rate_mbps"] if (step == 3 or step == 4) else 0.0,
            "cumulative_science_gb": round(step * 1.8, 2)
        })

    response_obj = {
        "session_id": session_id,
        "scenario_id": cfg.scenario_id,
        "outcome": SimulationOutcome.SUCCESS if score_eval["outcome"] == "SUCCESS" else SimulationOutcome.PARTIAL_SUCCESS,
        "total_science_gb": round(total_science_gb, 1),
        "operational_days_survived": duration_days,
        "final_eir_score": score_eval["final_score"],
        "honor_grade": score_eval["honor_grade"],
        "score_breakdown": score_eval["score_breakdown"],
        "anomalies_encountered": anomalies,
        "telemetry_time_series": telemetry,
        "verification_hash": f"CERT-{uuid.uuid4().hex[:16]}"
    }
    # Credit Space Agency Account with Mission Rewards & Research Points
    try:
        from backend.app.api.agency import load_agency_profile, save_agency_profile
        agency = load_agency_profile()
        if score_eval["outcome"] == "SUCCESS":
            payout = float(scenario.get("budget_cap_usd", 25000000.0) * 0.45)
            rp_award = int(50 + (score_eval["final_score"] / 20.0))
            rep_award = 3
        else:
            payout = float(scenario.get("budget_cap_usd", 25000000.0) * 0.15)
            rp_award = 15
            rep_award = -2

        build_cost = float(budgets.get("total_cost_usd", 15000000.0))
        net_delta = payout - build_cost
        agency["funds_usd"] = max(1000000.0, float(agency.get("funds_usd", 65000000.0)) - build_cost + payout)
        agency["research_points"] = agency.get("research_points", 100) + rp_award
        agency["reputation"] = max(10, min(100, agency.get("reputation", 82) + rep_award))
        
        # Log to mission history
        if "completed_mission_logs" not in agency:
            agency["completed_mission_logs"] = []
        agency["completed_mission_logs"].insert(0, {
            "session_id": session_id,
            "mission_id": cfg.scenario_id,
            "mission_name": scenario.get("name", "Classified Mission"),
            "score": score_eval["final_score"],
            "rank": score_eval["honor_grade"],
            "payout_usd": payout,
            "rp_earned": rp_award,
            "date": "2026-11-14"
        })
        save_agency_profile(agency)
        response_obj["agency_reward"] = {
            "payout_usd": payout,
            "rp_earned": rp_award,
            "rep_change": rep_award,
            "new_funds_usd": agency["funds_usd"],
            "new_rp": agency["research_points"],
            "new_reputation": agency["reputation"]
        }
    except Exception as e:
        print("Reward crediting error:", e)

    SIMULATION_RESULTS[session_id] = response_obj
    return response_obj

@app.get("/api/v1/leaderboard/{scenario_id}")
def get_leaderboard(scenario_id: str):
    return {
        "scenario_id": scenario_id,
        "top_records": [
            {
                "rank": 1,
                "callsign": "FlightDirector_Alex",
                "spacecraft_name": "Aura-Prime",
                "score": 962,
                "grade": "A+ (MASTER ARCHITECT)",
                "science_gb": 1820.0,
                "cost_usd": 24500000.0,
                "verified": True
            },
            {
                "rank": 2,
                "callsign": "Commander_Vance",
                "spacecraft_name": "Ignis Sentinel",
                "score": 950,
                "grade": "A+ (MASTER ARCHITECT)",
                "science_gb": 1450.0,
                "cost_usd": 24200000.0,
                "verified": True
            },
            {
                "rank": 3,
                "callsign": "Cadet_Taylor",
                "spacecraft_name": "CubeWildfire-1",
                "score": 734,
                "grade": "B (COMMERCIAL GRADE)",
                "science_gb": 410.0,
                "cost_usd": 5200000.0,
                "verified": True
            }
        ]
    }

# ==============================================================================
# WEBSOCKET REAL-TIME MULTIPLAYER HUB
# ==============================================================================

class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.room_roles: Dict[str, Dict[str, Optional[str]]] = {}

    async def connect(self, room_id: str, websocket: WebSocket, callsign: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
            self.room_roles[room_id] = {
                "MISSION_DIRECTOR": None,
                "SPACECRAFT_ENGINEER": None,
                "SCIENCE_OFFICER": None,
                "FLIGHT_OPERATIONS": None
            }
        self.rooms[room_id].append(websocket)
        await self.broadcast(room_id, {
            "type": "USER_JOINED",
            "callsign": callsign,
            "roles": self.room_roles[room_id]
        })

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                del self.room_roles[room_id]

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.rooms:
            payload = json.dumps(message)
            for ws in self.rooms[room_id]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    pass

manager = RoomConnectionManager()

@app.websocket("/ws/mission/{room_id}")
async def mission_socket(websocket: WebSocket, room_id: str, callsign: str = "Cadet"):
    await manager.connect(room_id, websocket, callsign)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            mtype = data.get("type")
            
            if mtype == "CLAIM_ROLE":
                role = data.get("role")
                if manager.room_roles[room_id].get(role) is None:
                    manager.room_roles[room_id][role] = callsign
                    await manager.broadcast(room_id, {
                        "type": "ROLE_ASSIGNED",
                        "role": role,
                        "callsign": callsign,
                        "roles": manager.room_roles[room_id]
                    })
            elif mtype in ["COMPONENT_MUTATION", "FRR_VOTE", "CHAT_MESSAGE"]:
                await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)


# Serve Static UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_root():
    landing_file = STATIC_DIR / "landing.html"
    if landing_file.exists():
        return FileResponse(landing_file)
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Orbital Architect API is live. Navigate to /docs for Swagger UI."}

@app.get("/landing")
def serve_landing():
    landing_file = STATIC_DIR / "landing.html"
    if landing_file.exists():
        return FileResponse(landing_file)
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/app")
@app.get("/app.html")
@app.get("/play")
def serve_app():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Orbital Architect Workstation is offline."}

@app.get("/mars")
@app.get("/mars.html")
@app.get("/mars-exploration")
def serve_mars():
    mars_file = STATIC_DIR / "mars.html"
    if mars_file.exists():
        return FileResponse(mars_file)
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/titan")
@app.get("/titan.html")
def serve_titan():
    titan_file = STATIC_DIR / "titan.html"
    if titan_file.exists():
        return FileResponse(titan_file)
    return FileResponse(STATIC_DIR / "index.html")
