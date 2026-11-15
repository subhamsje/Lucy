# PRODUCTION SOFTWARE ARCHITECTURE & SYSTEMS SPECIFICATION: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Architect:** Principal Software Architect & CTO  
**Target Repository:** `/Users/subham/code/Lucy`  
**Core Standard:** *Modular Monolith + Client-Side Deterministic Hybrid + Real-Time WebSocket State Sync*

---

## 1. SYSTEM ARCHITECTURE & HIGH-LEVEL TOPOLOGY

To optimize for **hackathon velocity**, **sub-millisecond UI reactivity**, and **production reliability**, the system avoids microservice bloat and adopts a high-throughput **Modular Monolith Architecture** with a **Hybrid Simulation Strategy**:
1. **Interactive Real-Time Design Loops (Client-Side):**
   * Immediate parametric margin calculations (AIAA mass growth allowance, power balance, link budget, and geometric fairing envelope) run in TypeScript directly in the browser. Zero HTTP round-trip latency when dragging sliders.
2. **Authoritative Verification & Multi-Orbit Numerical Integration (Backend):**
   * Python FastAPI + NumPy/SciPy handles authoritative Flight Readiness Reviews (FRR), numerical orbital integrations, stochastic anomaly simulations, and post-flight mission scoring.
3. **Multiplayer Room Gateway (WebSockets):**
   * Star-topology real-time state synchronization via FastAPI WebSockets. Redis is utilized strictly as an in-memory Pub/Sub message broker when horizontal multi-instance scaling is required, with a clean local in-memory fallback for local development.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CLIENT TIER (BROWSER)                                      │
│  React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui + Three.js / React Three Fiber         │
│                                                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌────────────────────────────────────┐  │
│  │   UI Presentation    │    │  Client Math Engine  │    │      Zustand Reactive Stores       │  │
│  │ 20 Mission Screens   │<──>│  Instant Margin Loop │<──>│ - MissionStore  - SubsystemStore   │  │
│  │ 3D Procedural R3F    │    │  Keplerian Line2 Gen │    │ - TelemetryStore- MultiplayerStore │  │
│  └──────────────────────┘    └──────────────────────┘    └─────────────────┬──────────────────┘  │
└───────────────────────────────────────────────▲────────────────────────────┼─────────────────────┘
                                                │ HTTPS REST                 │ WSS (WebSockets)
                                                ▼                            ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      BACKEND APPLICATION TIER                                    │
│                              FastAPI (Modular Monolith) + Python 3.11+                           │
│                                                                                                  │
│  ┌──────────────────────────────────────────────┐    ┌────────────────────────────────────────┐  │
│  │               REST API ROUTERS               │    │         REAL-TIME WEBSOCKET HUB        │  │
│  │ - /api/v1/auth        - /api/v1/components   │    │ - /ws/mission/{room_id}                │  │
│  │ - /api/v1/scenarios   - /api/v1/simulation   │    │ - RoomManager & Role Claims            │  │
│  │ - /api/v1/missions    - /api/v1/leaderboard  │    │ - Operational Event Dispatcher         │  │
│  └──────────────────────┬───────────────────────┘    └───────────────────┬────────────────────┘  │
│                         │                                                │                       │
│  ┌──────────────────────▼────────────────────────────────────────────────▼────────────────────┐  │
│  │                            CORE SCIENTIFIC SIMULATION ENGINE                               │  │
│  │  - NumPy Orbit Integrator (J2 Precession, Eclipse Geometry, Drag Decay)                    │  │
│  │  - Subsystem Coupling Matrix (AIAA S-120 Mass Compounding, Thermal Radiative Balance)      │  │
│  │  - Stochastic Space Weather Generator & Anomaly Resolution Engine                         │  │
│  └──────────────────────────────────────────────┬─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┼────────────────────────────────────────────────┘
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       PERSISTENCE & DATA TIER                                    │
│                                                                                                  │
│  ┌──────────────────────────────────────────────┐    ┌────────────────────────────────────────┐  │
│  │         PostgreSQL 15+ (Relational DB)       │    │           Redis (Optional Pub/Sub)     │  │
│  │ - User Accounts & Career Dossiers            │    │ - In-memory multi-room state broadcast │  │
│  │ - Certified Spacecraft Blueprint JSONB       │    │ - Real-time ephemeral telemetry cache  │  │
│  │ - Flight Verification Logs & Scoring Audits  │    │   (Defaults to In-Memory for dev)      │  │
│  └──────────────────────────────────────────────┘    └────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PROJECT REPOSITORY STRUCTURE

```
/Users/subham/code/Lucy/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entrypoint, middleware, CORS, lifespan
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic BaseSettings (env vars, secrets)
│   │   │   ├── database.py             # SQLAlchemy 2.0 Async Session Engine
│   │   │   ├── security.py             # Password hashing (argon2) & JWT tokens
│   │   │   └── logging.py              # Structured JSON logging (structlog)
│   │   ├── models/                     # SQLAlchemy ORM Data Models
│   │   │   ├── user.py
│   │   │   ├── component.py
│   │   │   ├── mission.py
│   │   │   └── simulation_result.py
│   │   ├── schemas/                    # Pydantic v2 Request/Response DTO Schemas
│   │   │   ├── auth.py
│   │   │   ├── spacecraft.py
│   │   │   ├── telemetry.py
│   │   │   └── simulation.py
│   │   ├── api/                        # REST API Route Controllers
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── components.py
│   │   │   │   ├── scenarios.py
│   │   │   │   ├── missions.py
│   │   │   │   ├── simulation.py
│   │   │   │   └── leaderboard.py
│   │   ├── simulation_engine/          # High-Performance Scientific Computations
│   │   │   ├── astrodynamics.py        # Keplerian & numerical orbit propagator
│   │   │   ├── margins.py              # AIAA S-120 Mass & Energy balance solver
│   │   │   ├── communications.py       # FSPL & Eb/N0 link margin calculator
│   │   │   └── anomalies.py            # Space weather & stochastic fault engine
│   │   └── websocket/                  # Real-Time Collaborative Hub
│   │       ├── connection_manager.py   # Multi-room client registry & broadcasting
│   │       └── protocol.py             # Typed WebSocket message schemas
│   ├── tests/
│   │   ├── test_astrodynamics.py
│   │   ├── test_margins.py
│   │   └── test_api_endpoints.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                    # React DOM entrypoint
│   │   ├── App.tsx                     # Top-level routing & layout wrapper
│   │   ├── index.css                   # Tailwind CSS v4 directives & font imports
│   │   ├── components/
│   │   │   ├── ui/                     # shadcn/ui primitives (Button, Slider, Modal, etc.)
│   │   │   ├── common/                 # TelemetryStatusBar, AudioAlerts, LoadingScreen
│   │   │   ├── studio/                 # SubsystemDrawers, ComponentCard, MarginGauges
│   │   │   ├── console/                # TelemetryStripChart, OrbitMap2D, MissionClock
│   │   │   └── 3d/                     # Three.js / React Three Fiber Viewports
│   │   │       ├── SpacecraftCanvas.tsx
│   │   │       ├── CelestialEarth.tsx
│   │   │       ├── OrbitRibbon.tsx
│   │   │       └── AtmosphereShader.tsx
│   │   ├── stores/                     # Zustand State Containers
│   │   │   ├── useMissionStore.ts      # Active scenario, spacecraft assembly state
│   │   │   ├── useTelemetryStore.ts    # Real-time streaming metrics & buffer %
│   │   │   ├── useMultiplayerStore.ts  # Room connection, player roles, team chat
│   │   │   └── useUIStore.ts           # Active view mode, drawer state, sound toggles
│   │   ├── hooks/
│   │   │   ├── useWebSocketSync.ts     # Resilient WS client with auto-reconnect
│   │   │   └── useOrbitCalculator.ts   # Client-side instant Keplerian math
│   │   ├── lib/
│   │   │   ├── api.ts                  # Axios / Fetch client with JWT interceptor
│   │   │   ├── audio.ts                # Synthesized Web Audio API sound generator
│   │   │   └── utils.ts                # Class merging & formatters
│   │   └── types/                      # TypeScript Interface Definitions
│   │       ├── component.ts
│   │       ├── scenario.ts
│   │       └── telemetry.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── data/                               # Shared Catalog Datasets & SQL DDL
│   ├── components_catalog.json
│   ├── compatibility_rules.json
│   └── schema.sql
└── docker-compose.yml                  # One-command full-stack orchestration
```

---

## 3. SEPARATION OF CONCERNS & BOUNDARY CONTRACTS

To maintain architectural integrity, components communicate strictly across defined boundaries:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STRICT ARCHITECTURAL BOUNDARIES                        │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Layer           │ Responsibilities & Explicit Constraints                   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 1. UI Layer     │ Reads Zustand stores and renders React DOM & R3F canvas.  │
│                 │ MUST NOT contain hardcoded aerospace formulas.            │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 2. Client Math  │ Fast algebraic calculations (e.g., mass sum, focal length │
│    Engine       │ GSD, nominal period) for instantaneous slider feedback.   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 3. Backend Sim  │ Authoritative flight physics (numerical orbit propagation,│
│    Engine       │ stochastic radiation events, official scoring).           │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 4. Multiplayer  │ Synchronizes JSON action deltas across room participants. │
│    State        │ Enforces single-writer locks on subsystem roles.          │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 5. Persistence  │ Manages PostgreSQL transactions, user dossiers, and       │
│    Layer        │ tamper-proof mission verification hashes.                 │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 4. DATABASE SCHEMA & RELATIONAL MODEL (POSTGRESQL)

```sql
-- Core PostgreSQL Relational Schema for Orbital Architect

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    callsign VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rank_tier VARCHAR(32) DEFAULT 'CADET' CHECK (rank_tier IN ('CADET', 'SPECIALIST', 'FLIGHT_DIRECTOR', 'MASTER_ARCHITECT')),
    engineering_integrity_rating INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mission Scenarios Table
CREATE TABLE scenarios (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    difficulty VARCHAR(32) NOT NULL,
    budget_cap_usd NUMERIC(14, 2) NOT NULL,
    primary_data_threshold_gb NUMERIC(10, 2) NOT NULL,
    scenario_metadata JSONB NOT NULL
);

-- 3. Spacecraft Designs (Blueprints)
CREATE TABLE spacecraft_designs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scenario_id VARCHAR(64) NOT NULL REFERENCES scenarios(id),
    name VARCHAR(100) NOT NULL,
    chassis_class VARCHAR(64) NOT NULL,
    target_orbit_altitude_km NUMERIC(8, 2) NOT NULL,
    target_orbit_inclination_deg NUMERIC(6, 3) NOT NULL,
    launch_vehicle_id VARCHAR(64) NOT NULL,
    subsystems_configuration JSONB NOT NULL,
    computed_dry_mass_kg NUMERIC(8, 3) NOT NULL,
    computed_wet_mass_kg NUMERIC(8, 3) NOT NULL,
    total_cost_usd NUMERIC(14, 2) NOT NULL,
    is_certified_for_flight BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Simulation Execution Records
CREATE TABLE simulation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spacecraft_id UUID NOT NULL REFERENCES spacecraft_designs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    scenario_id VARCHAR(64) NOT NULL REFERENCES scenarios(id),
    outcome_status VARCHAR(32) NOT NULL CHECK (outcome_status IN ('SUCCESS', 'PARTIAL_SUCCESS', 'CATASTROPHIC_FAILURE')),
    total_science_downlinked_gb NUMERIC(10, 2) NOT NULL,
    operational_days_survived INTEGER NOT NULL,
    final_eir_score INTEGER NOT NULL,
    failure_root_cause TEXT,
    flight_telemetry_summary JSONB NOT NULL,
    verification_hash VARCHAR(64) NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Multiplayer Collaborative Rooms
CREATE TABLE multiplayer_rooms (
    id VARCHAR(16) PRIMARY KEY, -- e.g., 'ROOM-7821'
    created_by_user_id UUID REFERENCES users(id),
    scenario_id VARCHAR(64) NOT NULL REFERENCES scenarios(id),
    is_active BOOLEAN DEFAULT TRUE,
    role_assignments JSONB DEFAULT '{"SYSTEMS": null, "SCIENCE": null, "POWER": null, "OPS": null}'::jsonb,
    shared_spacecraft_id UUID REFERENCES spacecraft_designs(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Fast Lookups & Leaderboard Queries
CREATE INDEX idx_simulation_results_scenario_score ON simulation_results(scenario_id, final_eir_score DESC);
CREATE INDEX idx_spacecraft_user ON spacecraft_designs(user_id);
```

---

## 5. API ARCHITECTURE & ENDPOINT SPECIFICATIONS

All REST endpoints follow standard JSON REST conventions under `/api/v1`.

### 5.1 Endpoint Inventory
| HTTP Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user with callsign & password | No |
| `POST` | `/api/v1/auth/login` | Authenticate and return JWT access token | No |
| `GET` | `/api/v1/components` | Retrieve complete 31-component catalog | No |
| `GET` | `/api/v1/scenarios` | Retrieve the 6 mission scenario definitions | No |
| `POST` | `/api/v1/spacecraft/validate` | Verify design against AIAA margins & rules | Optional |
| `POST` | `/api/v1/spacecraft/save` | Persist spacecraft blueprint | Bearer JWT |
| `POST` | `/api/v1/simulation/execute` | Run authoritative multi-orbit simulation | Bearer JWT |
| `GET` | `/api/v1/leaderboard/{scenario_id}` | Fetch top 50 ranked flight records | No |
| `WS` | `/ws/mission/{room_id}` | Real-time 4-player collaboration socket | Token Param |

### 5.2 Example Request & Response: `/api/v1/spacecraft/validate`
**Request Payload:**
```json
{
  "scenario_id": "SCEN-01-EO-SENTINEL",
  "chassis_class": "SMALLSAT_LEO",
  "launch_vehicle_id": "LV-ELECTRON-01",
  "target_orbit": {
    "altitude_km": 550.0,
    "inclination_deg": 97.6,
    "eccentricity": 0.001
  },
  "installed_components": [
    "INST-OPT-02",
    "EPS-SOL-02",
    "EPS-BAT-02",
    "ANT-X-02",
    "OBC-RAD-02",
    "PROP-HYD-02",
    "ADCS-RW-02",
    "TCS-PIPE-02",
    "STR-CFRP-02",
    "MEM-SSD-02"
  ]
}
```

**Response Payload:**
```json
{
  "is_certified": true,
  "mass_summary": {
    "dry_mass_kg": 138.5,
    "mass_growth_allowance_kg": 27.7,
    "propellant_mass_kg": 35.0,
    "wet_mass_kg": 201.2,
    "launcher_capacity_kg": 250.0,
    "mass_margin_pct": 19.52,
    "status": "NOMINAL"
  },
  "power_summary": {
    "day_generation_w": 380.0,
    "night_load_w": 65.0,
    "eclipse_duration_min": 35.2,
    "battery_depth_of_discharge_pct": 28.4,
    "status": "NOMINAL"
  },
  "link_summary": {
    "frequency_band": "X-Band",
    "downlink_rate_mbps": 120.0,
    "calculated_eb_n0_db": 18.4,
    "margin_db": 15.4,
    "status": "NOMINAL"
  },
  "budget_summary": {
    "total_capex_usd": 24200000.0,
    "budget_cap_usd": 35000000.0,
    "remaining_margin_usd": 10800000.0
  },
  "compatibility_checks": [
    { "rule": "Pointing Accuracy Check", "passed": true, "message": "ADCS-RW-02 provides 0.08 deg, satisfying INST-OPT-02 fine tracking." },
    { "rule": "Fairing Volume Enclosure", "passed": true, "message": "Stowed height 1.1m fits Electron 1.2m static envelope." }
  ]
}
```

---

## 6. MULTIPLAYER WEBSOCKET ARCHITECTURE & PROTOCOL

The multiplayer room gateway operates over a bidirectional WebSocket channel (`/ws/mission/{room_id}`).

### 6.1 State Ownership & Single-Writer Principle
To eliminate race conditions when 4 players edit the same spacecraft simultaneously:
* **Systems Director:** Exclusive write lock over `launch_vehicle_id`, `chassis_class`, and final budget commitment.
* **Science PI:** Exclusive write lock over `SCIENTIFIC_INSTRUMENT` slots and target ground resolution.
* **Power & Thermal Lead:** Exclusive write lock over `SOLAR_PANEL`, `BATTERY`, and `THERMAL_MANAGEMENT`.
* **Flight Operations Lead:** Exclusive write lock over `COMMUNICATION_ANTENNA`, ground network passes, and time-warp playback.

### 6.2 WebSocket Message Protocol (JSON Schemas)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WEBSOCKET MESSAGE ENVELOPE                            │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Field           │ Type & Description                                        │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ type            │ String: 'CLAIM_ROLE', 'COMPONENT_MOUNT', 'MARGIN_ALERT',  │
│                 │         'FRR_VOTE', 'TELEMETRY_SYNC', 'CHAT_MESSAGE'      │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ room_id         │ String: e.g. 'ROOM-7821'                                  │
│ sender_callsign │ String: e.g. 'FlightDirector_Alpha'                       │
│ role            │ String: 'SYSTEMS', 'SCIENCE', 'POWER', 'OPS'              │
│ timestamp_utc   │ ISO-8601 String                                           │
│ payload         │ Object containing message-specific data                   │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

**Example Event: Science PI mounts a radar instrument:**
```json
{
  "type": "COMPONENT_MOUNT",
  "room_id": "ROOM-7821",
  "sender_callsign": "Dr_Vance",
  "role": "SCIENCE",
  "payload": {
    "action": "ADD",
    "component_id": "INST-SAR-03",
    "subsystem": "SCIENTIFIC_INSTRUMENT"
  }
}
```
*When received, the backend validates role authorization, computes the updated system margins, and broadcasts the updated state to all 4 clients within 50 milliseconds.*

---

## 7. AUTHENTICATION & SESSION MANAGEMENT

* **Stateless JWT Tokens:** Standard RFC 7519 tokens containing `user_id`, `callsign`, and `rank_tier`.
* **Token Lifetime:** 24-hour access tokens, minimizing session expiration disruptions during multi-hour hackathon judging demos.
* **Guest / Cadet Mode:** Players can launch instant single-player missions without registration; designs are persisted to HTML5 `localStorage` and synchronized with an account upon sign-up.

---

## 8. OBSERVABILITY, LOGGING & ERROR HANDLING

* **Structured Logging:** Utilizes `structlog` in Python, outputting machine-readable JSON logs:
  ```json
  {"timestamp": "2026-11-14T22:30:15Z", "level": "INFO", "event": "SIMULATION_COMPLETED", "user": "Apollo9", "score": 885, "duration_ms": 142}
  ```
* **Global Error Middleware:** All exceptions return standardized RFC 7807 `ProblemDetails` responses:
  ```json
  {
    "type": "https://orbitalarchitect.space/errors/margin-violation",
    "title": "AIAA Mass Margin Violation",
    "status": 422,
    "detail": "Spacecraft wet mass (265.4 kg) exceeds launch vehicle capacity (250.0 kg) by 15.4 kg."
  }
  ```

---

## 9. DEPLOYMENT & ZERO-CONFIG LOCAL EXECUTION

### One-Command Full-Stack Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: orbital_architect
      POSTGRES_USER: lucy_admin
      POSTGRES_PASSWORD: aerospace_secret_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data/schema.sql:/docker-entrypoint-initdb.d/init.sql

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://lucy_admin:aerospace_secret_password@db:5432/orbital_architect
      JWT_SECRET: orbital_architect_super_secure_jwt_secret_key_2026
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```
*Developers and hackathon judges can start the entire stack with a single command:* `docker compose up -d`.
