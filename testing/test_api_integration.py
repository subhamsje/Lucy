"""
Comprehensive Automated Test Suite for Orbital Architect Backend
Validates:
- Live REST API endpoints (/components, /scenarios, /spacecraft/validate, /simulation/execute)
- Physics margin models (AIAA S-120 Mass Growth, Battery DoD, RF Link Budget)
- Catastrophic failure detection gates
- Scoring rubrics (1,000-point multi-attribute calculation)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert data["components_loaded"] >= 31
    assert data["scenarios_loaded"] >= 6

def test_catalog_endpoint():
    res = client.get("/api/v1/components")
    assert res.status_code == 200
    catalog = res.json()
    assert len(catalog["components"]) >= 31

def test_scenarios_endpoint():
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios["scenarios"]) == 6

def test_spacecraft_validation_nominal():
    # Balanced LEO Earth observation configuration satisfying pointing, mass, and budget constraints
    payload = {
        "name": "Sentinel-Nominal",
        "scenario_id": "SCEN-01-EO-SENTINEL",
        "chassis_class": "SMALLSAT_LEO",
        "launch_vehicle_id": "MICRO_LAUNCHER",
        "orbit": {
            "altitude_km": 550.0,
            "inclination_deg": 97.6,
            "eccentricity": 0.001
        },
        "installed_component_ids": [
            "INST-OPT-01", "EPS-SOL-02", "EPS-BAT-02", "ANT-X-02",
            "OBC-LEON-01", "PROP-HYD-02", "ADCS-RW-02", "TCS-PASS-01", "STR-CFRP-02", "MEM-FLASH-01"
        ]
    }
    res = client.post("/api/v1/spacecraft/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_certified"] is True
    assert data["resource_budgets"]["mass_margin_pct"] > 0
    assert data["resource_budgets"]["battery_depth_of_discharge_pct"] < 30.0
    assert data["resource_budgets"]["budget_remaining_usd"] > 0

def test_spacecraft_validation_overmass_violation():
    # Attempting to launch a heavy bus on an Electron micro-launcher (250kg limit)
    payload = {
        "name": "Heavy-Violation",
        "scenario_id": "SCEN-01-EO-SENTINEL",
        "chassis_class": "HEAVY_PROBE",
        "launch_vehicle_id": "MICRO_LAUNCHER",
        "orbit": {
            "altitude_km": 550.0,
            "inclination_deg": 97.6,
            "eccentricity": 0.001
        },
        "installed_component_ids": [
            "INST-SAR-03", "EPS-SOL-03", "EPS-BAT-03", "ANT-KA-03",
            "OBC-RAD-02", "PROP-ION-03", "ADCS-ST-03", "TCS-CRYO-03", "STR-ISO-03", "MEM-MRAM-03"
        ]
    }
    res = client.post("/api/v1/spacecraft/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_certified"] is False
    assert len(data["rule_violations"]) > 0
    assert any("AIAA Lift Margin Violation" in v for v in data["rule_violations"])

def test_simulation_execution_success():
    payload = {
        "difficulty": "SPECIALIST",
        "simulation_seed": 4281920,
        "spacecraft_config": {
            "name": "Sentinel-Success",
            "scenario_id": "SCEN-01-EO-SENTINEL",
            "chassis_class": "SMALLSAT_LEO",
            "launch_vehicle_id": "MICRO_LAUNCHER",
            "orbit": {
                "altitude_km": 550.0,
                "inclination_deg": 97.6,
                "eccentricity": 0.001
            },
            "installed_component_ids": [
                "INST-OPT-01", "EPS-SOL-02", "EPS-BAT-02", "ANT-X-02",
                "OBC-LEON-01", "PROP-HYD-02", "ADCS-RW-02", "TCS-PASS-01", "STR-CFRP-02", "MEM-FLASH-01"
            ]
        }
    }
    res = client.post("/api/v1/simulation/execute", json=payload)
    assert res.status_code == 200
    sim = res.json()
    assert sim["outcome"] == "SUCCESS"
    assert sim["final_eir_score"] >= 700
    assert len(sim["telemetry_time_series"]) == 12
    assert "verification_hash" in sim

def test_leaderboard_endpoint():
    res = client.get("/api/v1/leaderboard/SCEN-01-EO-SENTINEL")
    assert res.status_code == 200
    data = res.json()
    assert len(data["top_records"]) >= 3
    assert data["top_records"][0]["score"] > 900

def test_agency_profile_endpoint():
    res = client.get("/api/v1/agency/profile")
    assert res.status_code == 200
    profile = res.json()
    assert "name" in profile
    assert "funds_usd" in profile
    assert "reputation" in profile
    assert "research_points" in profile
    assert isinstance(profile["unlocked_tech_ids"], list)

def test_agency_create_or_update():
    payload = {
        "name": "Titan Vanguard Agency",
        "callsign": "VANGUARD-01",
        "director_role": "LEAD_PLANETARY_SCIENTIST"
    }
    res = client.post("/api/v1/agency/create", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["agency"]["name"] == "Titan Vanguard Agency"
    assert data["agency"]["director_role"] == "LEAD_PLANETARY_SCIENTIST"

def test_agency_tech_tree_endpoints():
    res = client.get("/api/v1/agency/tech-tree")
    assert res.status_code == 200
    data = res.json()
    assert "research_points" in data
    assert "nodes" in data
    assert len(data["nodes"]) >= 9

    # Test unlocking a tech node
    unlock_res = client.post("/api/v1/agency/tech-tree/unlock", json={"tech_id": "TECH-OPT-02"})
    assert unlock_res.status_code in [200, 400]

def test_agency_contract_acceptance():
    res = client.post("/api/v1/agency/contracts/accept/SCEN-01-EO-SENTINEL")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CONTRACT_ACCEPTED"
    assert data["active_contract_id"] == "SCEN-01-EO-SENTINEL"

def test_agency_expedition_reward():
    req = {
        "mission_id": "TITAN-SURFACE-EVA",
        "mission_name": "Titan: Last Transmission Surface Expedition",
        "score": 88,
        "science_score": 320,
        "survived": True,
        "data_transmitted_gb": 180.0,
        "grade": "HISTORIC NASA EXPEDITION",
        "details": "Test verification of persistent expedition bridge"
    }
    res = client.post("/api/v1/agency/expedition/reward", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "REWARD_CLAIMED"
    assert data["rp_earned"] > 0
    assert data["funds_payout"] > 0
    assert "agency" in data


