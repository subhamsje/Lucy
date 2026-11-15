/**
 * TypeScript Data Models & API Contracts for Orbital Architect (Lucy)
 * Strict 1:1 mirroring of backend Pydantic models.
 */

// ==============================================================================
// 1. ENUMS & CONSTANTS
// ==============================================================================

export type RankTier = 'CADET' | 'SPECIALIST' | 'FLIGHT_DIRECTOR' | 'MASTER_ARCHITECT';

export type MissionRole = 'MISSION_DIRECTOR' | 'SPACECRAFT_ENGINEER' | 'SCIENCE_OFFICER' | 'FLIGHT_OPERATIONS';

export type DifficultyLevel = 'CADET' | 'SPECIALIST' | 'FLIGHT_DIRECTOR';

export type ComponentCategory =
  | 'SCIENTIFIC_INSTRUMENT'
  | 'SOLAR_PANEL'
  | 'BATTERY'
  | 'COMMUNICATION_ANTENNA'
  | 'ONBOARD_COMPUTER'
  | 'PROPULSION_SYSTEM'
  | 'ATTITUDE_CONTROL'
  | 'THERMAL_MANAGEMENT'
  | 'SPACECRAFT_STRUCTURE'
  | 'DATA_STORAGE';

export type ComponentTier = 'BASIC' | 'INTERMEDIATE' | 'ADVANCED';

export type ChassisClass = 'CUBESAT_12U' | 'SMALLSAT_LEO' | 'MEDIUM_BUS' | 'HEAVY_PROBE';

export type SimulationOutcome = 'SUCCESS' | 'PARTIAL_SUCCESS' | 'CATASTROPHIC_FAILURE';

export type EventSeverity = 'ADVISORY' | 'CAUTION' | 'CRITICAL';

// ==============================================================================
// 2. CORE INTERFACES
// ==============================================================================

export interface User {
  id: string;
  callsign: string;
  email: string;
  rank_tier: RankTier;
  engineering_integrity_rating: number;
  created_at: string;
}

export interface OrbitConfiguration {
  altitude_km: number;
  inclination_deg: number;
  eccentricity: number;
  periapsis_km?: number;
  apoapsis_km?: number;
}

export interface ResourceBudgets {
  dry_mass_kg: number;
  mass_growth_allowance_kg: number;
  propellant_mass_kg: number;
  wet_mass_kg: number;
  launcher_capacity_kg: number;
  mass_margin_pct: number;

  day_power_generation_w: number;
  night_power_load_w: number;
  battery_capacity_wh: number;
  eclipse_duration_min: number;
  battery_depth_of_discharge_pct: number;

  rf_downlink_rate_mbps: number;
  link_margin_db: number;

  storage_capacity_gb: number;
  daily_data_generation_mb: number;

  total_cost_usd: number;
  budget_cap_usd: number;
  budget_remaining_usd: number;

  is_flight_certified: boolean;
}

export interface SpacecraftConfiguration {
  id?: string;
  name: string;
  scenario_id: string;
  chassis_class: ChassisClass;
  launch_vehicle_id: string;
  orbit: OrbitConfiguration;
  installed_component_ids: string[];
}

export interface FeasibilityValidationResponse {
  is_certified: boolean;
  status_summary: string;
  resource_budgets: ResourceBudgets;
  rule_violations: string[];
  compliance_warnings: string[];
}

export interface TelemetryFrame {
  met_seconds: number;
  orbit_number: number;
  true_anomaly_deg: number;
  is_in_eclipse: boolean;
  battery_soc_pct: number;
  bus_temperature_c: number;
  data_buffer_used_gb: number;
  reaction_wheel_rpm: number;
  current_downlink_rate_mbps: number;
  cumulative_science_gb: number;
}

export interface SimulationExecutionResponse {
  session_id: string;
  scenario_id: string;
  outcome: SimulationOutcome;
  total_science_gb: number;
  operational_days_survived: number;
  final_eir_score: number;
  honor_grade: string;
  score_breakdown: Record<string, number>;
  anomalies_encountered: Array<Record<string, any>>;
  telemetry_time_series: TelemetryFrame[];
  verification_hash: string;
}

// ==============================================================================
// 3. WEBSOCKET REAL-TIME CONTRACTS
// ==============================================================================

export type WSMessageType =
  | 'CLAIM_ROLE'
  | 'ROLE_ASSIGNED'
  | 'COMPONENT_MUTATION'
  | 'ORBIT_MUTATION'
  | 'STATE_DELTA'
  | 'FRR_VOTE'
  | 'FRR_STATUS'
  | 'TELEMETRY_FRAME'
  | 'ANOMALY_TRIGGERED'
  | 'ANOMALY_RESOLVED'
  | 'CHAT_MESSAGE';

export interface WSMessageEnvelope {
  type: WSMessageType;
  room_id: string;
  sender_callsign: string;
  role?: MissionRole;
  timestamp_utc: string;
  payload: Record<string, any>;
}
