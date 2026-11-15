"""
Unit and integration tests for MARS EXPLORATION educational game engine.
Tests:
- Configuration endpoint
- Satellite design validation (mass, power, battery backup, budget)
- Satellite overmass & power deficit rejection
- Mars surface map procedural generation
- Rover energy & delay mechanics
- Expedition reward bridge
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_mars_config_endpoint():
    res = client.get("/api/v1/mars/config")
    assert res.status_code == 200
    data = res.json()
    assert data["satellite"]["max_mass_kg"] == 50.0
    assert len(data["satellite"]["instruments"]) == 8
    assert len(data["satellite"]["missions"]) == 3
    assert len(data["satellite"]["challenges"]) == 6
    assert data["rover"]["max_energy"] == 100
    assert data["rover"]["max_storage_mb"] == 100.0
    assert len(data["rover"]["missions"]) == 5
    assert len(data["combined"]["stages"]) == 7

def test_satellite_design_validation_nominal():
    payload = {
        "selected_components": {
            "STRUCTURE": "STR_HEX_50",
            "SOLAR_PANELS": "SOL_DEPLOYABLE",
            "BATTERY": "BAT_LIS_200",
            "COMMUNICATION": "COM_PARABOLIC",
            "COMPUTER": "OBC_DUAL_CORE",
            "ATTITUDE_CONTROL": "ADCS_REACTION_WHEEL",
            "THERMAL_CONTROL": "THM_HEAT_PIPE",
            "PROPULSION": "PROP_MONO_HYD"
        },
        "selected_instruments": ["INST_OPTICAL", "INST_RADAR"],
        "mission_id": "MISSION_A"
    }
    res = client.post("/api/v1/mars/satellite/validate-design", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_mass_kg"] <= 50.0
    assert data["is_mass_valid"] is True
    assert data["is_budget_valid"] is True
    assert data["is_power_positive"] is True
    assert data["eclipse_survivable"] is True
    assert data["is_flight_ready"] is True
    assert len(data["warnings"]) == 0

def test_satellite_design_validation_overmass():
    payload = {
        "selected_components": {
            "STRUCTURE": "STR_REINFORCED", # 12 kg
            "SOLAR_PANELS": "SOL_TRACKING", # 8 kg
            "BATTERY": "BAT_SOLID_350", # 6 kg
            "COMMUNICATION": "COM_PHASED", # 7 kg
            "COMPUTER": "OBC_NEURAL", # 2.5 kg
            "ATTITUDE_CONTROL": "ADCS_CMG", # 8 kg
            "THERMAL_CONTROL": "THM_CRYO_LOOP", # 4.5 kg
            "PROPULSION": "PROP_PULSED_ION" # 9 kg -> Subtotal = 57 kg already > 50 kg!
        },
        "selected_instruments": ["INST_OPTICAL", "INST_MULTISPEC", "INST_RADAR"],
        "mission_id": "MISSION_C"
    }
    res = client.post("/api/v1/mars/satellite/validate-design", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_mass_valid"] is False
    assert data["is_flight_ready"] is False
    assert any("MASS OVERLOAD" in w for w in data["warnings"])

def test_rover_map_generation():
    payload = {"width": 10, "height": 10, "seed": 101}
    res = client.post("/api/v1/rover/generate-map", json=payload)
    # Note: route is under /api/v1/mars/rover/generate-map
    res = client.post("/api/v1/mars/rover/generate-map", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["width"] == 10
    assert data["height"] == 10
    assert data["starting_pos"] == {"x": 0, "y": 0}
    assert len(data["grid"]) == 10
    assert data["grid"][0][0]["type"] == "FLAT"
    assert data["total_science_sites"] >= 1

def test_mars_reward_claim():
    payload = {
        "game_mode": "COMBINED",
        "mission_id": "EXPEDITION_OMEGA",
        "science_collected": 160,
        "score": 92,
        "summary": "Completed combined orbital reconnaissance & Jezero mudstone rover exploration."
    }
    res = client.post("/api/v1/mars/expedition/reward", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["rewards"]["research_points"] >= 50
    assert data["rewards"]["capital_funding_millions"] >= 5.0
    assert data.get("persisted_to_hq") is True

def test_mars_multiplayer_full_lifecycle():
    # 1. Create Room
    create_payload = {
        "room_code": "TEST-ARES-4P",
        "callsign": "FlightDirector",
        "role": "COMMS_MISSION_DIRECTOR",
        "mode": "COMBINED"
    }
    res = client.post("/api/v1/mars/multiplayer/room/create", json=create_payload)
    assert res.status_code == 200
    data = res.json()
    room_code = data["room_code"]
    host_id = data["player_id"]
    assert "TEST-ARES-4P" in room_code
    assert data["room"]["players"][host_id]["role"] == "COMMS_MISSION_DIRECTOR"

    # 2. Join 3 more players (reaching 4-player max)
    roles = ["ORBITAL_SATELLITE_LEAD", "SURFACE_ROVER_DRIVER", "SCIENCE_PAYLOAD_DIRECTOR"]
    player_ids = [host_id]
    for idx, role in enumerate(roles):
        join_payload = {
            "room_code": room_code,
            "callsign": f"Specialist-{idx+1}",
            "role": role
        }
        jres = client.post("/api/v1/mars/multiplayer/room/join", json=join_payload)
        assert jres.status_code == 200
        jdata = jres.json()
        player_ids.append(jdata["player_id"])

    # 3. Verify room state has 4 players
    state_res = client.get(f"/api/v1/mars/multiplayer/room/{room_code}")
    assert state_res.status_code == 200
    room_state = state_res.json()
    assert len(room_state["players"]) == 4

    # 4. Attempt 5th player join -> Must reject with 400
    overflow_res = client.post("/api/v1/mars/multiplayer/room/join", json={
        "room_code": room_code,
        "callsign": "OverflowPlayer",
        "role": "ORBITAL_SATELLITE_LEAD"
    })
    assert overflow_res.status_code == 400

    # 5. Dispatch collaborative actions
    # Satellite lead updates satellite
    sat_lead_id = player_ids[1]
    sat_action = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/action", json={
        "player_id": sat_lead_id,
        "action": "UPDATE_SATELLITE",
        "payload": {
            "components": {"STRUCTURE": "STR_3U"},
            "instruments": ["INST_OPTICAL", "INST_RADAR"]
        }
    })
    assert sat_action.status_code == 200
    assert sat_action.json()["room"]["satellite_state"]["components"]["STRUCTURE"] == "STR_3U"

    # Rover driver moves rover
    rover_driver_id = player_ids[2]
    rover_action = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/action", json={
        "player_id": rover_driver_id,
        "action": "MOVE_ROVER",
        "payload": {"x": 1, "y": 0, "energy_cost": 5}
    })
    assert rover_action.status_code == 200
    assert rover_action.json()["room"]["rover_state"]["pos"] == {"x": 1, "y": 0}
    assert rover_action.json()["room"]["rover_state"]["energy"] == 95

    # Science director samples tile
    sci_lead_id = player_ids[3]
    sci_action = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/action", json={
        "player_id": sci_lead_id,
        "action": "SAMPLE_TILE",
        "payload": {"storage_cost": 25}
    })
    assert sci_action.status_code == 200
    assert sci_action.json()["room"]["rover_state"]["flash_mb"] == 25

    # Comms director transmits data
    comms_action = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/action", json={
        "player_id": host_id,
        "action": "TRANSMIT_DATA",
        "payload": {}
    })
    assert comms_action.status_code == 200
    assert comms_action.json()["room"]["rover_state"]["flash_mb"] == 0
    assert comms_action.json()["room"]["satellite_state"]["science_collected"] == 50

    # Advance stage
    adv_action = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/action", json={
        "player_id": host_id,
        "action": "ADVANCE_STAGE",
        "payload": {}
    })
    assert adv_action.status_code == 200
    assert adv_action.json()["room"]["expedition_stage"] == 2

    # 6. Post chat message
    chat_res = client.post(f"/api/v1/mars/multiplayer/room/{room_code}/chat", json={
        "player_id": rover_driver_id,
        "message": "Rover entering Jezero crater fan delta."
    })
    assert chat_res.status_code == 200
    assert len(chat_res.json()["messages"]) >= 1
