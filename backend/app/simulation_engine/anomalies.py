"""
Flight Operations Discrete-Event & Anomaly Generator for Orbital Architect
Generates reproducible space weather, subsystem wear, and recovery decision prompts based on PRNG seeds.
"""

import random
from typing import List, Dict, Any

class AnomalyEngine:
    @staticmethod
    def generate_flight_anomalies(
        seed: int,
        scenario_id: str,
        orbit_altitude_km: float,
        orbit_inclination_deg: float,
        difficulty: str = "SPECIALIST"
    ) -> List[Dict[str, Any]]:
        """
        Generates deterministic in-flight anomalies.
        Higher difficulty and extreme orbits produce higher event counts.
        """
        rng = random.Random(seed)
        events = []

        # 1. Solar Storm / CME (High probability in polar/interplanetary or Flight Director)
        if orbit_inclination_deg > 80.0 or "DEEP_SPACE" in scenario_id or difficulty == "FLIGHT_DIRECTOR":
            cme_day = rng.randint(25, 90)
            events.append({
                "event_id": "EVT-CME-01",
                "name": "Coronal Mass Ejection (Solar Particle Event)",
                "category": "SPACE_WEATHER",
                "severity": "CRITICAL",
                "met_day": cme_day,
                "telemetry_symptoms": {
                    "proton_flux_pfu": 1420.0,
                    "array_degradation_expected_pct": 14.5,
                    "single_event_upsets_logged": 3
                },
                "recommended_action": "Slew spacecraft to Survival Safe Attitude and de-energize unshielded optical payloads.",
                "mitigated": True
            })

        # 2. Reaction Wheel Momentum Saturation
        if difficulty in ["SPECIALIST", "FLIGHT_DIRECTOR"]:
            wheel_day = rng.randint(95, 140)
            events.append({
                "event_id": "EVT-ADCS-02",
                "name": "Reaction Wheel Momentum Saturation (5,850 RPM)",
                "category": "ATTITUDE_CONTROL",
                "severity": "CAUTION",
                "met_day": wheel_day,
                "telemetry_symptoms": {
                    "wheel_1_rpm": 5850.0,
                    "wheel_2_rpm": 5720.0,
                    "attitude_jitter_arcsec": 14.2
                },
                "recommended_action": "Execute 4-second thruster or magnetorquer momentum desaturation sequence.",
                "mitigated": True
            })

        return events
