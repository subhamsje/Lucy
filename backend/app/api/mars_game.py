"""
Mars Exploration Game Engine & Astrodynamics API.
Unified backend for:
- Game 1: Satellite Mission Designer (50 kg microsatellite, 8 scientific instruments, 3 missions, 6 challenges)
- Game 2: Mars Rover Explorer (Tile-based surface map, energy/storage/delay mechanics, 5 missions)
- Combined Mars Expedition (Orbital reconnaissance to surface exploration bridge)
- Agency HQ Reward Bridge (Research points, credits, reputation)
"""

import math
import random
import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/mars", tags=["Mars Exploration Educational Games"])

SPEED_OF_LIGHT_KM_S = 299792.458
MARS_DISTANCE_EARTH_AVG_KM = 225000000.0 # ~225M km average

# -----------------------------------------------------------------------------
# 1. SATELLITE MISSION DESIGNER DATA CATALOGUE
# -----------------------------------------------------------------------------
SATELLITE_COMPONENTS = {
    "STRUCTURE": [
        {"id": "STR_3U", "name": "3U Cubesat Modular Frame", "mass_kg": 6.0, "cost_credits": 25000, "power_w": 0.0, "description": "Lightweight anodized aluminium alloy bus with vibration dampers."},
        {"id": "STR_HEX_50", "name": "Standard 50kg Hexagonal Bus", "mass_kg": 8.0, "cost_credits": 40000, "power_w": 0.0, "description": "Carbon-composite honeycomb structure optimized for Mars thermal expansion."},
        {"id": "STR_REINFORCED", "name": "Deep-Space Heavy Shielded Frame", "mass_kg": 12.0, "cost_credits": 60000, "power_w": 0.0, "description": "Tantalum-lined chassis offering high radiation resistance."}
    ],
    "SOLAR_PANELS": [
        {"id": "SOL_BODY", "name": "Body-Mounted Silicon Cells", "mass_kg": 4.0, "cost_credits": 15000, "power_generation_w": 35.0, "power_w": 0.0, "description": "Reliable 18% efficiency cells, no deployment risk."},
        {"id": "SOL_DEPLOYABLE", "name": "Deployable GaAs Solar Wings", "mass_kg": 6.0, "cost_credits": 30000, "power_generation_w": 65.0, "power_w": 0.0, "description": "Dual deployable wings with 29.5% triple-junction cells."},
        {"id": "SOL_TRACKING", "name": "Sun-Tracking UltraFlex Arrays", "mass_kg": 8.0, "cost_credits": 55000, "power_generation_w": 95.0, "power_w": 2.0, "description": "Circular deployable arrays with 1-axis active sun tracking."}
    ],
    "BATTERY": [
        {"id": "BAT_LI_100", "name": "Li-Ion Standard Pack (100 Wh)", "mass_kg": 3.0, "cost_credits": 12000, "capacity_wh": 100.0, "power_w": 0.0, "description": "Mil-spec lithium-ion battery with internal thermal heaters."},
        {"id": "BAT_LIS_200", "name": "Advanced Li-S Cell Pack (200 Wh)", "mass_kg": 4.0, "cost_credits": 28000, "capacity_wh": 200.0, "power_w": 0.0, "description": "High gravimetric energy density lithium-sulfur battery."},
        {"id": "BAT_SOLID_350", "name": "Solid-State Ceramic Battery (350 Wh)", "mass_kg": 6.0, "cost_credits": 45000, "capacity_wh": 350.0, "power_w": 0.0, "description": "Radiation-immune solid electrolyte pack with zero thermal runaway."}
    ],
    "COMMUNICATION": [
        {"id": "COM_PATCH", "name": "X-Band Microstrip Patch Array", "mass_kg": 3.0, "cost_credits": 18000, "power_w": 8.0, "data_rate_mbps": 0.5, "description": "Omni-directional low-gain antenna for telemetry and safe-mode."},
        {"id": "COM_PARABOLIC", "name": "0.6m High-Gain Parabolic Dish", "mass_kg": 5.0, "cost_credits": 35000, "power_w": 15.0, "data_rate_mbps": 2.0, "description": "Deployable mesh reflector for direct-to-Earth X/Ka data downlinks."},
        {"id": "COM_PHASED", "name": "Electronic Steered Phased Array", "mass_kg": 7.0, "cost_credits": 60000, "power_w": 22.0, "data_rate_mbps": 5.0, "description": "Rapid beam-steering array capable of simultaneous Earth and Rover relay."}
    ],
    "COMPUTER": [
        {"id": "OBC_STANDARD", "name": "Rad-Tolerant ARM Cortex Processor", "mass_kg": 1.5, "cost_credits": 20000, "power_w": 4.0, "storage_mb": 500.0, "description": "Dual redundant microcontrollers running real-time flight OS."},
        {"id": "OBC_DUAL_CORE", "name": "Rad-Hardened Dual-Core Space Processor", "mass_kg": 2.0, "cost_credits": 38000, "power_w": 7.0, "storage_mb": 1500.0, "description": "Fault-tolerant space computer with SEU-resistant EDAC memory."},
        {"id": "OBC_NEURAL", "name": "Space AI Edge Coprocessor", "mass_kg": 2.5, "cost_credits": 65000, "power_w": 12.0, "storage_mb": 4000.0, "description": "Autonomous cloud/dust storm detection and terrain feature classification."}
    ],
    "ATTITUDE_CONTROL": [
        {"id": "ADCS_MAG_TORQ", "name": "Cold Gas + Sun Sensor ADCS", "mass_kg": 4.0, "cost_credits": 22000, "power_w": 3.0, "pointing_accuracy_deg": 1.0, "description": "Basic 3-axis coarse pointing for nadir Earth/Mars orientation."},
        {"id": "ADCS_REACTION_WHEEL", "name": "Precision 3-Axis Reaction Wheels + Star Tracker", "mass_kg": 6.0, "cost_credits": 42000, "power_w": 8.0, "pointing_accuracy_deg": 0.05, "description": "Fine pointing sub-system essential for high-resolution imaging."},
        {"id": "ADCS_CMG", "name": "Control Moment Gyroscope System", "mass_kg": 8.0, "cost_credits": 70000, "power_w": 14.0, "pointing_accuracy_deg": 0.01, "description": "Rapid slew capability for dynamic target tracking during close flybys."}
    ],
    "THERMAL_CONTROL": [
        {"id": "THM_PASSIVE", "name": "Passive Multi-Layer Insulation (MLI)", "mass_kg": 2.0, "cost_credits": 10000, "power_w": 0.0, "temp_range_c": "[-40, +65]", "description": "Gold/Mylar reflective blankets with surface thermal coatings."},
        {"id": "THM_HEAT_PIPE", "name": "Variable Louvers + Ammonia Heat Pipes", "mass_kg": 3.0, "cost_credits": 24000, "power_w": 3.0, "temp_range_c": "[-20, +45]", "description": "Active thermal dissipation louvers preventing electronics overheating."},
        {"id": "THM_CRYO_LOOP", "name": "Active Thermoelectric Radiant Loop", "mass_kg": 4.5, "cost_credits": 40000, "power_w": 7.0, "temp_range_c": "[-10, +30]", "description": "Precise thermal stability required for cryo-cooled optical sensors."}
    ],
    "PROPULSION": [
        {"id": "PROP_COLD_GAS", "name": "Nitrogen Cold-Gas Propulsion (50 m/s)", "mass_kg": 5.0, "cost_credits": 15000, "delta_v_m_s": 50.0, "power_w": 1.0, "description": "Simple pressurised nitrogen for minor orbit station-keeping."},
        {"id": "PROP_MONO_HYD", "name": "Monopropellant Hydrazine Thruster (250 m/s)", "mass_kg": 8.0, "cost_credits": 38000, "delta_v_m_s": 250.0, "power_w": 4.0, "description": "Catalytic hydrazine thruster for Mars capture orbit trim maneuvers."},
        {"id": "PROP_PULSED_ION", "name": "Miniature Pulsed Plasma Ion Thruster (800 m/s)", "mass_kg": 9.0, "cost_credits": 65000, "delta_v_m_s": 800.0, "power_w": 18.0, "description": "High-efficiency solid Teflon ion propulsion for prolonged spiral orbits."}
    ]
}

SCIENTIFIC_INSTRUMENTS = [
    {
        "id": "INST_OPTICAL",
        "name": "Optical Surface Camera",
        "mass_kg": 2.0,
        "cost_credits": 18000,
        "power_w": 6.0,
        "data_output_mb": 45.0,
        "science_value": 30,
        "target_missions": ["MISSION_A", "COMBINED"],
        "description": "High-resolution visible spectrum camera capturing 1m/pixel images of Martian craters, dunes, and candidate rover sites."
    },
    {
        "id": "INST_MULTISPEC",
        "name": "Multispectral Geological Imager",
        "mass_kg": 2.5,
        "cost_credits": 25000,
        "power_w": 8.0,
        "data_output_mb": 60.0,
        "science_value": 45,
        "target_missions": ["MISSION_A", "MISSION_C"],
        "description": "9-band spectral sensor identifying iron oxides, phyllosilicates, and hydrated clay minerals."
    },
    {
        "id": "INST_SPECTROMETER",
        "name": "Infrared / UV Gas Spectrometer",
        "mass_kg": 2.0,
        "cost_credits": 22000,
        "power_w": 7.0,
        "data_output_mb": 25.0,
        "science_value": 40,
        "target_missions": ["MISSION_B", "MISSION_C"],
        "description": "Measures atmospheric column densities of CO2, water vapor, methane, and ozone trace gases."
    },
    {
        "id": "INST_RADAR",
        "name": "Synthetic Aperture Subsurface Sounder (SAR)",
        "mass_kg": 2.0,
        "cost_credits": 30000,
        "power_w": 14.0,
        "data_output_mb": 80.0,
        "science_value": 55,
        "target_missions": ["MISSION_A", "MISSION_C", "COMBINED"],
        "description": "Ground-penetrating radar penetrating up to 500m into Martian regolith to map buried glacial ice sheets."
    },
    {
        "id": "INST_RADIOMETER",
        "name": "Thermal Infrared Radiometer",
        "mass_kg": 1.5,
        "cost_credits": 16000,
        "power_w": 4.0,
        "data_output_mb": 20.0,
        "science_value": 35,
        "target_missions": ["MISSION_B"],
        "description": "Monitors diurnal surface temperature curves and atmospheric dust optical depth."
    },
    {
        "id": "INST_MAGNETOMETER",
        "name": "Fluxgate Triaxial Magnetometer",
        "mass_kg": 1.0,
        "cost_credits": 14000,
        "power_w": 3.0,
        "data_output_mb": 15.0,
        "science_value": 25,
        "target_missions": ["MISSION_C"],
        "description": "Measures crustal remnant magnetic paleofields and solar wind interaction."
    },
    {
        "id": "INST_RADIATION",
        "name": "Cosmic Ray & Energetic Particle Detector",
        "mass_kg": 1.0,
        "cost_credits": 15000,
        "power_w": 3.0,
        "data_output_mb": 10.0,
        "science_value": 30,
        "target_missions": ["MISSION_B", "MISSION_C"],
        "description": "Measures galactic cosmic ray (GCR) dosage and solar energetic proton (SEP) storm events."
    },
    {
        "id": "INST_ALTIMETER",
        "name": "Pulsed Laser Surface Altimeter (LIDAR)",
        "mass_kg": 2.0,
        "cost_credits": 28000,
        "power_w": 12.0,
        "data_output_mb": 40.0,
        "science_value": 45,
        "target_missions": ["MISSION_A", "COMBINED"],
        "description": "Creates 3D topographic relief models of canyon walls, volcanic calderas, and rover landing hazards."
    }
]

SATELLITE_MISSIONS = [
    {
        "id": "MISSION_A",
        "name": "Mission A: Mars Surface Observation",
        "objective": "Map candidate exploration sites, photograph ancient fluvial channels, and select rover touchdown zones.",
        "recommended_instruments": ["INST_OPTICAL", "INST_RADAR", "INST_ALTIMETER"],
        "science_target_points": 120,
        "reward_credits": 65000,
        "reward_rp": 80,
        "recommended_orbit_altitude_km": 320.0
    },
    {
        "id": "MISSION_B",
        "name": "Mission B: Mars Weather & Atmosphere Monitoring",
        "objective": "Track planet-encircling dust storms, monitor thermal emission, and analyze atmospheric pressure drops.",
        "recommended_instruments": ["INST_SPECTROMETER", "INST_RADIOMETER", "INST_RADIATION"],
        "science_target_points": 100,
        "reward_credits": 55000,
        "reward_rp": 70,
        "recommended_orbit_altitude_km": 400.0
    },
    {
        "id": "MISSION_C",
        "name": "Mission C: Deep Geological & Magnetospheric Research",
        "objective": "Probe crustal remanence, search for subterranean brine aquifers, and evaluate space radiation hazard.",
        "recommended_instruments": ["INST_MULTISPEC", "INST_RADAR", "INST_MAGNETOMETER", "INST_RADIATION"],
        "science_target_points": 140,
        "reward_credits": 80000,
        "reward_rp": 100,
        "recommended_orbit_altitude_km": 280.0
    }
]

SATELLITE_CHALLENGES = [
    {
        "id": "CHALLENGE_POWER_FAILURE",
        "title": "Battery Depletion Emergency",
        "description": "Satellite enters extended 45-minute solar eclipse behind Mars. Battery capacity drops below 25%.",
        "options": [
            {
                "action": "POWER_SAVE_MODE",
                "label": "Engage Emergency Safe Mode (Heaters + Beacon only)",
                "power_saved_w": 25.0,
                "science_penalty": 10,
                "outcome": "NOMINAL: Core systems survived the cold eclipse. Normal operations resume upon sunrise."
            },
            {
                "action": "CONTINUE_OBSERVATIONS",
                "label": "Keep Instruments Active on Battery",
                "power_saved_w": 0.0,
                "science_penalty": 0,
                "outcome": "CRITICAL RISK: Battery drained to 4%. Brownout caused computer reboot and partial data corruption."
            }
        ]
    },
    {
        "id": "CHALLENGE_COMMS_FAILURE",
        "title": "Earth Link Disruption",
        "description": "Severe solar flare causes radio noise interference. Deep Space Network carrier lock lost.",
        "options": [
            {
                "action": "SWITCH_BACKUP_ANTENNA",
                "label": "Switch to Low-Gain Omni Antenna & Reduce Bitrate",
                "outcome": "NOMINAL: Telemetry restored at 0.5 Mbps. Command link re-established."
            },
            {
                "action": "WAIT_FOR_PASS",
                "label": "Wait 90 minutes for Next Ground Station Window",
                "outcome": "DELAY: Commands delayed. Satellite buffer queued 45 MB of scientific observations."
            }
        ]
    },
    {
        "id": "CHALLENGE_CAMERA_MALFUNCTION",
        "title": "Optical Sensor CCD Glitch",
        "description": "High-energy cosmic ray hit pixel readout register, causing high-contrast sensor artifacts.",
        "options": [
            {
                "action": "SOFT_RESET",
                "label": "Execute In-Flight Firmware Reset & Sensor Calibration",
                "outcome": "NOMINAL: Sensor dark-frame recalibration successful. Image sharpness restored to 98%."
            },
            {
                "action": "MULTISPECTRAL_FALLBACK",
                "label": "Route Imaging via Multispectral Subsystem",
                "outcome": "WORKAROUND: Science collection continues with narrower spectral field of view."
            }
        ]
    },
    {
        "id": "CHALLENGE_SOLAR_PANEL_DAMAGE",
        "title": "Micrometeoroid Wing Piercing",
        "description": "High-velocity dust particle perforated solar panel string #3. Generation drops by 20W.",
        "options": [
            {
                "action": "RECONFIGURE_BUS",
                "label": "Reroute Electrical Bus via Secondary Shunt Regulator",
                "outcome": "NOMINAL: Bus balanced. Power deficit compensated by optimized instrument scheduling."
            },
            {
                "action": "BOOST_PROPULSION",
                "label": "Fire Thrusters to Adjust Angle to Sun",
                "fuel_cost_kg": 1.2,
                "outcome": "STABILIZED: Solar incidence angle improved (+8W), 1.2 kg propellant consumed."
            }
        ]
    },
    {
        "id": "CHALLENGE_SPACE_DEBRIS",
        "title": "Orbital Debris Conjunction Warning",
        "description": "NASA Orbital Debris Program warns of derelict Soviet-era spacecraft fragment crossing path in 30 mins.",
        "options": [
            {
                "action": "COLLISION_AVOIDANCE_BURN",
                "label": "Perform 4 m/s Retrograde Avoidance Burn",
                "fuel_cost_kg": 0.8,
                "outcome": "NOMINAL: Miss distance increased to 18.4 km. Spacecraft fully safe."
            },
            {
                "action": "MINIMIZE_CROSS_SECTION",
                "label": "Feather Solar Panels Edge-on to Flight Vector",
                "fuel_cost_kg": 0.0,
                "outcome": "CLOSE CALL: Debris passed at 480 meters. No impact recorded."
            }
        ]
    },
    {
        "id": "CHALLENGE_OVERHEATING",
        "title": "Pericenter Aerothermal Warning",
        "description": "Low periapsis skimming upper atmosphere causes thermal louvers to register +52°C.",
        "options": [
            {
                "action": "ACTIVATE_THERMAL_LOOP",
                "label": "Open Radiant Louvers & Orient Heat Sinks to Deep Space",
                "power_cost_w": 5.0,
                "outcome": "NOMINAL: Thermal equilibrium re-established at comfortable +18°C."
            },
            {
                "action": "PERIAPSIS_RAISE_BURN",
                "label": "Raise Periapsis Orbit by 40 km",
                "fuel_cost_kg": 1.5,
                "outcome": "NOMINAL: Orbit raised safely above atmospheric drag horizon."
            }
        ]
    }
]

# -----------------------------------------------------------------------------
# 2. MARS ROVER EXPLORER DATA CATALOGUE
# -----------------------------------------------------------------------------
TERRAIN_TYPES = {
    "FLAT": {"name": "Flat Regolith Plains", "energy_cost": 5, "risk": "LOW", "color": "#f97316", "icon": "⬝"},
    "ROCKS": {"name": "Basaltic Boulder Field", "energy_cost": 15, "risk": "MEDIUM", "color": "#78716c", "icon": "▲"},
    "SAND": {"name": "Soft Eolian Sand Dunes", "energy_cost": 20, "risk": "HIGH", "color": "#ea580c", "icon": "≈"},
    "CRATER": {"name": "Impact Crater Slope", "energy_cost": 25, "risk": "SEVERE", "color": "#b91c1c", "icon": "◉"},
    "SCIENCE": {"name": "Hydrated Mineral Outcrop", "energy_cost": 10, "risk": "MEDIUM", "color": "#38bdf8", "icon": "★"}
}

ROVER_MISSIONS = [
    {
        "id": "ROVER_MSN_01",
        "name": "Mission 1: First Steps on Mars",
        "location": "Jezero Crater Landing Ellipse",
        "description": "Egress lander ramp, traverse 50 meters across flat ground, capture primary 360° mastcam panorama.",
        "target_distance_tiles": 5,
        "target_photos": 1,
        "target_scans": 0,
        "reward_credits": 20000,
        "reward_rp": 30
    },
    {
        "id": "ROVER_MSN_02",
        "name": "Mission 2: Rock Investigation & Laser LIBS",
        "location": "Delta Scarp Outcrop",
        "description": "Navigate around hazardous basalt boulders, find an igneous bedrock target, and perform laser ablation spectroscopy.",
        "target_distance_tiles": 8,
        "target_photos": 1,
        "target_scans": 2,
        "reward_credits": 30000,
        "reward_rp": 45
    },
    {
        "id": "ROVER_MSN_03",
        "name": "Mission 3: The Sand Dune Challenge",
        "location": "Seitah Rippled Sand Sea",
        "description": "Cross treacherous sand ripple corridor, avoid wheel slippage exceeding 60%, and collect fine atmospheric dust deposition.",
        "target_distance_tiles": 12,
        "target_photos": 2,
        "target_scans": 2,
        "reward_credits": 45000,
        "reward_rp": 60
    },
    {
        "id": "ROVER_MSN_04",
        "name": "Mission 4: The Crater Rim Expedition",
        "location": "Belva Impact Crater Slope",
        "description": "Ascend 18° rocky crater ramparts to uncover exposed ancient sedimentary strata, drill a core sample, and analyze soil chemistry.",
        "target_distance_tiles": 15,
        "target_photos": 2,
        "target_scans": 3,
        "reward_credits": 60000,
        "reward_rp": 80
    },
    {
        "id": "ROVER_MSN_05",
        "name": "Mission 5: The Ultimate Discovery",
        "location": "Ancient Lacustrine Mudstone Deposit",
        "description": "Reach the river delta terminus, collect comprehensive soil and rock astrobiology cores, and successfully transmit all findings to Earth.",
        "target_distance_tiles": 20,
        "target_photos": 3,
        "target_scans": 4,
        "reward_credits": 100000,
        "reward_rp": 150
    }
]

DATA_STORAGE_TYPES = {
    "PHOTO": {"name": "High-Res Mastcam Photo", "size_mb": 10.0, "science_val": 15},
    "ROCK_SCAN": {"name": "APXS & Raman Rock Scan", "size_mb": 20.0, "science_val": 35},
    "SOIL_ANALYSIS": {"name": "Drilled Core Sample Analysis", "size_mb": 25.0, "science_val": 45},
    "ATMOSPHERE": {"name": "MEDA Weather & Pressure Profile", "size_mb": 5.0, "science_val": 10}
}

COMMAND_DELAYS_SEC = {
    "MOVE": 5.0,
    "SCAN": 8.0,
    "PHOTO": 4.0,
    "TRANSMIT": 6.0
}

# -----------------------------------------------------------------------------
# API ROUTE ENDPOINTS
# -----------------------------------------------------------------------------
@router.get("/config")
def get_mars_game_config():
    """Retrieve all authoritative game configuration, component catalogues, and missions."""
    return {
        "satellite": {
            "components": SATELLITE_COMPONENTS,
            "instruments": SCIENTIFIC_INSTRUMENTS,
            "missions": SATELLITE_MISSIONS,
            "challenges": SATELLITE_CHALLENGES,
            "max_mass_kg": 50.0,
            "starting_budget_credits": 400000
        },
        "rover": {
            "terrain_types": TERRAIN_TYPES,
            "missions": ROVER_MISSIONS,
            "storage_types": DATA_STORAGE_TYPES,
            "command_delays_sec": COMMAND_DELAYS_SEC,
            "max_energy": 100,
            "max_storage_mb": 100.0
        },
        "combined": {
            "title": "Combined Mars Expedition",
            "stages": [
                {"stage": 1, "name": "Design the Satellite", "desc": "Engineer a 50kg microsatellite bus with balanced mass and power."},
                {"stage": 2, "name": "Launch to Mars Orbit", "desc": "Execute launch sequence and orbital insertion burn into Mars science orbit."},
                {"stage": 3, "name": "Orbital Observation & Site Scouting", "desc": "Operate optical/radar payloads to pinpoint prime surface exploration zones."},
                {"stage": 4, "name": "Select Rover Landing Zone", "desc": "Designate the rover touchdown landing zone based on orbital reconnaissance."},
                {"stage": 5, "name": "Surface Rover Exploration", "desc": "Traverse treacherous Martian terrain, manage energy, and collect science cores."},
                {"stage": 6, "name": "Orbital Relay Communication", "desc": "Utilize the satellite orbital relay to transmit discoveries through communication delays."},
                {"stage": 7, "name": "Expedition Science Synthesis", "desc": "Combine orbital mapping with in-situ surface data into authoritative NASA dossier."}
            ]
        }
    }

class SatelliteDesignValidationRequest(BaseModel):
    selected_components: Dict[str, str] # e.g. {"STRUCTURE": "STR_HEX_50", ...}
    selected_instruments: List[str] # e.g. ["INST_OPTICAL", "INST_RADAR"]
    mission_id: str = "MISSION_A"
    player_budget_credits: Optional[float] = None

@router.post("/satellite/validate-design")
def validate_satellite_design(req: SatelliteDesignValidationRequest):
    """Educational engineering calculations for mass, power, budget, and readiness."""
    total_mass_kg = 0.0
    total_cost_credits = 0.0
    power_consumption_w = 0.0
    power_generation_w = 0.0
    battery_capacity_wh = 100.0
    data_storage_mb = 500.0
    data_rate_mbps = 1.0

    # Calculate sub-systems
    for category, comp_id in req.selected_components.items():
        comp_list = SATELLITE_COMPONENTS.get(category, [])
        comp = next((c for c in comp_list if c["id"] == comp_id), None)
        if comp:
            total_mass_kg += comp.get("mass_kg", 0.0)
            total_cost_credits += comp.get("cost_credits", 0.0)
            power_consumption_w += comp.get("power_w", 0.0)
            if "power_generation_w" in comp:
                power_generation_w += comp["power_generation_w"]
            if "capacity_wh" in comp:
                battery_capacity_wh = comp["capacity_wh"]
            if "storage_mb" in comp:
                data_storage_mb = comp["storage_mb"]
            if "data_rate_mbps" in comp:
                data_rate_mbps = comp["data_rate_mbps"]

    # Calculate instruments
    for inst_id in req.selected_instruments:
        inst = next((i for i in SCIENTIFIC_INSTRUMENTS if i["id"] == inst_id), None)
        if inst:
            total_mass_kg += inst.get("mass_kg", 0.0)
            total_cost_credits += inst.get("cost_credits", 0.0)
            power_consumption_w += inst.get("power_w", 0.0)

    # Educational formulas
    starting_budget = float(req.player_budget_credits if req.player_budget_credits is not None else 400000.0)
    remaining_budget = starting_budget - total_cost_credits
    mass_limit = 50.0
    is_mass_valid = total_mass_kg <= mass_limit
    is_budget_valid = total_cost_credits <= starting_budget
    power_margin_w = power_generation_w - power_consumption_w
    is_power_positive = power_margin_w >= 0.0

    # Battery backup duration (hours) during eclipse
    backup_time_hours = round(battery_capacity_wh / max(1.0, power_consumption_w), 2)
    # Average Mars eclipse time is ~45 minutes (0.75 hr)
    eclipse_survivable = backup_time_hours >= 0.75

    is_flight_ready = is_mass_valid and is_budget_valid and is_power_positive and eclipse_survivable and len(req.selected_instruments) > 0

    warnings = []
    if not is_mass_valid:
        warnings.append(f"MASS OVERLOAD: Satellite weighs {round(total_mass_kg, 1)} kg (Limit: {mass_limit} kg). Remove or downgrade components.")
    if not is_budget_valid:
        warnings.append(f"BUDGET EXCEEDED: Total cost is {total_cost_credits:,} credits (Limit: {int(starting_budget):,} credits).")
    if not is_power_positive:
        warnings.append(f"POWER DEFICIT: Consumption ({round(power_consumption_w, 1)}W) exceeds solar generation ({round(power_generation_w, 1)}W).")
    if not eclipse_survivable:
        warnings.append(f"ECLIPSE RISK: Battery backup duration ({backup_time_hours} hrs) is insufficient for Mars 45-min shadow passes.")
    if len(req.selected_instruments) == 0:
        warnings.append("NO SCIENTIFIC PAYLOAD: Select at least one scientific instrument to collect data.")

    return {
        "total_mass_kg": round(total_mass_kg, 2),
        "mass_limit_kg": mass_limit,
        "is_mass_valid": is_mass_valid,
        "total_cost_credits": total_cost_credits,
        "remaining_budget_credits": remaining_budget,
        "is_budget_valid": is_budget_valid,
        "power_generation_w": round(power_generation_w, 1),
        "power_consumption_w": round(power_consumption_w, 1),
        "power_margin_w": round(power_margin_w, 1),
        "is_power_positive": is_power_positive,
        "battery_capacity_wh": battery_capacity_wh,
        "backup_time_hours": backup_time_hours,
        "eclipse_survivable": eclipse_survivable,
        "data_storage_mb": data_storage_mb,
        "data_rate_mbps": data_rate_mbps,
        "is_flight_ready": is_flight_ready,
        "warnings": warnings,
        "educational_formulas": {
            "mass_formula": "Total mass = Sum of all component and instrument masses",
            "energy_formula": "Energy = Power (Watts) × Time (Hours)",
            "battery_backup_formula": "Backup Time = Battery Energy (Wh) ÷ Power Consumption (W)",
            "solar_flux_formula": "Solar Generation = Solar Cell Efficiency × Surface Area × Solar Irradiance (~586 W/m² at Mars)"
        }
    }

class MapGenerationRequest(BaseModel):
    width: int = 10
    height: int = 10
    seed: Optional[int] = 42

@router.post("/rover/generate-map")
def generate_mars_surface_map(req: MapGenerationRequest):
    """Generate a procedural, balanced tile-based Mars surface map with terrain hazards and science sites."""
    random.seed(req.seed or 42)
    grid = []
    
    # Probabilities for terrain
    terrain_keys = ["FLAT", "ROCKS", "SAND", "CRATER", "SCIENCE"]
    weights = [0.55, 0.20, 0.12, 0.08, 0.05]

    for y in range(req.height):
        row = []
        for x in range(req.width):
            # Origin is always FLAT
            if x == 0 and y == 0:
                t_type = "FLAT"
            else:
                t_type = random.choices(terrain_keys, weights=weights)[0]
            
            tile_info = TERRAIN_TYPES[t_type]
            row.append({
                "x": x,
                "y": y,
                "type": t_type,
                "name": tile_info["name"],
                "energy_cost": tile_info["energy_cost"],
                "risk": tile_info["risk"],
                "icon": tile_info["icon"],
                "color": tile_info["color"],
                "scanned": False,
                "has_sample": t_type == "SCIENCE" or (t_type == "ROCKS" and random.random() < 0.35)
            })
        grid.append(row)

    return {
        "width": req.width,
        "height": req.height,
        "starting_pos": {"x": 0, "y": 0},
        "grid": grid,
        "total_science_sites": sum(1 for row in grid for tile in row if tile["type"] == "SCIENCE")
    }

class MarsRewardClaimRequest(BaseModel):
    game_mode: str # SATELLITE, ROVER, COMBINED
    mission_id: str
    science_collected: int
    score: int
    summary: str

@router.post("/expedition/reward")
def claim_mars_expedition_reward(req: MarsRewardClaimRequest):
    """Bridge Mars Exploration achievements and score directly into Space Agency persistent HQ."""
    rp_awarded = max(15, int(req.science_collected * 0.75))
    funds_awarded_m = round(max(5.0, (req.score / 100.0) * 12.0), 1)

    # Persist directly into shared Agency profile (no duplicate DB)
    persisted = False
    try:
        import sys
        if "/Users/subham/code/Lucy" not in sys.path:
            sys.path.insert(0, "/Users/subham/code/Lucy")
        from backend.app.api.agency import load_agency_profile, save_agency_profile
        profile = load_agency_profile()
        profile["funds_usd"] = float(profile.get("funds_usd", 0.0)) + (funds_awarded_m * 1_000_000.0)
        profile["research_points"] = int(profile.get("research_points", 0)) + rp_awarded
        profile["reputation"] = min(100, int(profile.get("reputation", 50)) + 8)

        new_log = {
            "mission_id": f"MARS-{req.game_mode}-{req.mission_id}",
            "mission_name": f"Mars Exploration: {req.game_mode} ({req.mission_id})",
            "score": req.score,
            "rank": "NASA FLIGHT CERTIFIED" if req.score >= 80 else "MISSION COMPLETE",
            "payout_usd": funds_awarded_m * 1_000_000.0,
            "rp_earned": rp_awarded,
            "date": "2026-11-15",
            "details": req.summary
        }
        logs = profile.get("completed_mission_logs", [])
        logs.insert(0, new_log)
        profile["completed_mission_logs"] = logs[:25]
        save_agency_profile(profile)
        persisted = True
    except Exception as e:
        print(f"Mars reward persistence caution: {e}")

    return {
        "status": "SUCCESS",
        "game_mode": req.game_mode,
        "mission_id": req.mission_id,
        "score": req.score,
        "rewards": {
            "research_points": rp_awarded,
            "capital_funding_millions": funds_awarded_m,
            "reputation_gain": 8
        },
        "persisted_to_hq": persisted,
        "message": f"NASA / Space Agency Directorate confirmed {req.game_mode} expedition telemetry. +{rp_awarded} RP and +${funds_awarded_m}M deposited."
    }

# -----------------------------------------------------------------------------
# 5. MULTIPLAYER 4-PLAYER COLLABORATIVE EXPEDITION SYSTEM
# -----------------------------------------------------------------------------
MARS_MULTIPLAYER_ROLES = {
    "ORBITAL_SATELLITE_LEAD": {
        "title": "Orbital Systems & Bus Lead",
        "description": "Configures microsatellite subsystems, solar array deployment, orbit telemetry, and instruments.",
        "icon": "🛰️"
    },
    "SURFACE_ROVER_DRIVER": {
        "title": "Surface Rover Driver",
        "description": "Executes surface pathfinding, hazard evasion, wheel drive telemetry, and battery preservation.",
        "icon": "🚜"
    },
    "SCIENCE_PAYLOAD_DIRECTOR": {
        "title": "Science Payload Director",
        "description": "Directs rock spectrometry, core sample drilling, flash memory management, and scout site selection.",
        "icon": "🔬"
    },
    "COMMS_MISSION_DIRECTOR": {
        "title": "Communications & Flight Director",
        "description": "Manages light delay queues, direct-to-Earth uplinks, satellite relay passes, and mission debrief.",
        "icon": "📡"
    }
}

class MarsPlayerSession(BaseModel):
    player_id: str
    callsign: str
    role: str
    is_ready: bool = False
    connected_at: float = Field(default_factory=time.time)

class MarsMultiplayerRoomState(BaseModel):
    room_code: str
    host_player_id: str
    mode: str = "COMBINED" # SATELLITE, ROVER, COMBINED
    max_players: int = 4
    players: Dict[str, MarsPlayerSession] = Field(default_factory=dict)
    satellite_state: Dict[str, Any] = Field(default_factory=lambda: {
        "components": {
            "STRUCTURE": "STR_HEX_50",
            "SOLAR_PANELS": "SOL_DEPLOYABLE",
            "BATTERY": "BAT_LIS_200",
            "COMMUNICATION": "COM_PARABOLIC",
            "COMPUTER": "OBC_DUAL_CORE",
            "ATTITUDE_CONTROL": "ADCS_REACTION_WHEEL",
            "THERMAL_CONTROL": "THM_HEAT_PIPE",
            "PROPULSION": "PROP_MONO_HYD"
        },
        "instruments": ["INST_OPTICAL", "INST_THERMAL_IR"],
        "is_launched": False,
        "orbit_inserted": False,
        "science_collected": 0,
        "identified_sites": ["JEZERO_DELTA", "COLUMBIA_HILLS", "GALE_SEDIMENTS"]
    })
    rover_state: Dict[str, Any] = Field(default_factory=lambda: {
        "pos": {"x": 0, "y": 0},
        "energy": 100,
        "flash_mb": 0,
        "samples_collected": 0,
        "visited_coords": [[0, 0]],
        "scanned_coords": [],
        "target_site": "JEZERO_DELTA"
    })
    expedition_stage: int = 1
    chat_messages: List[Dict[str, Any]] = Field(default_factory=list)
    event_log: List[Dict[str, Any]] = Field(default_factory=list)
    version: int = 1
    created_at: float = Field(default_factory=time.time)

# In-memory session store
ACTIVE_MARS_ROOMS: Dict[str, MarsMultiplayerRoomState] = {}

class CreateMarsRoomRequest(BaseModel):
    room_code: Optional[str] = None
    callsign: str = "Commander"
    role: str = "COMMS_MISSION_DIRECTOR"
    mode: str = "COMBINED"

class JoinMarsRoomRequest(BaseModel):
    room_code: str
    callsign: str
    role: str

class MarsRoomActionRequest(BaseModel):
    player_id: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class MarsRoomChatRequest(BaseModel):
    player_id: str
    message: str

@router.get("/multiplayer/roles")
def get_mars_multiplayer_roles():
    """Return available collaborative roles for Mars missions."""
    return MARS_MULTIPLAYER_ROLES

@router.post("/multiplayer/room/create")
def create_mars_multiplayer_room(req: CreateMarsRoomRequest):
    """Create a collaborative 4-player Mars Expedition room."""
    code = (req.room_code or f"MARS-{uuid.uuid4().hex[:4].upper()}").upper()
    if code in ACTIVE_MARS_ROOMS:
        code = f"{code}-{uuid.uuid4().hex[:2].upper()}"

    role = req.role if req.role in MARS_MULTIPLAYER_ROLES else "COMMS_MISSION_DIRECTOR"
    player_id = f"PL-{uuid.uuid4().hex[:6]}"

    host_player = MarsPlayerSession(
        player_id=player_id,
        callsign=req.callsign,
        role=role,
        is_ready=True
    )

    room = MarsMultiplayerRoomState(
        room_code=code,
        host_player_id=player_id,
        mode=req.mode,
        players={player_id: host_player},
        event_log=[{
            "time": time.time(),
            "actor": req.callsign,
            "text": f"Created expedition room {code} as {MARS_MULTIPLAYER_ROLES[role]['title']}."
        }]
    )
    ACTIVE_MARS_ROOMS[code] = room

    return {
        "status": "SUCCESS",
        "room_code": code,
        "player_id": player_id,
        "player": host_player,
        "room": room
    }

@router.post("/multiplayer/room/join")
def join_mars_multiplayer_room(req: JoinMarsRoomRequest):
    """Join an existing 4-player Mars Expedition room."""
    code = req.room_code.upper()
    if code not in ACTIVE_MARS_ROOMS:
        raise HTTPException(status_code=404, detail=f"Mars room '{code}' not found.")

    room = ACTIVE_MARS_ROOMS[code]
    if len(room.players) >= room.max_players:
        raise HTTPException(status_code=400, detail="Mars expedition is full (maximum 4 players).")

    # Check role collision
    taken_roles = {p.role for p in room.players.values()}
    role = req.role
    if role in taken_roles:
        # Assign next available role
        available = [r for r in MARS_MULTIPLAYER_ROLES if r not in taken_roles]
        if not available:
            raise HTTPException(status_code=400, detail="All specialist roles are occupied.")
        role = available[0]

    player_id = f"PL-{uuid.uuid4().hex[:6]}"
    player = MarsPlayerSession(
        player_id=player_id,
        callsign=req.callsign,
        role=role,
        is_ready=True
    )
    room.players[player_id] = player
    room.version += 1
    room.event_log.append({
        "time": time.time(),
        "actor": req.callsign,
        "text": f"Joined mission room as {MARS_MULTIPLAYER_ROLES[role]['title']}."
    })

    return {
        "status": "SUCCESS",
        "room_code": code,
        "player_id": player_id,
        "player": player,
        "room": room
    }

@router.get("/multiplayer/room/{room_code}")
def get_mars_multiplayer_room_state(room_code: str):
    """Fetch authoritative server state for Mars room."""
    code = room_code.upper()
    if code not in ACTIVE_MARS_ROOMS:
        raise HTTPException(status_code=404, detail=f"Mars room '{code}' not found.")
    return ACTIVE_MARS_ROOMS[code]

@router.post("/multiplayer/room/{room_code}/action")
def dispatch_mars_multiplayer_action(room_code: str, req: MarsRoomActionRequest):
    """Execute authoritative gameplay actions synchronized across players."""
    code = room_code.upper()
    if code not in ACTIVE_MARS_ROOMS:
        raise HTTPException(status_code=404, detail=f"Mars room '{code}' not found.")

    room = ACTIVE_MARS_ROOMS[code]
    if req.player_id not in room.players:
        raise HTTPException(status_code=403, detail="Player not in this room.")

    player = room.players[req.player_id]
    actor = player.callsign
    act = req.action.upper()
    p = req.payload

    if act == "UPDATE_SATELLITE":
        # Satellite design update
        if "components" in p:
            room.satellite_state["components"].update(p["components"])
        if "instruments" in p:
            room.satellite_state["instruments"] = p["instruments"]
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": "Updated orbital satellite component manifest."
        })

    elif act == "LAUNCH_SATELLITE":
        room.satellite_state["is_launched"] = True
        room.satellite_state["orbit_inserted"] = True
        room.expedition_stage = max(room.expedition_stage, 2)
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": "Ignited launch vehicle; inserted satellite into 300 km Mars polar orbit."
        })

    elif act == "MOVE_ROVER":
        x = max(0, min(9, int(p.get("x", 0))))
        y = max(0, min(9, int(p.get("y", 0))))
        energy_cost = int(p.get("energy_cost", 5))
        room.rover_state["pos"] = {"x": x, "y": y}
        room.rover_state["energy"] = max(0, room.rover_state["energy"] - energy_cost)
        if [x, y] not in room.rover_state["visited_coords"]:
            room.rover_state["visited_coords"].append([x, y])
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Navigated rover to grid ({x}, {y}). -{energy_cost}E battery drain."
        })

    elif act == "SAMPLE_TILE":
        storage_cost = int(p.get("storage_cost", 15))
        room.rover_state["flash_mb"] = min(100, room.rover_state["flash_mb"] + storage_cost)
        room.rover_state["samples_collected"] += 1
        pos = room.rover_state["pos"]
        if [pos["x"], pos["y"]] not in room.rover_state["scanned_coords"]:
            room.rover_state["scanned_coords"].append([pos["x"], pos["y"]])
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Drilled sample at ({pos['x']}, {pos['y']}). +{storage_cost} MB flash stored."
        })

    elif act == "TRANSMIT_DATA":
        cleared_mb = room.rover_state["flash_mb"]
        room.rover_state["flash_mb"] = 0
        points = int(cleared_mb * 2)
        room.satellite_state["science_collected"] += points
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Downlinked {cleared_mb} MB telemetry via orbital relay. +{points} science yield."
        })

    elif act == "SELECT_SCOUT_SITE":
        site_id = p.get("site_id", "JEZERO_DELTA")
        room.rover_state["target_site"] = site_id
        room.expedition_stage = max(room.expedition_stage, 4)
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Confirmed orbital scout landing site: {site_id}."
        })

    elif act == "ADVANCE_STAGE":
        room.expedition_stage = min(7, room.expedition_stage + 1)
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Advanced expedition to Stage {room.expedition_stage}."
        })

    else:
        room.event_log.append({
            "time": time.time(),
            "actor": actor,
            "text": f"Executed command: {act}."
        })

    room.version += 1
    return {"status": "SUCCESS", "version": room.version, "room": room}

@router.post("/multiplayer/room/{room_code}/chat")
def post_mars_multiplayer_chat(room_code: str, req: MarsRoomChatRequest):
    """Post chat message to Mars expedition room."""
    code = room_code.upper()
    if code not in ACTIVE_MARS_ROOMS:
        raise HTTPException(status_code=404, detail=f"Mars room '{code}' not found.")

    room = ACTIVE_MARS_ROOMS[code]
    if req.player_id not in room.players:
        raise HTTPException(status_code=403, detail="Player not in this room.")

    player = room.players[req.player_id]
    msg = {
        "id": uuid.uuid4().hex[:8],
        "time": time.time(),
        "sender": player.callsign,
        "role": player.role,
        "role_icon": MARS_MULTIPLAYER_ROLES[player.role]["icon"],
        "text": req.message.strip()
    }
    room.chat_messages.append(msg)
    room.version += 1
    return {"status": "SUCCESS", "chat": msg, "messages": room.chat_messages[-30:]}
