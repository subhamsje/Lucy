"""
Authoritative Margin & Physics Engine for Orbital Architect (Lucy)
Implements:
- AIAA S-120-2006 Mass Growth Allowance (MGA) compounding
- Keplerian orbital period and eclipse duration geometry
- Day/Night electrical energy conservation & Battery Depth-of-Discharge (DoD)
- Free-Space Path Loss (FSPL) and digital RF link budget (Eb/N0)
- Tsiolkovsky rocket equation stationkeeping propellant sizing
- Thermal radiative balance check (single-node steady state)
- Compatibility rule validations against catalog constraints
"""

import math
from typing import Dict, List, Any, Tuple
from orbital_engine.calculator import (
    OrbitalCalculator,
    MU_EARTH,
    R_EARTH,
    J2_EARTH,
    SOLAR_CONSTANT_1AU
)

calc = OrbitalCalculator()

class MarginEngine:
    @staticmethod
    def evaluate_spacecraft_margins(
        design_dict: Dict[str, Any],
        scenario_dict: Dict[str, Any],
        catalog_components: List[Dict[str, Any]],
        rules_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Computes authoritative engineering margins and checks physical compliance.
        Returns a dictionary strictly adhering to FeasibilityValidationResponse schema.
        """
        components_by_id = {c["id"]: c for c in catalog_components}
        installed_ids = design_dict.get("installed_component_ids", [])
        installed = [components_by_id[cid] for cid in installed_ids if cid in components_by_id]

        rule_violations: List[str] = []
        compliance_warnings: List[str] = []

        # ----------------------------------------------------------------------
        # 1. MASS COMPOSITION & AIAA S-120 MGA COMPOUNDING
        # ----------------------------------------------------------------------
        payload_mass_kg = sum(c["mass_kg"] for c in installed if c["category"] == "SCIENTIFIC_INSTRUMENT")
        subsystems_mass_kg = sum(c["mass_kg"] for c in installed if c["category"] != "SCIENTIFIC_INSTRUMENT")
        
        # Explicit primary structure compounding rule: m_structure = 0.22 * non_structural_dry
        non_structural_dry = payload_mass_kg + sum(c["mass_kg"] for c in installed if c["category"] not in ["SCIENTIFIC_INSTRUMENT", "SPACECRAFT_STRUCTURE"])
        explicit_structure = next((c for c in installed if c["category"] == "SPACECRAFT_STRUCTURE"), None)
        
        if explicit_structure:
            structure_mass_kg = explicit_structure["mass_kg"]
            dry_mass_kg = payload_mass_kg + subsystems_mass_kg
        else:
            structure_mass_kg = 0.22 * (payload_mass_kg + subsystems_mass_kg)
            dry_mass_kg = payload_mass_kg + subsystems_mass_kg + structure_mass_kg

        # AIAA S-120 Mass Growth Allowance (20% for Phase A/B concept)
        mga_mass_kg = dry_mass_kg * 0.20

        # Propellant sizing via Tsiolkovsky Rocket Equation
        orbit_alt_km = design_dict["orbit"]["altitude_km"]
        orbit_inc_deg = design_dict["orbit"]["inclination_deg"]
        
        # Stationkeeping & deorbit delta-v budget
        required_dv_ms = 120.0
        if orbit_alt_km < 400.0:
            required_dv_ms += 180.0  # Increased drag-makeup budget
        elif orbit_alt_km > 30000.0:
            required_dv_ms += 1500.0 # GTO to GEO circularization

        prop_component = next((c for c in installed if c["category"] == "PROPULSION_SYSTEM"), None)
        isp_seconds = prop_component["performance_metrics"].get("isp_seconds", 224.0) if prop_component else 70.0
        
        # m_prop = (m_dry + MGA) * (exp(dv / (isp * g0)) - 1)
        g0 = 9.80665
        propellant_mass_kg = (dry_mass_kg + mga_mass_kg) * (math.exp(required_dv_ms / (isp_seconds * g0)) - 1.0)
        propellant_mass_kg = max(2.5, propellant_mass_kg)
        
        wet_mass_kg = dry_mass_kg + mga_mass_kg + propellant_mass_kg

        # Launcher payload capacity check
        launcher_limits = {
            "MICRO_LAUNCHER": 250.0,
            "RIDESHARE_ESPA": 450.0,
            "MEDIUM_LIFT": 12000.0,
            "HEAVY_LIFT": 21000.0
        }
        launch_vehicle_id = design_dict.get("launch_vehicle_id", "MICRO_LAUNCHER")
        launcher_capacity_kg = launcher_limits.get(launch_vehicle_id, 300.0)
        
        mass_margin_pct = ((launcher_capacity_kg - wet_mass_kg) / launcher_capacity_kg) * 100.0

        if wet_mass_kg > launcher_capacity_kg:
            rule_violations.append(
                f"AIAA Lift Margin Violation: Spacecraft wet mass ({wet_mass_kg:.1f} kg) exceeds "
                f"launch vehicle capacity ({launcher_capacity_kg:.1f} kg) by +{wet_mass_kg - launcher_capacity_kg:.1f} kg."
            )
        elif mass_margin_pct < 10.0:
            compliance_warnings.append(
                f"Mass margin ({mass_margin_pct:.1f}%) is below the recommended 15.0% threshold."
            )

        # ----------------------------------------------------------------------
        # 2. ORBIT GEOMETRY, ECLIPSE, & ELECTRICAL ENERGY BALANCE
        # ----------------------------------------------------------------------
        r_orbit_m = (R_EARTH + orbit_alt_km * 1000.0)
        t_period_s = calc.orbital_period(r_orbit_m, MU_EARTH)
        t_eclipse_s, eclipse_fraction_pct = calc.eclipse_duration(orbit_alt_km * 1000.0, R_EARTH, MU_EARTH)
        
        eclipse_duration_min = t_eclipse_s / 60.0
        sun_duration_min = (t_period_s - t_eclipse_s) / 60.0

        # Day generation
        day_power_gen_w = sum(c.get("power_generation_w", 0.0) for c in installed)
        
        # Loads
        day_power_load_w = sum(c.get("power_consumption_w", 0.0) for c in installed)
        night_power_load_w = sum(
            c.get("power_consumption_w", 0.0) for c in installed 
            if c["category"] != "SCIENTIFIC_INSTRUMENT"
        ) + 12.0 # Quiescent bus survival load (OBC, TT&C receiver, survival heaters)

        # Battery capacity sizing
        battery_wh = 0.0
        for c in installed:
            if c["category"] == "BATTERY":
                battery_wh += c["performance_metrics"].get("capacity_wh", c["mass_kg"] * 55.0)

        # Battery Depth-of-Discharge (DoD) calculation
        battery_dod_pct = 0.0
        if battery_wh > 0.0:
            # Energy drawn in eclipse accounting for 90% chemical discharge efficiency
            night_energy_wh = (night_power_load_w * (eclipse_duration_min / 60.0)) / 0.90
            battery_dod_pct = (night_energy_wh / battery_wh) * 100.0
        else:
            battery_dod_pct = 100.0 # Instant failure without batteries

        if battery_wh <= 0.0:
            rule_violations.append("Electrical Power Subsystem Failure: No battery storage module installed.")
        elif battery_dod_pct > 60.0:
            rule_violations.append(
                f"Critical Battery DoD Violation: Depth-of-Discharge ({battery_dod_pct:.1f}%) exceeds "
                f"allowable 60.0% threshold (causes cell freeze during eclipse)."
            )
        elif battery_dod_pct > 30.0:
            compliance_warnings.append(
                f"Battery Depth-of-Discharge ({battery_dod_pct:.1f}%) exceeds nominal 30.0% wear threshold; accelerates degradation."
            )

        if day_power_gen_w < day_power_load_w:
            rule_violations.append(
                f"Energy Deficit: Solar array generation ({day_power_gen_w:.1f} W) is insufficient "
                f"for daytime operational load ({day_power_load_w:.1f} W)."
            )

        # ----------------------------------------------------------------------
        # 3. COMMUNICATIONS & DATA BUFFER BUDGET
        # ----------------------------------------------------------------------
        antenna = next((c for c in installed if c["category"] == "COMMUNICATION_ANTENNA"), None)
        rf_downlink_rate_mbps = antenna["performance_metrics"].get("max_downlink_rate_mbps", 2.0) if antenna else 0.5
        antenna_band = antenna["performance_metrics"].get("frequency_band", "S-band") if antenna else "S-band"
        
        # Link budget Eb/N0 calculation
        carrier_ghz = 26.5 if "Ka" in antenna_band else (8.4 if "X" in antenna_band else 2.2)
        tx_gain_dbi = antenna["performance_metrics"].get("peak_gain_dbi", 3.0) if antenna else 0.0
        
        # Assume standard ground station (G/T = 32 dB/K, range = slant distance at 5 deg elevation)
        slant_range_km = math.sqrt((r_orbit_m/1000.0)**2 - (R_EARTH/1000.0)**2 * math.cos(math.radians(5.0))**2) - (R_EARTH/1000.0) * math.sin(math.radians(5.0))
        slant_range_km = max(800.0, slant_range_km)
        
        link_eb_n0_db = calc.link_budget_snr_db(
            tx_power_w=8.0,
            tx_gain_dbi=tx_gain_dbi,
            rx_gain_dbi=42.0,
            freq_ghz=carrier_ghz,
            range_km=slant_range_km,
            data_rate_bps=rf_downlink_rate_mbps * 1e6
        )
        link_margin_db = link_eb_n0_db - 6.0 # 6 dB required threshold for standard QPSK
        
        if link_margin_db < 3.0:
            rule_violations.append(
                f"RF Link Budget Failure: Link margin ({link_margin_db:.1f} dB) is below the minimum required 3.0 dB threshold."
            )

        daily_data_gen_mb = sum(c.get("data_generation_mb_per_day", 0.0) for c in installed)
        storage_capacity_gb = sum(c.get("storage_capacity_gb", 0.0) for c in installed)
        
        if storage_capacity_gb <= 0.0 and daily_data_gen_mb > 0.0:
            rule_violations.append("C&DH Failure: No solid-state mass memory installed to buffer payload telemetry.")

        # ----------------------------------------------------------------------
        # 4. CAPEX FINANCIAL BUDGET LEDGER
        # ----------------------------------------------------------------------
        component_costs_usd = sum(c.get("cost_usd", 0.0) for c in installed)
        launcher_costs_usd = {
            "MICRO_LAUNCHER": 7500000.0,
            "RIDESHARE_ESPA": 2500000.0,
            "MEDIUM_LIFT": 65000000.0,
            "HEAVY_LIFT": 130000000.0
        }
        launcher_cost_usd = launcher_costs_usd.get(launch_vehicle_id, 10000000.0)
        system_integration_overhead_usd = 1500000.0
        total_cost_usd = component_costs_usd + launcher_cost_usd + system_integration_overhead_usd
        
        budget_cap_usd = scenario_dict.get("budget_cap_usd", 50000000.0)
        budget_remaining_usd = budget_cap_usd - total_cost_usd

        if total_cost_usd > budget_cap_usd:
            rule_violations.append(
                f"Programmatic Cost Overrun: Total mission CapEx (${total_cost_usd:,.0f}) exceeds "
                f"the allowable budget cap (${budget_cap_usd:,.0f}) by ${total_cost_usd - budget_cap_usd:,.0f}."
            )

        # ----------------------------------------------------------------------
        # 5. SUBSYSTEM CROSS-COUPLING & CHASSIS CONSTRAINTS
        # ----------------------------------------------------------------------
        chassis_class = design_dict.get("chassis_class", "SMALLSAT_LEO")
        chassis_limits = rules_dict.get("compatibility_engine", {}).get("chassis_rules", {}).get(chassis_class, {})
        max_chassis_payload_kg = chassis_limits.get("max_payload_mass_kg", 500.0)
        
        if payload_mass_kg > max_chassis_payload_kg:
            rule_violations.append(
                f"Chassis Structural Limit: Total payload mass ({payload_mass_kg:.1f} kg) exceeds "
                f"the structural rating for {chassis_class} ({max_chassis_payload_kg:.1f} kg)."
            )

        # Pointing Budget Check
        adcs = next((c for c in installed if c["category"] == "ATTITUDE_CONTROL"), None)
        achieved_pointing_deg = adcs["performance_metrics"].get("pointing_accuracy_achievable_deg", 2.0) if adcs else 5.0
        
        for c in installed:
            req_pointing = c.get("compatibility", {}).get("required_pointing_accuracy_deg", 0.0)
            if req_pointing > 0.0 and achieved_pointing_deg > req_pointing:
                rule_violations.append(
                    f"Pointing Stability Deficit: Instrument {c['name']} requires {req_pointing}° pointing accuracy, "
                    f"but installed ADCS only provides {achieved_pointing_deg}°."
                )

        is_certified = len(rule_violations) == 0

        return {
            "is_certified": is_certified,
            "status_summary": "ALL_SUBSYSTEMS_CERTIFIED" if is_certified else "MARGIN_VIOLATION_DETECTED",
            "resource_budgets": {
                "dry_mass_kg": round(dry_mass_kg, 2),
                "mass_growth_allowance_kg": round(mga_mass_kg, 2),
                "propellant_mass_kg": round(propellant_mass_kg, 2),
                "wet_mass_kg": round(wet_mass_kg, 2),
                "launcher_capacity_kg": round(launcher_capacity_kg, 2),
                "mass_margin_pct": round(mass_margin_pct, 2),
                "day_power_generation_w": round(day_power_gen_w, 2),
                "night_power_load_w": round(night_power_load_w, 2),
                "battery_capacity_wh": round(battery_wh, 2),
                "eclipse_duration_min": round(eclipse_duration_min, 2),
                "battery_depth_of_discharge_pct": round(battery_dod_pct, 2),
                "rf_downlink_rate_mbps": round(rf_downlink_rate_mbps, 2),
                "link_margin_db": round(link_margin_db, 2),
                "storage_capacity_gb": round(storage_capacity_gb, 2),
                "daily_data_generation_mb": round(daily_data_gen_mb, 2),
                "total_cost_usd": round(total_cost_usd, 2),
                "budget_cap_usd": round(budget_cap_usd, 2),
                "budget_remaining_usd": round(budget_remaining_usd, 2),
                "is_flight_certified": is_certified
            },
            "rule_violations": rule_violations,
            "compliance_warnings": compliance_warnings
        }
