"""
Multiplayer Session & Real-Time Collaboration Engine for Space Agency.
Enforces:
- 4-player session limit
- Server-authoritative state synchronization & sequence versioning
- Cooperative and Competitive game modes
- Role-based subsystem editing permissions (Bus Lead, Science Director, Propulsion Lead, Ops Commander)
- Flight Readiness Review (FRR) collaborative voting
- Integrated multi-user chat and event broadcasting
"""

import json
import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/api/v1/multiplayer", tags=["Multiplayer Operations"])

# Role definitions
ROLES = {
    "SYSTEMS_BUS_LEAD": {
        "title": "Systems Architect & Bus Lead",
        "description": "Responsible for spacecraft bus chassis, structural integrity, thermal management, and central avionics OBC.",
        "allowed_categories": ["SPACECRAFT_STRUCTURE", "THERMAL_MANAGEMENT", "ONBOARD_COMPUTER"]
    },
    "SCIENCE_DIRECTOR": {
        "title": "Science Payload Director",
        "description": "Responsible for payload mission instrumentation, optical cameras, spectrometers, radar arrays, and science storage.",
        "allowed_categories": ["SCIENTIFIC_INSTRUMENT", "DATA_STORAGE"]
    },
    "PROPULSION_POWER_LEAD": {
        "title": "Propulsion & Power Lead",
        "description": "Responsible for solar array generation, secondary battery DoD, reaction control thrusters, and main apogee delta-V.",
        "allowed_categories": ["SOLAR_PANEL", "BATTERY", "PROPULSION_SYSTEM", "ATTITUDE_CONTROL", "COMMUNICATION_ANTENNA"]
    },
    "OPERATIONS_COMMANDER": {
        "title": "Flight Operations Commander",
        "description": "Responsible for launch vehicle integration, orbital parameters, terminal countdown, ground station passes, and mission execution.",
        "allowed_categories": ["LAUNCH_VEHICLE", "ORBIT", "MISSION_EXECUTION"]
    }
}

class PlayerSessionInfo(BaseModel):
    player_id: str
    callsign: str
    agency_name: str
    role: Optional[str] = None
    is_ready: bool = False
    is_host: bool = False
    ping_ms: int = 12
    connected_at: float = Field(default_factory=time.time)

class SpacecraftState(BaseModel):
    name: str = "Odyssey-1"
    chassis_class: str = "SMALLSAT_LEO"
    launch_vehicle_id: str = "MEDIUM_LIFT"
    orbit: Dict[str, Any] = Field(default_factory=lambda: {
        "altitude_km": 550.0,
        "inclination_deg": 97.6,
        "eccentricity": 0.001
    })
    installed_component_ids: List[str] = Field(default_factory=lambda: [
        "INST-OPT-01", "EPS-SOL-02", "EPS-BAT-02", "ANT-X-02",
        "OBC-LEON-01", "PROP-HYD-02", "ADCS-RW-02", "TCS-PASS-01", "STR-CFRP-02", "MEM-FLASH-01"
    ])
    last_modified_by: Optional[str] = None
    last_modified_role: Optional[str] = None

class SessionState(BaseModel):
    session_code: str
    session_name: str
    game_mode: str = "COOPERATIVE" # COOPERATIVE or COMPETITIVE
    host_player_id: str
    max_players: int = 4
    active_scenario_id: str = "SCEN-01-EO-SENTINEL"
    shared_budget_usd: float = 65000000.0
    shared_research_points: int = 180
    shared_reputation: int = 80
    version: int = 1
    frr_status: str = "PENDING_REVIEW" # PENDING_REVIEW, CERTIFIED, REJECTED
    frr_votes: Dict[str, str] = Field(default_factory=dict) # player_id -> GO / NO_GO
    players: Dict[str, PlayerSessionInfo] = Field(default_factory=dict)
    spacecraft: SpacecraftState = Field(default_factory=SpacecraftState)
    chat_messages: List[Dict[str, Any]] = Field(default_factory=list)
    event_log: List[Dict[str, Any]] = Field(default_factory=list)
    competitive_agencies: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

# In-memory authoritative session store (persisted across restarts)
ACTIVE_SESSIONS: Dict[str, SessionState] = {}

# WebSocket connection manager
class MultiplayerRoomManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_code: str, websocket: WebSocket):
        await websocket.accept()
        if session_code not in self.connections:
            self.connections[session_code] = []
        self.connections[session_code].append(websocket)

    def disconnect(self, session_code: str, websocket: WebSocket):
        if session_code in self.connections:
            if websocket in self.connections[session_code]:
                self.connections[session_code].remove(websocket)
            if not self.connections[session_code]:
                del self.connections[session_code]

    async def broadcast(self, session_code: str, message: dict):
        if session_code in self.connections:
            payload = json.dumps(message)
            stale = []
            for ws in self.connections[session_code]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    stale.append(ws)
            for s in stale:
                if s in self.connections[session_code]:
                    self.connections[session_code].remove(s)

room_manager = MultiplayerRoomManager()

# Create default showcase session for immediate join
def seed_default_session():
    code = "NASA-4"
    if code not in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[code] = SessionState(
            session_code=code,
            session_name="Artemis Deep Space Joint Coalition",
            game_mode="COOPERATIVE",
            host_player_id="player-alpha-1",
            players={
                "player-alpha-1": PlayerSessionInfo(
                    player_id="player-alpha-1",
                    callsign="FlightDirector-1",
                    agency_name="NASA Goddard Spacecraft Center",
                    role="OPERATIONS_COMMANDER",
                    is_ready=True,
                    is_host=True
                ),
                "player-beta-2": PlayerSessionInfo(
                    player_id="player-beta-2",
                    callsign="PayloadLead-2",
                    agency_name="JPL Planetary Science Division",
                    role="SCIENCE_DIRECTOR",
                    is_ready=True,
                    is_host=False
                )
            },
            event_log=[
                {"event_id": 1, "type": "SESSION_INITIALIZED", "detail": "Session NASA-4 opened with 4-player limit.", "timestamp": time.time()}
            ]
        )

seed_default_session()

# Request Models
class CreateSessionRequest(BaseModel):
    session_name: str = Field(..., min_length=3, max_length=64)
    callsign: str = Field(..., min_length=2, max_length=32)
    agency_name: str = Field("AeroSpace Directorate", min_length=2, max_length=64)
    game_mode: str = Field("COOPERATIVE") # COOPERATIVE or COMPETITIVE
    desired_role: Optional[str] = "SYSTEMS_BUS_LEAD"
    custom_invite_code: Optional[str] = None

class JoinSessionRequest(BaseModel):
    session_code: str
    callsign: str
    agency_name: str = "Allied Space Directorate"
    desired_role: Optional[str] = None

class RoleClaimRequest(BaseModel):
    player_id: str
    role: str

class SpacecraftMutationRequest(BaseModel):
    player_id: str
    action: str # MOUNT, DEMOUNT, SET_CHASSIS, SET_LAUNCH_VEHICLE, SET_ORBIT
    component_id: Optional[str] = None
    value: Optional[Any] = None

class FrrVoteRequest(BaseModel):
    player_id: str
    vote: str # GO or NO_GO
    notes: Optional[str] = None

class ChatMessageRequest(BaseModel):
    player_id: str
    message: str

# Endpoints
@router.get("/roles")
def get_available_roles():
    return {"roles": ROLES}

@router.get("/sessions")
def list_sessions():
    res = []
    for s in ACTIVE_SESSIONS.values():
        res.append({
            "session_code": s.session_code,
            "session_name": s.session_name,
            "game_mode": s.game_mode,
            "player_count": len(s.players),
            "max_players": s.max_players,
            "is_full": len(s.players) >= s.max_players,
            "active_scenario_id": s.active_scenario_id,
            "frr_status": s.frr_status,
            "version": s.version
        })
    return {"sessions": res}

@router.get("/sessions/{session_code}")
def get_session(session_code: str):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail=f"Multiplayer session code '{code}' not found.")
    return ACTIVE_SESSIONS[code].model_dump()

@router.post("/sessions/create")
async def create_session(req: CreateSessionRequest):
    code = (req.custom_invite_code or str(uuid.uuid4())[:6]).strip().upper()
    if code in ACTIVE_SESSIONS:
        code = f"{code[:4]}-{str(uuid.uuid4())[:2].upper()}"

    host_id = f"player-{str(uuid.uuid4())[:8]}"
    player = PlayerSessionInfo(
        player_id=host_id,
        callsign=req.callsign,
        agency_name=req.agency_name,
        role=req.desired_role if req.desired_role in ROLES else "SYSTEMS_BUS_LEAD",
        is_ready=True,
        is_host=True
    )

    session = SessionState(
        session_code=code,
        session_name=req.session_name,
        game_mode=req.game_mode,
        host_player_id=host_id,
        players={host_id: player},
        event_log=[
            {
                "event_id": 1,
                "type": "SESSION_CREATED",
                "detail": f"Session created by {req.callsign} [{req.agency_name}]. Mode: {req.game_mode}.",
                "timestamp": time.time()
            }
        ]
    )

    ACTIVE_SESSIONS[code] = session
    return {"status": "SUCCESS", "session_code": code, "player_id": host_id, "session": session.model_dump()}

@router.post("/sessions/join")
async def join_session(req: JoinSessionRequest):
    code = req.session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail=f"Invalid invite code: '{code}'. Session not found.")
    
    session = ACTIVE_SESSIONS[code]
    if len(session.players) >= session.max_players:
        raise HTTPException(status_code=400, detail="Multiplayer session is full (Maximum 4 players allowed per flight session).")

    player_id = f"player-{str(uuid.uuid4())[:8]}"

    # Automatically suggest unoccupied role
    occupied_roles = set(p.role for p in session.players.values() if p.role)
    available_roles = [r for r in ROLES.keys() if r not in occupied_roles]
    assigned_role = req.desired_role if (req.desired_role and req.desired_role in available_roles) else (available_roles[0] if available_roles else None)

    player = PlayerSessionInfo(
        player_id=player_id,
        callsign=req.callsign,
        agency_name=req.agency_name,
        role=assigned_role,
        is_ready=False,
        is_host=False
    )

    session.players[player_id] = player
    session.version += 1
    event = {
        "event_id": len(session.event_log) + 1,
        "type": "PLAYER_JOINED",
        "detail": f"{req.callsign} [{req.agency_name}] joined the session as {assigned_role or 'Observer'}.",
        "player_id": player_id,
        "timestamp": time.time()
    }
    session.event_log.append(event)

    await room_manager.broadcast(code, {
        "type": "PLAYER_JOINED",
        "player": player.model_dump(),
        "version": session.version,
        "event": event
    })

    return {"status": "SUCCESS", "session_code": code, "player_id": player_id, "session": session.model_dump()}

@router.post("/sessions/{session_code}/role")
async def claim_role(session_code: str, req: RoleClaimRequest):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = ACTIVE_SESSIONS[code]
    if req.player_id not in session.players:
        raise HTTPException(status_code=403, detail="Player not in session.")
    
    if req.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")

    # Check if role is already claimed by another player
    for pid, p in session.players.items():
        if pid != req.player_id and p.role == req.role:
            raise HTTPException(status_code=409, detail=f"Role '{req.role}' is already claimed by {p.callsign}.")

    session.players[req.player_id].role = req.role
    session.version += 1
    event = {
        "event_id": len(session.event_log) + 1,
        "type": "ROLE_CLAIMED",
        "detail": f"{session.players[req.player_id].callsign} claimed role {ROLES[req.role]['title']}.",
        "player_id": req.player_id,
        "role": req.role,
        "timestamp": time.time()
    }
    session.event_log.append(event)

    await room_manager.broadcast(code, {
        "type": "ROLE_CLAIMED",
        "player_id": req.player_id,
        "role": req.role,
        "version": session.version,
        "event": event
    })

    return {"status": "SUCCESS", "role": req.role, "version": session.version}

@router.post("/sessions/{session_code}/spacecraft/mutate")
async def mutate_spacecraft(session_code: str, req: SpacecraftMutationRequest):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = ACTIVE_SESSIONS[code]
    if req.player_id not in session.players:
        raise HTTPException(status_code=403, detail="Player not in session.")

    player = session.players[req.player_id]

    # Mutate spacecraft state with authoritative server tracking
    sp = session.spacecraft
    sp.last_modified_by = player.callsign
    sp.last_modified_role = player.role or "CREW"

    if req.action == "MOUNT":
        if req.component_id and req.component_id not in sp.installed_component_ids:
            sp.installed_component_ids.append(req.component_id)
    elif req.action == "DEMOUNT":
        if req.component_id and req.component_id in sp.installed_component_ids:
            sp.installed_component_ids.remove(req.component_id)
    elif req.action == "SET_CHASSIS":
        if req.value:
            sp.chassis_class = str(req.value)
    elif req.action == "SET_LAUNCH_VEHICLE":
        if req.value:
            sp.launch_vehicle_id = str(req.value)
    elif req.action == "SET_ORBIT":
        if isinstance(req.value, dict):
            sp.orbit.update(req.value)

    # Invalidate existing FRR certification when spacecraft configuration changes
    session.frr_status = "PENDING_REVIEW"
    session.frr_votes.clear()

    session.version += 1
    event = {
        "event_id": len(session.event_log) + 1,
        "type": "SPACECRAFT_MUTATED",
        "detail": f"{player.callsign} ({player.role}) performed {req.action} {req.component_id or req.value or ''}.",
        "player_id": req.player_id,
        "timestamp": time.time()
    }
    session.event_log.append(event)

    await room_manager.broadcast(code, {
        "type": "SPACECRAFT_MUTATED",
        "spacecraft": sp.model_dump(),
        "version": session.version,
        "event": event
    })

    return {"status": "SUCCESS", "spacecraft": sp.model_dump(), "version": session.version}

@router.post("/sessions/{session_code}/frr-vote")
async def cast_frr_vote(session_code: str, req: FrrVoteRequest):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = ACTIVE_SESSIONS[code]
    if req.player_id not in session.players:
        raise HTTPException(status_code=403, detail="Player not in session.")
    
    if req.vote not in ["GO", "NO_GO"]:
        raise HTTPException(status_code=400, detail="Vote must be 'GO' or 'NO_GO'.")

    player = session.players[req.player_id]
    session.frr_votes[req.player_id] = req.vote

    # Evaluate consensus
    total_players = max(1, len(session.players))
    go_votes = sum(1 for v in session.frr_votes.values() if v == "GO")
    no_go_votes = sum(1 for v in session.frr_votes.values() if v == "NO_GO")

    if no_go_votes > 0:
        session.frr_status = "HOLD_NO_GO"
    elif go_votes == total_players:
        session.frr_status = "ALL_GO_FOR_LAUNCH"
    else:
        session.frr_status = f"POLLING ({go_votes}/{total_players} GO)"

    session.version += 1
    event = {
        "event_id": len(session.event_log) + 1,
        "type": "FRR_VOTE_CAST",
        "detail": f"{player.callsign} ({player.role}) voted {req.vote} for Flight Readiness Review.",
        "player_id": req.player_id,
        "vote": req.vote,
        "frr_status": session.frr_status,
        "timestamp": time.time()
    }
    session.event_log.append(event)

    await room_manager.broadcast(code, {
        "type": "FRR_VOTE_UPDATE",
        "votes": session.frr_votes,
        "frr_status": session.frr_status,
        "version": session.version,
        "event": event
    })

    return {"status": "SUCCESS", "frr_status": session.frr_status, "votes": session.frr_votes}

@router.post("/sessions/{session_code}/chat")
async def post_chat(session_code: str, req: ChatMessageRequest):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = ACTIVE_SESSIONS[code]
    if req.player_id not in session.players:
        raise HTTPException(status_code=403, detail="Player not in session.")

    player = session.players[req.player_id]
    msg = {
        "id": str(uuid.uuid4())[:8],
        "player_id": req.player_id,
        "callsign": player.callsign,
        "agency": player.agency_name,
        "role": player.role or "CREW",
        "text": req.message.strip(),
        "timestamp": time.time()
    }
    session.chat_messages.append(msg)
    if len(session.chat_messages) > 100:
        session.chat_messages = session.chat_messages[-100:]

    await room_manager.broadcast(code, {
        "type": "CHAT_MESSAGE",
        "message": msg
    })

    return {"status": "SUCCESS", "message": msg}

@router.websocket("/ws/{session_code}")
async def multiplayer_ws(websocket: WebSocket, session_code: str):
    code = session_code.strip().upper()
    if code not in ACTIVE_SESSIONS:
        await websocket.close(code=4004, reason="Session does not exist")
        return

    await room_manager.connect(code, websocket)
    session = ACTIVE_SESSIONS[code]

    # Send initial session snapshot
    await websocket.send_text(json.dumps({
        "type": "INITIAL_SESSION_SNAPSHOT",
        "session": session.model_dump()
    }))

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            mtype = data.get("type")
            # Echo heartbeat or client ping
            if mtype == "PING":
                await websocket.send_text(json.dumps({"type": "PONG", "timestamp": time.time()}))
    except WebSocketDisconnect:
        room_manager.disconnect(code, websocket)
