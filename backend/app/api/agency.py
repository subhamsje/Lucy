from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/v1/agency", tags=["Agency Operations"])

AGENCY_STORE_FILE = Path("/Users/subham/code/Lucy/data/agency_profile.json")

DEFAULT_AGENCY = {
    "name": "AeroSpace Directorate",
    "callsign": "TITAN-ARCHITECT",
    "director_role": "FLIGHT_SYSTEMS_ENGINEER",
    "funds_usd": 65000000.0,
    "reputation": 82,
    "research_points": 180,
    "active_contract_id": "SCEN-01-EO-SENTINEL",
    "unlocked_tech_ids": ["TECH-OPT-01", "TECH-SOLAR-01", "TECH-BAT-01", "TECH-PROP-01", "TECH-COM-01"],
    "completed_mission_logs": [
        {
            "mission_id": "SCEN-01-EO-SENTINEL",
            "mission_name": "Ignis Sentinel: LEO Earth Observation",
            "score": 950,
            "rank": "A+",
            "payout_usd": 15000000.0,
            "rp_earned": 85,
            "date": "2026-11-14"
        }
    ]
}

TECH_CATALOG = [
    {
        "id": "TECH-OPT-02",
        "name": "Advanced Multispectral Remote Sensing",
        "category": "PAYLOAD",
        "cost_rp": 80,
        "description": "Sub-meter high-resolution visible and thermal spectral arrays.",
        "unlocks_component_ids": ["INST-OPT-02"]
    },
    {
        "id": "TECH-RADAR-03",
        "name": "Synthetic Aperture L-Band Radar (SAR)",
        "category": "PAYLOAD",
        "cost_rp": 250,
        "description": "Cloud-penetrating and subsurface radar profiling arrays.",
        "unlocks_component_ids": ["INST-SAR-03"]
    },
    {
        "id": "TECH-SOLAR-02",
        "name": "Deployable Gallium Arsenide Arrays",
        "category": "POWER",
        "cost_rp": 100,
        "description": "Multi-junction GaAs triple-junction cells with 31% efficiency.",
        "unlocks_component_ids": ["EPS-SOL-02"]
    },
    {
        "id": "TECH-SOLAR-03",
        "name": "High-Efficiency Concentrator Wings",
        "category": "POWER",
        "cost_rp": 200,
        "description": "Deep-space solar concentrators rated to 3.5 AU.",
        "unlocks_component_ids": ["EPS-SOL-03"]
    },
    {
        "id": "TECH-BAT-02",
        "name": "Solid-State Ceramic Li-Ion Packs",
        "category": "POWER",
        "cost_rp": 90,
        "description": "High specific-energy cells with 80% safe Depth of Discharge.",
        "unlocks_component_ids": ["EPS-BAT-02"]
    },
    {
        "id": "TECH-PROP-02",
        "name": "Monopropellant Hydrazine Blowdown",
        "category": "PROPULSION",
        "cost_rp": 120,
        "description": "High-thrust impulsive orbital insertion and reaction control.",
        "unlocks_component_ids": ["PROP-HYD-02"]
    },
    {
        "id": "TECH-PROP-03",
        "name": "Gridded Ion Xenon Propulsion",
        "category": "PROPULSION",
        "cost_rp": 300,
        "description": "Ultra-high specific impulse (3,200s Isp) continuous electric thrust.",
        "unlocks_component_ids": ["PROP-ION-03"]
    },
    {
        "id": "TECH-COM-02",
        "name": "Deep Space X-Band High Gain Dish",
        "category": "COMMS",
        "cost_rp": 110,
        "description": "1.2m parabolic carbon dish for high data return rates.",
        "unlocks_component_ids": ["ANT-X-02"]
    },
    {
        "id": "TECH-COM-03",
        "name": "Phased-Array Ka-Band Transceiver",
        "category": "COMMS",
        "cost_rp": 260,
        "description": "Ultra-wideband multi-gigabit downlinks to NASA DSN.",
        "unlocks_component_ids": ["ANT-KA-03"]
    },
    {
        "id": "TECH-CRYO-01",
        "name": "Cryogenic Surface Astrobiology Assay",
        "category": "PAYLOAD",
        "cost_rp": 180,
        "description": "Sub-100K cryo-sampling core drill with hermetic bio-containment for Titan & Europa.",
        "unlocks_component_ids": ["INST-SPEC-02"]
    },
    {
        "id": "TECH-RTG-01",
        "name": "Pu-238 Multi-Mission RTG (MMRTG)",
        "category": "POWER",
        "cost_rp": 240,
        "description": "Decay heat thermoelectric generator providing 125W continuous power independent of solar distance.",
        "unlocks_component_ids": ["EPS-RTG-03"]
    }
]

def load_agency_profile() -> dict:
    if AGENCY_STORE_FILE.exists():
        try:
            return json.loads(AGENCY_STORE_FILE.read_text())
        except Exception:
            pass
    AGENCY_STORE_FILE.write_text(json.dumps(DEFAULT_AGENCY, indent=2))
    return DEFAULT_AGENCY

def save_agency_profile(data: dict):
    AGENCY_STORE_FILE.write_text(json.dumps(data, indent=2))

class CreateAgencyRequest(BaseModel):
    name: str = Field(..., min_length=2)
    callsign: str = Field(..., min_length=2)
    director_role: str = Field("FLIGHT_SYSTEMS_ENGINEER")

class UnlockTechRequest(BaseModel):
    tech_id: str

@router.get("/profile")
def get_agency_profile():
    return load_agency_profile()

@router.post("/create")
def create_agency(req: CreateAgencyRequest):
    data = load_agency_profile()
    data["name"] = req.name
    data["callsign"] = req.callsign
    data["director_role"] = req.director_role
    save_agency_profile(data)
    return {"status": "SUCCESS", "agency": data}

@router.get("/tech-tree")
def get_tech_tree():
    profile = load_agency_profile()
    unlocked = set(profile.get("unlocked_tech_ids", []))
    res = []
    for t in TECH_CATALOG:
        node = dict(t)
        node["is_unlocked"] = t["id"] in unlocked
        res.append(node)
    return {
        "research_points": profile.get("research_points", 0),
        "nodes": res
    }

@router.post("/tech-tree/unlock")
def unlock_tech(req: UnlockTechRequest):
    profile = load_agency_profile()
    target_tech = next((t for t in TECH_CATALOG if t["id"] == req.tech_id), None)
    if not target_tech:
        raise HTTPException(status_code=404, detail="Technology node not found")
    
    if req.tech_id in profile.get("unlocked_tech_ids", []):
        return {"status": "ALREADY_UNLOCKED", "agency": profile}
    
    rp = profile.get("research_points", 0)
    cost = target_tech["cost_rp"]
    if rp < cost:
        raise HTTPException(status_code=400, detail=f"Insufficient Research Points: {rp} available, {cost} required")
    
    profile["research_points"] = rp - cost
    profile["unlocked_tech_ids"].append(req.tech_id)
    save_agency_profile(profile)
    return {"status": "UNLOCKED", "agency": profile, "unlocked_tech": target_tech}

@router.post("/contracts/accept/{contract_id}")
def accept_contract(contract_id: str):
    profile = load_agency_profile()
    profile["active_contract_id"] = contract_id
    save_agency_profile(profile)
    return {"status": "CONTRACT_ACCEPTED", "active_contract_id": contract_id}


class ExpeditionRewardRequest(BaseModel):
    mission_id: str = "TITAN-SURFACE-EVA"
    mission_name: str = "Titan: Last Transmission Surface Expedition"
    score: int
    science_score: int
    survived: bool
    data_transmitted_gb: float = 0.0
    grade: str
    details: Optional[str] = None


@router.post("/expedition/reward")
def claim_expedition_reward(req: ExpeditionRewardRequest):
    profile = load_agency_profile()
    
    # Calculate rewards based on score and survival
    rp_earned = int(req.science_score * 0.75 + (60 if req.survived else 20))
    funds_payout = 45000000.0 if req.survived else 15000000.0
    if req.score >= 80:
        funds_payout += 25000000.0
        rp_earned += 75
    
    rep_delta = 8 if req.survived else 2
    if req.score >= 82:
        rep_delta += 6

    profile["funds_usd"] = float(profile.get("funds_usd", 0.0)) + funds_payout
    profile["research_points"] = int(profile.get("research_points", 0)) + rp_earned
    profile["reputation"] = min(100, int(profile.get("reputation", 50)) + rep_delta)

    log_entry = {
        "mission_id": req.mission_id,
        "mission_name": req.mission_name,
        "score": req.score,
        "rank": req.grade,
        "payout_usd": funds_payout,
        "rp_earned": rp_earned,
        "date": "2026-11-15",
        "details": req.details or f"Titan EVA Survival Expedition. Survived: {req.survived}"
    }
    
    logs = profile.setdefault("completed_mission_logs", [])
    logs.insert(0, log_entry)
    save_agency_profile(profile)
    
    return {
        "status": "REWARD_CLAIMED",
        "rp_earned": rp_earned,
        "funds_payout": funds_payout,
        "reputation_delta": rep_delta,
        "agency": profile
    }

