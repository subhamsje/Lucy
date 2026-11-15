"""
Automated Test Suite for Multiplayer Space Agency, Solar System, and 20-Category Mission Catalogue.
Verifies:
- 4-player session limit enforcement
- Invite codes and session lookup
- Role claiming & concurrency conflict prevention
- Synchronized spacecraft state mutations
- Flight Readiness Review (FRR) multi-player consensus voting
- Real-time room chat
- Solar system planetary data (Sun to Kuiper Belt)
- Astrodynamic transfer delta-V and speed-of-light calculations
- 20-category mission catalogue integrity
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_available_roles_endpoint():
    res = client.get("/api/v1/multiplayer/roles")
    assert res.status_code == 200
    roles = res.json()["roles"]
    assert "SYSTEMS_BUS_LEAD" in roles
    assert "SCIENCE_DIRECTOR" in roles
    assert "PROPULSION_POWER_LEAD" in roles
    assert "OPERATIONS_COMMANDER" in roles

def test_four_player_session_lifecycle():
    # 1. Create session as Player 1 (Host / Operations Commander)
    create_payload = {
        "session_name": "Artemis Test Squadron",
        "callsign": "Commander-1",
        "agency_name": "NASA HQ",
        "game_mode": "COOPERATIVE",
        "desired_role": "OPERATIONS_COMMANDER",
        "custom_invite_code": "TEST-4P"
    }
    res = client.post("/api/v1/multiplayer/sessions/create", json=create_payload)
    assert res.status_code == 200
    data = res.json()
    code = data["session_code"]
    p1_id = data["player_id"]
    assert code == "TEST-4P"
    assert len(data["session"]["players"]) == 1

    # 2. Player 2 joins as Science Director
    p2_payload = {
        "session_code": code,
        "callsign": "Scientist-2",
        "agency_name": "JPL Mars Division",
        "desired_role": "SCIENCE_DIRECTOR"
    }
    p2_res = client.post("/api/v1/multiplayer/sessions/join", json=p2_payload)
    assert p2_res.status_code == 200
    p2_id = p2_res.json()["player_id"]

    # 3. Player 3 joins as Propulsion Lead
    p3_payload = {
        "session_code": code,
        "callsign": "Propulsion-3",
        "agency_name": "ESA Propulsion Lab",
        "desired_role": "PROPULSION_POWER_LEAD"
    }
    p3_res = client.post("/api/v1/multiplayer/sessions/join", json=p3_payload)
    assert p3_res.status_code == 200
    p3_id = p3_res.json()["player_id"]

    # 4. Player 4 joins as Systems Bus Lead
    p4_payload = {
        "session_code": code,
        "callsign": "Architect-4",
        "agency_name": "CSA Structures",
        "desired_role": "SYSTEMS_BUS_LEAD"
    }
    p4_res = client.post("/api/v1/multiplayer/sessions/join", json=p4_payload)
    assert p4_res.status_code == 200
    p4_id = p4_res.json()["player_id"]

    # Verify session is at capacity (4/4 players)
    session_res = client.get(f"/api/v1/multiplayer/sessions/{code}")
    assert session_res.status_code == 200
    session_data = session_res.json()
    assert len(session_data["players"]) == 4

    # 5. Attempt 5th player join -> Must be rejected (4-player strict limit)
    p5_payload = {
        "session_code": code,
        "callsign": "Invader-5",
        "agency_name": "Rogue Space Agency"
    }
    p5_res = client.post("/api/v1/multiplayer/sessions/join", json=p5_payload)
    assert p5_res.status_code == 400
    assert "Maximum 4 players allowed" in p5_res.json()["detail"]

    # 6. Test Role Collision Prevention (Player 2 tries to claim Player 1's role)
    role_conflict_payload = {
        "player_id": p2_id,
        "role": "OPERATIONS_COMMANDER"
    }
    conflict_res = client.post(f"/api/v1/multiplayer/sessions/{code}/role", json=role_conflict_payload)
    assert conflict_res.status_code == 409
    assert "already claimed" in conflict_res.json()["detail"]

    # 7. Test Collaborative Spacecraft Mutation by Player 2 (mounting instrument)
    mutate_payload = {
        "player_id": p2_id,
        "action": "MOUNT",
        "component_id": "INST-SAR-03"
    }
    mut_res = client.post(f"/api/v1/multiplayer/sessions/{code}/spacecraft/mutate", json=mutate_payload)
    assert mut_res.status_code == 200
    assert "INST-SAR-03" in mut_res.json()["spacecraft"]["installed_component_ids"]

    # 8. Test Collaborative Flight Readiness Review (FRR) Voting
    # Player 1 votes GO
    vote1 = client.post(f"/api/v1/multiplayer/sessions/{code}/frr-vote", json={"player_id": p1_id, "vote": "GO"})
    assert vote1.status_code == 200
    assert "POLLING (1/4 GO)" in vote1.json()["frr_status"]

    # Player 2, 3, 4 vote GO
    client.post(f"/api/v1/multiplayer/sessions/{code}/frr-vote", json={"player_id": p2_id, "vote": "GO"})
    client.post(f"/api/v1/multiplayer/sessions/{code}/frr-vote", json={"player_id": p3_id, "vote": "GO"})
    vote4 = client.post(f"/api/v1/multiplayer/sessions/{code}/frr-vote", json={"player_id": p4_id, "vote": "GO"})
    assert vote4.status_code == 200
    assert vote4.json()["frr_status"] == "ALL_GO_FOR_LAUNCH"

    # 9. Test In-Game Chat
    chat_payload = {
        "player_id": p1_id,
        "message": "All stations, this is Flight. Terminal count is armed. Go for orbital insertion."
    }
    chat_res = client.post(f"/api/v1/multiplayer/sessions/{code}/chat", json=chat_payload)
    assert chat_res.status_code == 200
    assert chat_res.json()["message"]["callsign"] == "Commander-1"

def test_solar_system_bodies_endpoint():
    res = client.get("/api/v1/solar-system/bodies")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 19
    body_ids = [b["id"] for b in data["bodies"]]
    expected_bodies = [
        "SUN", "MERCURY", "VENUS", "EARTH", "MOON", "MARS", "PHOBOS", "DEIMOS",
        "CERES", "ASTEROID_BELT", "JUPITER", "EUROPA", "GANYMEDE", "SATURN",
        "TITAN", "URANUS", "NEPTUNE", "PLUTO", "KUIPER_BELT"
    ]
    for b in expected_bodies:
        assert b in body_ids, f"Missing body: {b}"

def test_solar_system_trajectory_calculation():
    payload = {
        "destination_body_id": "TITAN",
        "launch_vehicle_id": "HEAVY_LIFT",
        "spacecraft_wet_mass_kg": 450.0
    }
    res = client.post("/api/v1/solar-system/calculate-trajectory", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["destination"] == "Titan"
    assert data["estimated_flight_duration_days"] > 1000
    assert data["delta_v_budget_km_s"] >= 7.0
    assert data["one_way_light_delay_min"] > 60.0 # ~80 minutes to Titan

def test_modular_mission_catalogue_20_categories():
    res = client.get("/api/v1/missions/catalogue")
    assert res.status_code == 200
    data = res.json()
    assert data["total_missions"] >= 20
    assert data["categories_covered"] == 20

    # Test filtering by specific category
    eo_res = client.get("/api/v1/missions/catalogue?category=EARTH_OBSERVATION")
    assert eo_res.status_code == 200
    assert len(eo_res.json()["missions"]) >= 1

def test_solar_system_2_0_ephemeris_and_reconnaissance():
    """Verify Solar System 2.0 multi-tier ephemeris, moons, orbital regions and surface sites."""
    res = client.get("/api/v1/solar-system/bodies")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 30
    assert "bodies_dict" in data

    bdict = data["bodies_dict"]
    
    # 1. Verify Moon Systems
    assert "IO" in bdict and bdict["IO"]["parent_id"] == "JUPITER"
    assert "EUROPA" in bdict and bdict["EUROPA"]["parent_id"] == "JUPITER"
    assert "GANYMEDE" in bdict and bdict["GANYMEDE"]["parent_id"] == "JUPITER"
    assert "CALLISTO" in bdict and bdict["CALLISTO"]["parent_id"] == "JUPITER"
    
    assert "MIMAS" in bdict and bdict["MIMAS"]["parent_id"] == "SATURN"
    assert "ENCELADUS" in bdict and bdict["ENCELADUS"]["parent_id"] == "SATURN"
    assert "TITAN" in bdict and bdict["TITAN"]["parent_id"] == "SATURN"

    assert "MIRANDA" in bdict and bdict["MIRANDA"]["parent_id"] == "URANUS"
    assert "TITANIA" in bdict and bdict["TITANIA"]["parent_id"] == "URANUS"

    assert "TRITON" in bdict and bdict["TRITON"]["parent_id"] == "NEPTUNE"
    assert "CHARON" in bdict and bdict["CHARON"]["parent_id"] == "PLUTO"

    # 2. Verify Physical Properties
    earth = bdict["EARTH"]
    assert earth["mass_kg"] > 5.9e24
    assert earth["density_g_cm3"] > 5.0
    assert earth["rotation_period_hours"] == 24.0
    assert len(earth["orbital_regions"]) >= 3 # LEO, SSO, GEO
    assert len(earth["surface_sites"]) >= 2 # KSC, Kourou

    # 3. Verify Landing Sites & Science Reconnaissance
    mars = bdict["MARS"]
    mars_site_ids = [s["id"] for s in mars["surface_sites"]]
    assert "JEZERO_CRATER" in mars_site_ids
    assert "OLYMPUS_MONS" in mars_site_ids

    titan = bdict["TITAN"]
    titan_site_ids = [s["id"] for s in titan["surface_sites"]]
    assert "KRAKEN_MARE" in titan_site_ids
    assert "HUYGENS_COAST" in titan_site_ids
    assert titan["surface_pressure_bar"] == 1.45

    # 4. Verify Rings Data
    saturn = bdict["SATURN"]
    assert saturn["has_rings"] is True
    assert "ring_data" in saturn

    # 5. Verify Parent Filtering Endpoint
    jovian_res = client.get("/api/v1/solar-system/bodies?parent_id=JUPITER")
    assert jovian_res.status_code == 200
    jovian_bodies = jovian_res.json()["bodies"]
    assert len(jovian_bodies) >= 4 # Io, Europa, Ganymede, Callisto

    titan_res = client.get("/api/v1/missions/catalogue?category=TITAN_EXPLORATION")
    assert titan_res.status_code == 200
    assert len(titan_res.json()["missions"]) >= 1
    assert "Titan Last Transmission" in titan_res.json()["missions"][0]["name"]
