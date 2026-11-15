"""
Pydantic v2 Models & API Contract Definitions for Orbital Architect (Lucy)
Unified schema matching TypeScript types 1:1 with strict aerospace validation.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, EmailStr


# ==============================================================================
# 1. ENUMS & CONSTANTS
# ==============================================================================

class RankTier(str, Enum):
    CADET = "CADET"
    SPECIALIST = "SPECIALIST"
    FLIGHT_DIRECTOR = "FLIGHT_DIRECTOR"
    MASTER_ARCHITECT = "MASTER_ARCHITECT"

class MissionRole(str, Enum):
    MISSION_DIRECTOR = "MISSION_DIRECTOR"
    SPACECRAFT_ENGINEER = "SPACECRAFT_ENGINEER"
    SCIENCE_OFFICER = "SCIENCE_OFFICER"
    FLIGHT_OPERATIONS = "FLIGHT_OPERATIONS"

class DifficultyLevel(str, Enum):
    CADET = "CADET"
    SPECIALIST = "SPECIALIST"
    FLIGHT_DIRECTOR = "FLIGHT_DIRECTOR"

class ComponentCategory(str, Enum):
    SCIENTIFIC_INSTRUMENT = "SCIENTIFIC_INSTRUMENT"
    SOLAR_PANEL = "SOLAR_PANEL"
    BATTERY = "BATTERY"
    COMMUNICATION_ANTENNA = "COMMUNICATION_ANTENNA"
    ONBOARD_COMPUTER = "ONBOARD_COMPUTER"
    PROPULSION_SYSTEM = "PROPULSION_SYSTEM"
    ATTITUDE_CONTROL = "ATTITUDE_CONTROL"
    THERMAL_MANAGEMENT = "THERMAL_MANAGEMENT"
    SPACECRAFT_STRUCTURE = "SPACECRAFT_STRUCTURE"
    DATA_STORAGE = "DATA_STORAGE"

class ComponentTier(str, Enum):
    BASIC = "BASIC"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class ChassisClass(str, Enum):
    CUBESAT_12U = "CUBESAT_12U"
    SMALLSAT_LEO = "SMALLSAT_LEO"
    MEDIUM_BUS = "MEDIUM_BUS"
    HEAVY_PROBE = "HEAVY_PROBE"

class SimulationOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    CATASTROPHIC_FAILURE = "CATASTROPHIC_FAILURE"

class EventSeverity(str, Enum):
    ADVISORY = "ADVISORY"
    CAUTION = "CAUTION"
    CRITICAL = "CRITICAL"


# ==============================================================================
# 2. CORE ENTITY SCHEMAS
# ==============================================================================

class UserBase(BaseModel):
    callsign: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    rank_tier: RankTier
    engineering_integrity_rating: int
    created_at: str

    class Config:
        from_attributes = True


class OrbitConfiguration(BaseModel):
    altitude_km: float = Field(..., ge=150.0, le=1500000.0, description="Altitude in km")
    inclination_deg: float = Field(..., ge=0.0, le=180.0, description="Inclination in degrees")
    eccentricity: float = Field(0.0, ge=0.0, le=0.99, description="Orbital eccentricity")
    periapsis_km: Optional[float] = None
    apoapsis_km: Optional[float] = None


class ResourceBudgets(BaseModel):
    dry_mass_kg: float = Field(..., ge=0.0)
    mass_growth_allowance_kg: float = Field(..., ge=0.0)
    propellant_mass_kg: float = Field(..., ge=0.0)
    wet_mass_kg: float = Field(..., ge=0.0)
    launcher_capacity_kg: float = Field(..., ge=0.0)
    mass_margin_pct: float
    
    day_power_generation_w: float = Field(..., ge=0.0)
    night_power_load_w: float = Field(..., ge=0.0)
    battery_capacity_wh: float = Field(..., ge=0.0)
    eclipse_duration_min: float = Field(..., ge=0.0)
    battery_depth_of_discharge_pct: float = Field(..., ge=0.0, le=100.0)
    
    rf_downlink_rate_mbps: float = Field(..., ge=0.0)
    link_margin_db: float
    
    storage_capacity_gb: float = Field(..., ge=0.0)
    daily_data_generation_mb: float = Field(..., ge=0.0)
    
    total_cost_usd: float = Field(..., ge=0.0)
    budget_cap_usd: float = Field(..., ge=0.0)
    budget_remaining_usd: float
    
    is_flight_certified: bool


class SpacecraftConfiguration(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=100)
    scenario_id: str
    chassis_class: ChassisClass
    launch_vehicle_id: str
    orbit: OrbitConfiguration
    installed_component_ids: List[str] = Field(default_factory=list)


class FeasibilityValidationResponse(BaseModel):
    is_certified: bool
    status_summary: str
    resource_budgets: ResourceBudgets
    rule_violations: List[str] = Field(default_factory=list)
    compliance_warnings: List[str] = Field(default_factory=list)


class SimulationExecutionRequest(BaseModel):
    spacecraft_id: Optional[str] = None
    spacecraft_config: Optional[SpacecraftConfiguration] = None
    scenario_id: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.SPECIALIST
    simulation_seed: int = Field(default=4281920)


class TelemetryFrame(BaseModel):
    met_seconds: float
    orbit_number: int
    true_anomaly_deg: float
    is_in_eclipse: bool
    battery_soc_pct: float
    bus_temperature_c: float
    data_buffer_used_gb: float
    reaction_wheel_rpm: float
    current_downlink_rate_mbps: float
    cumulative_science_gb: float


class SimulationExecutionResponse(BaseModel):
    session_id: str
    scenario_id: str
    outcome: SimulationOutcome
    total_science_gb: float
    operational_days_survived: int
    final_eir_score: int
    honor_grade: str
    score_breakdown: Dict[str, float]
    anomalies_encountered: List[Dict[str, Any]]
    telemetry_time_series: List[TelemetryFrame]
    verification_hash: str
    agency_reward: Optional[Dict[str, Any]] = None


# ==============================================================================
# 3. WEBSOCKET REAL-TIME CONTRACTS
# ==============================================================================

class WSMessageType(str, Enum):
    CLAIM_ROLE = "CLAIM_ROLE"
    ROLE_ASSIGNED = "ROLE_ASSIGNED"
    COMPONENT_MUTATION = "COMPONENT_MUTATION"
    ORBIT_MUTATION = "ORBIT_MUTATION"
    STATE_DELTA = "STATE_DELTA"
    FRR_VOTE = "FRR_VOTE"
    FRR_STATUS = "FRR_STATUS"
    TELEMETRY_FRAME = "TELEMETRY_FRAME"
    ANOMALY_TRIGGERED = "ANOMALY_TRIGGERED"
    ANOMALY_RESOLVED = "ANOMALY_RESOLVED"
    CHAT_MESSAGE = "CHAT_MESSAGE"


class WSMessageEnvelope(BaseModel):
    type: WSMessageType
    room_id: str
    sender_callsign: str
    role: Optional[MissionRole] = None
    timestamp_utc: str
    payload: Dict[str, Any]
