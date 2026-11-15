"""
Authoritative 1,000-Point Scoring Engine for Orbital Architect (Lucy)
Evaluates mission results objectively against charter objectives, physical margins, and flight survival.
"""

from typing import Dict, Any

class ScoringEngine:
    @staticmethod
    def calculate_mission_score(
        simulation_data: Dict[str, Any],
        scenario_dict: Dict[str, Any],
        difficulty: str = "SPECIALIST"
    ) -> Dict[str, Any]:
        """
        Computes transparent multi-attribute mission score (0 - 1000+ points).
        Enforces failure gates, bonuses, penalties, and difficulty multipliers.
        """
        # Catastrophic Failure Gate
        if simulation_data.get("is_catastrophic_failure", False):
            return {
                "final_score": 0,
                "honor_grade": "F (CATASTROPHIC LOSS)",
                "outcome": "CATASTROPHIC_FAILURE",
                "failure_reason": simulation_data.get("failure_reason", "Hardware lost during flight operations"),
                "score_breakdown": {
                    "objective_fulfillment": 0.0,
                    "science_achievement": 0.0,
                    "mass_margin_rigor": 0.0,
                    "energy_efficiency": 0.0,
                    "budget_efficiency": 0.0,
                    "comms_performance": 0.0,
                    "lifetime_survival": 0.0,
                    "hardware_health": 0.0,
                    "propulsion_sustainability": 0.0,
                    "team_collaboration": 0.0,
                    "bonuses": 0.0,
                    "penalties": 0.0
                }
            }

        budgets = simulation_data.get("resource_budgets", {})
        downlinked_gb = simulation_data.get("total_science_gb", 0.0)
        target_gb = scenario_dict.get("scientific_requirements", {}).get("primary_data_threshold_gb", 400.0)
        budget_cap = scenario_dict.get("budget_cap_usd", 35000000.0)
        total_cost = budgets.get("total_cost_usd", budget_cap)
        dod_avg = budgets.get("battery_depth_of_discharge_pct", 30.0)
        mass_margin_pct = budgets.get("mass_margin_pct", 15.0)
        days_survived = simulation_data.get("operational_days_survived", scenario_dict.get("mission_duration_days", 180))
        target_days = scenario_dict.get("mission_duration_days", 180)
        soh_pct = simulation_data.get("hardware_soh_pct", 95.0)
        deorbit_compliant = simulation_data.get("deorbit_compliant", True)

        # 1. Primary Objective Fulfillment (Max 250)
        s_obj = 250.0 * min(1.0, downlinked_gb / target_gb)

        # 2. Scientific Achievement & Resolution Factor (Max 150)
        science_ratio = min(1.5, downlinked_gb / target_gb)
        s_sci = 150.0 * science_ratio

        # 3. Engineering Margin Rigor (Max 120)
        s_margin = 120.0 * max(0.0, min(1.0, (mass_margin_pct - 5.0) / 15.0))

        # 4. Energy Efficiency (Max 100)
        s_power = 100.0 * max(0.0, 1.0 - (dod_avg / 60.0))

        # 5. Budget Responsibility (Max 100)
        s_budget = 100.0 * max(0.0, min(1.0, (budget_cap - total_cost) / (budget_cap * 0.5)))

        # 6. Communications Performance (Max 80)
        s_comms = 80.0 * (1.0 if simulation_data.get("buffer_overflows", 0) == 0 else 0.5)

        # 7. Lifetime & Survival (Max 70)
        s_life = 70.0 * min(1.0, days_survived / target_days)

        # 8. Hardware Health (Max 50)
        s_health = 50.0 * (soh_pct / 100.0)

        # 9. Propulsion Sustainability / Deorbit Reserve (Max 40)
        s_prop = 40.0 * (1.0 if deorbit_compliant else 0.0)

        # 10. Multi-Seat Team Collaboration (Max 40)
        s_team = 40.0

        raw_base = (
            s_obj + s_sci + s_margin + s_power + s_budget +
            s_comms + s_life + s_health + s_prop + s_team
        )

        # Bonuses & Deductions
        bonuses = 0.0
        penalties = 0.0
        if total_cost <= budget_cap * 0.60:
            bonuses += 50.0  # Under-Budget Pioneer
        if mass_margin_pct >= 15.0 and mass_margin_pct <= 20.0:
            bonuses += 40.0  # Razor's Edge Mass Discipline
        if not deorbit_compliant:
            penalties += 100.0  # Space Debris Non-Compliance

        # Difficulty Multiplier
        multipliers = {"CADET": 0.85, "SPECIALIST": 1.00, "FLIGHT_DIRECTOR": 1.35}
        diff_mult = multipliers.get(difficulty, 1.00)

        final_score = int(max(0.0, min(1200.0, (raw_base + bonuses - penalties) * diff_mult)))

        if final_score >= 900:
            honor_grade = "A+ (MASTER ARCHITECT)"
            outcome = "SUCCESS"
        elif final_score >= 800:
            honor_grade = "A (FLIGHT QUALIFIED)"
            outcome = "SUCCESS"
        elif final_score >= 700:
            honor_grade = "B (COMMERCIAL GRADE)"
            outcome = "SUCCESS"
        elif final_score >= 500:
            honor_grade = "C (PARTIAL SUCCESS)"
            outcome = "PARTIAL_SUCCESS"
        else:
            honor_grade = "D (SUB-OPTIMAL)"
            outcome = "PARTIAL_SUCCESS"

        return {
            "final_score": final_score,
            "honor_grade": honor_grade,
            "outcome": outcome,
            "score_breakdown": {
                "objective_fulfillment": round(s_obj, 1),
                "science_achievement": round(s_sci, 1),
                "mass_margin_rigor": round(s_margin, 1),
                "energy_efficiency": round(s_power, 1),
                "budget_efficiency": round(s_budget, 1),
                "comms_performance": round(s_comms, 1),
                "lifetime_survival": round(s_life, 1),
                "hardware_health": round(s_health, 1),
                "propulsion_sustainability": round(s_prop, 1),
                "team_collaboration": round(s_team, 1),
                "bonuses": bonuses,
                "penalties": penalties
            }
        }
