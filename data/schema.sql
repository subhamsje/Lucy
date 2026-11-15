-- ==============================================================================
-- DATABASE SCHEMA: ORBITAL ARCHITECT (Project Lucy)
-- Standard: PostgreSQL 15+ / SQLite3 compatible
-- Description: Relational catalog for modular spacecraft components & configurations
-- ==============================================================================

-- 1. Component Categories Enum Table
CREATE TABLE IF NOT EXISTS component_categories (
    category_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    subsystem_code VARCHAR(10) NOT NULL,
    description TEXT
);

INSERT INTO component_categories (category_id, display_name, subsystem_code, description) VALUES
('SCIENTIFIC_INSTRUMENT', 'Scientific Payload Instruments', 'PAY', 'Sensors, imagers, radars, spectrometers'),
('SOLAR_PANEL', 'Solar Photovoltaic Arrays', 'EPS', 'Silicon, GaAs, body-mounted, tracking wings'),
('BATTERY', 'Energy Storage Modules', 'EPS', 'Li-ion, LiFePO4, solid-state batteries'),
('COMMUNICATION_ANTENNA', 'RF Antennas & Transmitters', 'TTC', 'S-band, X-band, Ka-band reflectors & horns'),
('ONBOARD_COMPUTER', 'Command & Data Handling OBC', 'CDH', 'LEON3, RAD750, Edge AI microprocessors'),
('PROPULSION_SYSTEM', 'Spacecraft Propulsion', 'PROP', 'Cold gas, hydrazine, xenon Hall thrusters'),
('ATTITUDE_CONTROL', 'ADCS Stabilization & Actuators', 'ADCS', 'Magnetorquers, reaction wheels, star trackers'),
('THERMAL_MANAGEMENT', 'Thermal Control Systems', 'TCS', 'MLI blankets, heat pipes, cryocoolers'),
('SPACECRAFT_STRUCTURE', 'Primary Structure Chassis', 'STR', 'CubeSat dispensers, CFRP, isogrid buses'),
('DATA_STORAGE', 'Mass Memory Recorders', 'MEM', 'Flash SSR, NVMe, radiation-hard MRAM')
ON CONFLICT (category_id) DO NOTHING;

-- 2. Component Master Table
CREATE TABLE IF NOT EXISTS components (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL REFERENCES component_categories(category_id),
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('BASIC', 'INTERMEDIATE', 'ADVANCED')),
    description TEXT NOT NULL,
    mass_kg NUMERIC(8, 3) NOT NULL CHECK (mass_kg > 0),
    power_consumption_w NUMERIC(8, 2) NOT NULL DEFAULT 0.0 CHECK (power_consumption_w >= 0),
    power_generation_w NUMERIC(8, 2) NOT NULL DEFAULT 0.0 CHECK (power_generation_w >= 0),
    cost_usd NUMERIC(12, 2) NOT NULL CHECK (cost_usd >= 1000),
    data_generation_mb_per_day NUMERIC(12, 2) NOT NULL DEFAULT 0.0,
    storage_capacity_gb NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    
    -- Reliability Metrics
    mtbf_hours INTEGER NOT NULL,
    trl INTEGER NOT NULL CHECK (trl BETWEEN 1 AND 9),
    failure_probability_annual NUMERIC(5, 4) NOT NULL,
    radiation_tolerance_krad NUMERIC(6, 1) NOT NULL,
    
    -- Subsystem-Specific Metrics (JSONB allows flexible expansion without engine changes)
    performance_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Compatibility & Interfaces
    required_bus_voltage_v INTEGER NOT NULL CHECK (required_bus_voltage_v IN (5, 12, 28, 50, 100)),
    required_pointing_accuracy_deg NUMERIC(6, 4) DEFAULT 0.0,
    requires_deployable_boom BOOLEAN DEFAULT FALSE,
    requires_cryocooler BOOLEAN DEFAULT FALSE,
    requires_stationkeeping_thrusters BOOLEAN DEFAULT FALSE,
    
    -- Heritage & References
    heritage_reference VARCHAR(200) NOT NULL,
    benchmark_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Chassis Compatibility Junction Table
CREATE TABLE IF NOT EXISTS component_chassis_support (
    component_id VARCHAR(50) REFERENCES components(id) ON DELETE CASCADE,
    chassis_class VARCHAR(50) NOT NULL CHECK (chassis_class IN ('CUBESAT_12U', 'SMALLSAT_LEO', 'MEDIUM_BUS', 'HEAVY_PROBE')),
    PRIMARY KEY (component_id, chassis_class)
);

-- 4. Component Dependencies & Prerequisites
CREATE TABLE IF NOT EXISTS component_prerequisites (
    component_id VARCHAR(50) REFERENCES components(id) ON DELETE CASCADE,
    required_component_id VARCHAR(50) REFERENCES components(id) ON DELETE CASCADE,
    PRIMARY KEY (component_id, required_component_id)
);

-- 5. Component Exclusions (Mutual Conflicts)
CREATE TABLE IF NOT EXISTS component_exclusions (
    component_a VARCHAR(50) REFERENCES components(id) ON DELETE CASCADE,
    component_b VARCHAR(50) REFERENCES components(id) ON DELETE CASCADE,
    conflict_reason TEXT NOT NULL,
    PRIMARY KEY (component_a, component_b)
);

-- 6. Indexes for High-Speed Querying & Dynamic Assembly
CREATE INDEX IF NOT EXISTS idx_components_category ON components(category);
CREATE INDEX IF NOT EXISTS idx_components_tier ON components(tier);
CREATE INDEX IF NOT EXISTS idx_components_cost ON components(cost_usd);
CREATE INDEX IF NOT EXISTS idx_components_mass ON components(mass_kg);
