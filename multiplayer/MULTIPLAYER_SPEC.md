# COOPERATIVE MULTIPLAYER ARCHITECTURE: NASA CONCURRENT DESIGN FACILITY (CDF)
**Document Version:** 1.0.0  
**Architect:** Multiplayer Game Architect & Real-Time Distributed Systems Engineer  
**Target Repository:** `/Users/subham/code/Lucy/multiplayer`  
**Core Motto:** *True Interdependence: No Single Role Can Launch Alone; Every Specialist Owns a Physical Boundary.*

---

## 1. THE COOPERATIVE PHILOSOPHY & ROLE SPECIALIZATION

In `Orbital Architect`, multiplayer is not a shared spectator screen. It is an authentic simulation of the **NASA Jet Propulsion Laboratory Project Design Center (PDC)** and the **ESA Concurrent Design Facility (CDF)**.
Each of the 4 players holds exclusive domain authority over a specific set of aerospace subsystems. A change made by one player immediately imposes physical and financial constraints on the other three.

```
       ┌─────────────────────────────────────────────────────────────┐
       │             MISSION DIRECTOR (Systems & Launch Lead)        │
       │   - Holds Master Budget Cap ($M) & Fairing Envelope         │
       │   - Selects Launch Vehicle Tier & Approves Launch Clearances│
       └──────────────┬──────────────────────────────┬───────────────┘
                      │ Demands Mass Margin          │ Allocates CapEx
                      ▼                              ▼
┌─────────────────────────────────────┐      ┌─────────────────────────────────────┐
│    SPACECRAFT ENGINEER (Bus Lead)   │      │   SCIENCE OFFICER (Principal Invest)│
│ - Sizes Bus Structure & Materials   │      │ - Selects Scientific Instruments    │
│ - Configures EPS (Arrays & Battery) │<────>│ - Sets Target Resolution & GSD      │
│ - Sizes TCS (Radiators & Heaters)   │Power │ - Manages Data Generation Rate      │
│ - Allocates Propulsion & ADCS       │Draw  └──────────────────┬──────────────────┘
└──────────────────┬──────────────────┘                         │ Data
                   │ Delta-V Required                           │ Volume
                   ▼                                            ▼
       ┌─────────────────────────────────────────────────────────────┐
       │         FLIGHT OPERATIONS OFFICER (Comms & Orbit Lead)      │
       │   - Configures Orbit Altitude, Inclination, & Ground Passes │
       │   - Sizes RF Antennas (S/X/Ka Band) & Downlink Transmitters │
       │   - Manages Real-time Ground Station Contacts & Anomalies   │
       └─────────────────────────────────────────────────────────────┘
```

---

## 2. THE 4 SPECIALIST ROLES & EXCLUSIVE CAPABILITIES

| Role | Exclusive Subsystem Authority | Decision Responsibilities | Primary Failure Modes Owned |
| :--- | :--- | :--- | :--- |
| **1. Mission Director** | Master Mission Budget, Launch Vehicle Selection, Flight Readiness Review (FRR) authorization. | Selects rocket class, approves financial expenditures, adjudicates trade-off disputes between science and engineering. | Launch mass exceedance, program financial bankruptcy. |
| **2. Spacecraft Engineer** | `STRUCTURE`, `ELECTRICAL_POWER`, `THERMAL_MANAGEMENT`, `PROPULSION`, `ATTITUDE_CONTROL`. | Sizes solar array area ($m^2$), battery capacity ($Wh$), radiator heat pipes, reaction wheels, and propellant tanks. | Eclipse battery brownout, component thermal runaway, wheel momentum saturation. |
| **3. Science Officer** | `SCIENTIFIC_INSTRUMENT` slots, observation duty cycle schedules, Target Resolution (GSD). | Selects optical telescopes, radars, spectrometers, and balances observation windows vs. data generation. | Missing minimum science yield threshold, blurry imagery due to excessive jitter. |
| **4. Flight Operations Officer** | `COMMUNICATION_ANTENNA`, Orbit altitude ($h$), inclination ($i$), ground station contracts, time-warp controls. | Configures RF transmitter power, downlink frequency bands, ground station contacts, and safe-mode recovery. | Telemetry buffer overflow, loss of ground station link ($E_b/N_0 < 3\text{ dB}$), atmospheric drag decay. |

---

## 3. SESSION LIFECYCLE & MULTIPLAYER FLOW

### 3.1 Room Creation & Player Joining
1. **Creation:** A player clicks `[HOST CO-OP ROOM]` $\to$ Server generates a human-readable 6-character room code (e.g., `ORBIT-729`).
2. **Joining:** Other players enter the room code on the landing page or join via direct URL: `https://orbitalarchitect.space/join/ORBIT-729`.
3. **Role Selection (Claiming Seats):**
   * The lobby presents a 4-seat mission operations console.
   * Players click `[CLAIM SEAT]` on an open role.
   * If fewer than 4 players are present, unfilled roles can be assigned to an active player as a secondary role, or managed by an AI/Assisted Copilot.

### 3.2 Shared Mission State Architecture
The authoritative room state is maintained in-memory on the FastAPI server and broadcast via WebSockets:

```json
{
  "room_id": "ORBIT-729",
  "scenario_id": "SCEN-01-EO-SENTINEL",
  "room_phase": "CONCURRENT_DESIGN", // 'CONCURRENT_DESIGN' | 'FRR_REVIEW' | 'FLIGHT_OPS' | 'DEBRIEF'
  "connected_clients": {
    "client_uuid_1": { "callsign": "FlightDirector_Dan", "role": "MISSION_DIRECTOR", "latency_ms": 24 },
    "client_uuid_2": { "callsign": "Dr_Vance", "role": "SCIENCE_OFFICER", "latency_ms": 18 },
    "client_uuid_3": { "callsign": "Chief_Eng_Sarah", "role": "SPACECRAFT_ENGINEER", "latency_ms": 31 },
    "client_uuid_4": { "callsign": "Comms_Lead_Alex", "role": "FLIGHT_OPERATIONS", "latency_ms": 22 }
  },
  "spacecraft_configuration": {
    "chassis_class": "SMALLSAT_LEO",
    "launch_vehicle_id": "LV-ELECTRON-01",
    "orbit": { "altitude_km": 550.0, "inclination_deg": 97.6, "eccentricity": 0.001 },
    "installed_components": [
      "INST-OPT-02", "EPS-SOL-02", "EPS-BAT-02", "ANT-X-02",
      "OBC-RAD-02", "PROP-HYD-02", "ADCS-RW-02", "TCS-PIPE-02", "STR-CFRP-02", "MEM-SSD-02"
    ]
  },
  "authoritative_margins": {
    "wet_mass_kg": 201.2,
    "launcher_capacity_kg": 250.0,
    "mass_margin_pct": 19.52,
    "power_net_balance_w": 42.5,
    "battery_dod_pct": 28.4,
    "link_margin_db": 15.4,
    "capex_remaining_usd": 10800000.0,
    "is_flight_certified": true
  },
  "frr_approval_votes": {
    "MISSION_DIRECTOR": false,
    "SPACECRAFT_ENGINEER": false,
    "SCIENCE_OFFICER": false,
    "FLIGHT_OPERATIONS": false
  }
}
```

---

## 4. CONCURRENT EDITING & CONFLICT RESOLUTION

### 4.1 Strict Domain Partitioning (The Single-Writer Principle)
To prevent race conditions without complex operational transforms (OT) or CRDT overhead:
* **Write Permissions:** A client can only emit action mutations for subsystems assigned to their claimed role.
  * *Example:* If the Science Officer attempts to change the battery component, the server rejects the WebSocket payload with `403 FORBIDDEN: Domain belongs to SPACECRAFT_ENGINEER`.
* **Instant Delta Broadcasting:**
  * When a player modifies an authorized subsystem, the server applies the change, recalculates all 6 coupled system margins, and broadcasts the updated state delta to all clients in $< 50\text{ ms}$.

### 4.2 Cross-Role Resource Requests (The Negotiation Mechanic)
When a role requires resources owned by another specialist, the UI provides formal **Resource Request Pings**:
1. *Scenario:* The Science Officer wants to install the high-power SAR Radar (`INST-SAR-03`, $1450\text{ W}$), which causes a power deficit alarm on the Spacecraft Engineer's console.
2. *Interaction:* The Science Officer clicks `[REQUEST POWER ALLOCATION: +500W]`.
3. *Feedback:* A high-priority amber notification flashes on the Spacecraft Engineer's HUD:
   `"SCIENCE REQUEST: Requires +500W for SAR observation pass. Options: [UPGRADE SOLAR ARRAY (+$2.5M)] or [REJECT REQUEST]"`.
4. *Resolution:* If the Spacecraft Engineer accepts, the array is upgraded; this increases structural mass, which immediately notifies the Mission Director of a reduced launch vehicle margin.

---

## 5. DECISION APPROVALS: THE FLIGHT READINESS REVIEW (FRR) CONSENSUS

Before the spacecraft can be launched, the team must pass the formal **Flight Readiness Review (FRR)**:
* Each specialist has a physical **"KEY TURN"** approval toggle:
  * Mission Director certifies **Budget & Launch Vehicle Margin**.
  * Spacecraft Engineer certifies **Mass Growth Allowance & Thermal Balance**.
  * Science Officer certifies **Primary Science Yield Viability**.
  * Flight Operations certifies **RF Link Budget & Ground Station Visibility**.
* **Launch Clearance Gate:**
  The server will only transition `room_phase` to `FLIGHT_OPS` when:
  $$\bigwedge_{r \in \text{Roles}} \text{Vote}(r) == \text{TRUE} \quad \land \quad \text{AuthoritativeMargins.is\_flight\_certified} == \text{TRUE}$$

---

## 6. AUTHORITATIVE SERVER-SIDE VALIDATION (ANTI-TAMPERING)

To ensure academic and competitive integrity, **the frontend client is treated as an untrusted presentation layer**:
1. **Never Trust Client Math:** The client sends only intent actions (e.g., `{"action": "ADD_COMPONENT", "id": "EPS-BAT-02"}`). The server runs the authoritative formulas in Python (`simulation_engine/margins.py` and `calculator.py`).
2. **State Verification Hashes:**
   Every simulation state update contains a cryptographic HMAC-SHA256 hash:
   $$\text{Hash} = \text{HMAC}(\text{RoomState}, \text{SecretKey})$$
   Any attempt to inject modified battery levels, fuel reserves, or budget numbers triggers immediate disconnection and room invalidation.

---

## 7. RESILIENCE: DISCONNECTIONS, RECONNECTIONS & FAULT TOLERANCE

| Event | System Reaction | User Feedback |
| :--- | :--- | :--- |
| **Player Drops Offline** | Server marks role as `DISCONNECTED` with a 90-second grace window. The simulation auto-pauses in `FLIGHT_OPS`. | Status bar displays: `⚠️ Science Officer (Dr_Vance) disconnected. 90s reconnect window...` |
| **Player Reconnects** | Client rejoins using room code and persistent JWT/Session cookie. Server responds with the complete authoritative snapshot. | Player's UI rehydrates instantly to current simulation state without losing progress. |
| **Grace Window Expires** | Role controls unlocked for delegation. Any connected player can click `[ASSUME ROLE]` to take over orphaned responsibilities. | Banner displays: `Science Officer seat is now open. Mission Director assigned temporary authority.` |
| **Host Drops Offline** | Room ownership transfers dynamically to the next lowest-latency connected player (Host Migration). | Zero gameplay interruption; room WebSocket connection remains open. |

---

## 8. REAL-TIME FASTAPI WEBSOCKET IMPLEMENTATION

### 8.1 Production Connection Manager (`backend/app/websocket/connection_manager.py`)
```python
import json
from typing import Dict, Set
from fastapi import WebSocket

class MultiplayerRoomManager:
    """Manages active multiplayer rooms, client connections, and role assignments."""

    def __init__(self):
        # Mapping: room_id -> set of active WebSockets
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        # Mapping: room_id -> dict of client metadata (roles, callsigns)
        self.room_states: Dict[str, dict] = {}

    async def connect(self, room_id: str, websocket: WebSocket, callsign: str):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = set()
            self.room_states[room_id] = {
                "room_id": room_id,
                "roles": {"MISSION_DIRECTOR": None, "SPACECRAFT_ENGINEER": None, "SCIENCE_OFFICER": None, "FLIGHT_OPERATIONS": None},
                "spacecraft": {"installed_components": []},
                "frr_votes": {}
            }
        self.active_rooms[room_id].add(websocket)
        # Broadcast user joined
        await self.broadcast(room_id, {
            "type": "USER_JOINED",
            "callsign": callsign,
            "roles": self.room_states[room_id]["roles"]
        })

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_rooms and websocket in self.active_rooms[room_id]:
            self.active_rooms[room_id].remove(websocket)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
                del self.room_states[room_id]

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_rooms:
            payload = json.dumps(message)
            for connection in self.active_rooms[room_id]:
                await connection.send_text(payload)

    def claim_role(self, room_id: str, role: str, callsign: str) -> bool:
        roles = self.room_states[room_id]["roles"]
        if roles.get(role) is None or roles.get(role) == callsign:
            roles[role] = callsign
            return True
        return False
```

### 8.2 WebSocket Action Router (`backend/app/api/v1/websocket_routes.py`)
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import MultiplayerRoomManager

router = APIRouter()
manager = MultiplayerRoomManager()

@router.websocket("/ws/mission/{room_id}")
async def mission_websocket_endpoint(websocket: WebSocket, room_id: str, callsign: str = "Cadet"):
    await manager.connect(room_id, websocket, callsign)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "CLAIM_ROLE":
                role = data.get("role")
                if manager.claim_role(room_id, role, callsign):
                    await manager.broadcast(room_id, {
                        "type": "ROLE_ASSIGNED",
                        "role": role,
                        "callsign": callsign
                    })

            elif msg_type == "COMPONENT_MUTATION":
                # 1. Verify that sender owns the subsystem category
                # 2. Authoritative server calculation of mass, power, and margins
                # 3. Broadcast updated authoritative state to all room players
                await manager.broadcast(room_id, {
                    "type": "STATE_DELTA",
                    "delta": data.get("payload")
                })

            elif msg_type == "FRR_VOTE":
                role = data.get("role")
                vote = data.get("vote", False)
                manager.room_states[room_id]["frr_votes"][role] = vote
                await manager.broadcast(room_id, {
                    "type": "FRR_VOTE_UPDATE",
                    "votes": manager.room_states[room_id]["frr_votes"]
                })

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(room_id, {
            "type": "USER_DISCONNECTED",
            "callsign": callsign
        })
```

---

## 9. HACKATHON FEASIBILITY VS. FUTURE SCALABILITY

| Dimension | Minimal Hackathon Implementation (Immediate) | Scalable Production Architecture (Future) |
| :--- | :--- | :--- |
| **State Storage** | Python in-memory dictionaries inside FastAPI process. | Distributed Redis Streams + PostgreSQL write-through cache. |
| **Message Broker** | Direct asyncio in-process WebSocket broadcasting. | Redis Pub/Sub cluster with horizontal FastAPI worker nodes. |
| **Conflict Resolution** | Role-based single-writer mutexes. | Operational Transformation (OT) or JSON-CRDT (Automerge/Yjs). |
| **Disconnection Handling** | 90-second in-memory grace timer before unclaiming seat. | Durable presence tracking via Redis heartbeats and session tokens. |
| **Voice & Comms** | In-app text chat and visual resource ping system. | WebRTC mesh audio channels for voice communications. |
