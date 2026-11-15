# APPLICATION SECURITY REVIEW & THREAT MODEL: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Security Lead:** Senior Application Security Architect  
**Target Repository:** `/Users/subham/code/Lucy/security`  
**Security Standard:** OWASP Top 10:2021 + OWASP API Security Top 10 + Zero-Trust Client State Model

---

## 1. THREAT MODEL & ATTACK SURFACE OVERVIEW

In an interactive simulation game with competitive leaderboards and collaborative multiplayer, the primary threat actors are:
1. **Malicious / Scripting Players:** Attempting to manipulate resource values (e.g., unlimited propellant, zero mass, infinite battery) to cheat leaderboard rankings.
2. **Unauthorized Room Manipulators:** Attempting to hijack rooms, unseat players, or inject forged Flight Readiness Review (FRR) approval votes.
3. **Denial-of-Service / Resource Exhaustion Attackers:** Flooding the WebSocket gateway with rapid mutation frames or submitting extreme orbital integration parameters ($e \to 1.0$, $10^9$ time steps) to freeze backend CPU workers.

```
       ┌─────────────────────────────────────────────────────────────┐
       │                 UNTRUSTED CLIENT (BROWSER)                  │
       │   React State • DevTools Console • Tampered WebSocket WS    │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         [Untrusted Action Payloads]
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             SECURITY GATEWAY & VALIDATION LAYER             │
       │  1. Rate Limiting (Token Bucket per IP / Client Token)      │
       │  2. JWT Authentication & Room Membership RBAC Check         │
       │  3. Strict Pydantic v2 Schema Bounds & Regex Validation     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │               AUTHORITATIVE CALCULATION CORE                │
       │  - Server Recomputes All Margins (Ignores Client Math)      │
       │  - Single-Writer Role Mutex Enforcement                     │
       │  - Simulation Step Bounds (Max 5,000 steps per call)        │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                 SECURE PERSISTENCE LAYER                    │
       │  - SQLAlchemy Parameterized SQL (Zero Raw Concatenation)    │
       │  - Argon2 Password Hashes • Secret HMAC Scoring Signatures  │
       └─────────────────────────────────────────────────────────────┘
```

---

## 2. VULNERABILITY ANALYSIS & SECURITY CONTROLS

---

### VULNERABILITY 1: Client Resource Tampering & Cheat Injection
* **Threat:** A user opens Chrome DevTools and modifies local JavaScript memory or emits a WebSocket payload claiming:
  `{"wet_mass_kg": 1.0, "battery_soc_pct": 100.0, "total_science_gb": 999999.0}`.
* **Impact:** Trivial cheating, unearned leaderboard records, loss of educational integrity.
* **Mandatory Security Control:**
  1. **Zero-Trust Client State:** The server **never accepts physical values** from the client. The client can only send *intents* to mount/unmount a discrete component ID from the verified catalog:
     `{"action": "ADD_COMPONENT", "component_id": "INST-OPT-02"}`.
  2. **Authoritative Server Recomputation:** The backend retrieves component attributes from its local verified catalog (`components_catalog.json`) and calculates mass, power, thermal balance, and scoring independently.
  3. **HMAC Result Verification:** Leaderboard submission requires an authoritative server-generated HMAC-SHA256 signature:
     $$\text{VerificationHash} = \text{HMAC}_{\text{SHA256}}(\text{SessionID} \parallel \text{Score} \parallel \text{Seed}, \text{SecretKey})$$
     Clients cannot forge a leaderboard entry without the server's private secret key.

---

### VULNERABILITY 2: Broken Object-Level Authorization (BOLA / IDOR)
* **Threat:** A player changes the URL from `/api/v1/missions/84912` to `/api/v1/missions/84913` to view, overwrite, or delete another student's proprietary spacecraft blueprint.
* **Impact:** Data tampering, intellectual theft of winning mission configurations.
* **Mandatory Security Control:**
  1. Every database query verifying a mission design must enforce user ownership:
     ```python
     # Secure SQLAlchemy query enforcing ownership
     stmt = select(SpacecraftDesign).where(
         SpacecraftDesign.id == design_id,
         SpacecraftDesign.user_id == current_user.id  # Enforce tenant boundary
     )
     ```
  2. If the user does not own the design and is not an active collaborator in the assigned multiplayer room, return `404 Not Found` (to prevent ID enumeration) or `403 Forbidden`.

---

### VULNERABILITY 3: Broken Function-Level Authorization in Multiplayer (Role Spoofing)
* **Threat:** A player claiming the `SCIENCE_OFFICER` seat sends a WebSocket event attempting to select the launch vehicle or authorize the final Flight Readiness Review (FRR) vote reserved for the `MISSION_DIRECTOR`.
* **Impact:** Chaos in collaborative sessions; unauthorized launch clearances.
* **Mandatory Security Control:**
  1. **Strict Role-Based Access Control (RBAC) in WebSocket Router:**
     Every incoming WebSocket event is validated against the sender's claimed role:
     ```python
     ROLE_PERMISSIONS = {
         MissionRole.MISSION_DIRECTOR: {"LAUNCH_VEHICLE_SELECT", "FRR_VOTE_DIRECTOR", "BUDGET_ADJUDICATE"},
         MissionRole.SPACECRAFT_ENGINEER: {"BUS_COMPONENT_SELECT", "EPS_TUNE", "TCS_TUNE", "PROPULSION_SELECT"},
         MissionRole.SCIENCE_OFFICER: {"PAYLOAD_SELECT", "GSD_TARGET_TUNE", "DUTY_CYCLE_SCHEDULE"},
         MissionRole.FLIGHT_OPERATIONS: {"ORBIT_CONFIG_SELECT", "ANTENNA_SELECT", "TIMEWARP_CONTROL"}
     }

     if action_type not in ROLE_PERMISSIONS[client_role]:
         await websocket.send_json({"error": "403_FORBIDDEN", "detail": f"Action {action_type} unauthorized for {client_role}"})
         return
     ```

---

### VULNERABILITY 4: WebSocket Connection Hijacking & Room Flooding
* **Threat:** An attacker connects to `ws://api/ws/mission/ROOM-729` without authentication, floods the channel with malformed JSON, or impersonates an existing player's callsign.
* **Impact:** Service degradation, room crashes, malicious state desynchronization.
* **Mandatory Security Control:**
  1. **Token Authentication on WebSocket Handshake:**
     Require JWT token validation in the query parameter or initial handshake ticket:
     `ws://api/ws/mission/ROOM-729?token=<JWT_TOKEN>`.
  2. **Max Connection Clamping per Room:**
     Clamp maximum concurrent WebSocket connections to **6 per room** (4 active roles + 2 read-only spectators). Additional connection attempts receive `WS Close Code 1008 (Policy Violation)`.
  3. **WebSocket Ingestion Rate Limiting:**
     Enforce a per-client message throttle: maximum **10 messages per second**. Rapid bursts above 20 msgs/sec trigger immediate connection termination.

---

### VULNERABILITY 5: Denial-of-Service via Computational Astrodynamics (ReDoS / Float Bombs)
* **Threat:** An attacker calls `/api/v1/simulation/execute` with an extreme orbital eccentricity ($e = 0.999999$) or requests a 50-year orbital propagation with a $\Delta t = 0.001\text{ s}$ step size ($1.5\times 10^{12}$ loop iterations).
* **Impact:** CPU starvation; blocks the FastAPI asyncio event loop; crashes the server worker.
* **Mandatory Security Control:**
  1. **Strict Pydantic Input Boundaries:**
     ```python
     class OrbitConfiguration(BaseModel):
         altitude_km: float = Field(..., ge=150.0, le=1500000.0)
         inclination_deg: float = Field(..., ge=0.0, le=180.0)
         eccentricity: float = Field(0.0, ge=0.0, le=0.85)  # Clamped to prevent near-parabolic stalls
     ```
  2. **Simulation Timeout & Step Limits:**
     * Maximum operational simulation days clamped to **1,825 days (5 years)**.
     * Maximum integration time-steps capped at **10,000 steps** per API execution.
     * Hard execution timeout: Python `asyncio.wait_for(run_simulation(), timeout=5.0)` kills any execution taking longer than 5.0 seconds.

---

### VULNERABILITY 6: SQL Injection & ORM Leaks
* **Threat:** Malicious callsigns or search queries containing classic SQL injection payloads:
  `callsign: "admin' OR 1=1; --"`.
* **Impact:** Complete database compromise, leaking hashed passwords and session records.
* **Mandatory Security Control:**
  1. **100% Parameterized Queries via SQLAlchemy 2.0:**
     Zero raw string formatting (`f"SELECT * FROM users WHERE name = '{name}'"` is strictly forbidden by linter rules).
  2. **Strict Regex on User Identifiers:**
     Callsigns are restricted to alphanumeric characters, dashes, and underscores:
     `pattern=r"^[a-zA-Z0-9_-]{3,32}$"`.

---

### VULNERABILITY 7: Password Storage & Credential Leakage
* **Threat:** Leaked database dumps exposing user credentials.
* **Impact:** Credential stuffing across other platforms.
* **Mandatory Security Control:**
  1. Passwords hashed using **Argon2id** (the winner of the Password Hashing Competition) or **Bcrypt (cost factor 12)** via `passlib`.
  2. Zero plaintext passwords stored or logged.
  3. JWT tokens signed with **HMAC-SHA256** using an environment-injected secret key (`JWT_SECRET`, minimum 256 bits).

---

### VULNERABILITY 8: CORS Misconfiguration & Sensitive Data Exposure
* **Threat:** Permissive `allow_origins=["*"]` with `allow_credentials=True` exposing authentication cookies or API tokens to malicious third-party origins.
* **Impact:** Cross-Site WebSocket Hijacking (CSWSH) and session theft.
* **Mandatory Security Control:**
  1. Explicit CORS configuration in `backend/app/main.py`:
     ```python
     app.add_middleware(
         CORSMiddleware,
         allow_origins=["http://localhost:3000", "https://orbitalarchitect.space"],
         allow_credentials=True,
         allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Authorization", "Content-Type"],
     )
     ```
  2. Sensitive headers (`Authorization`, `Cookie`) stripped from structured application logs.

---

## 3. IMPLEMENTATION: FASTAPI SECURITY & AUTH MIDDLEWARE

The security controls are consolidated into:
[`backend/app/core/security.py`](file:///Users/subham/code/Lucy/backend/app/core/security.py)

```python
"""
Core Application Security & Token Validation Module for Orbital Architect
"""

import hmac
import hashlib
import time
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings

security_bearer = HTTPBearer()

def hash_mission_result(session_id: str, score: int, seed: int) -> str:
    """Generates an unforgeable HMAC-SHA256 signature for certified flight scores."""
    message = f"{session_id}:{score}:{seed}".encode("utf-8")
    return hmac.new(settings.JWT_SECRET.encode("utf-8"), message, hashlib.sha256).hexdigest()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> dict:
    """Validates incoming Bearer JWT token against server secret."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("exp") and payload["exp"] < time.time():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token")
```

---

## 4. PRACTICAL HACKATHON SECURITY CHECKLIST

To balance production-grade security with rapid hackathon deployment speed, apply this practical checklist:

| Category | Security Action Item | Status | Verified By |
| :--- | :--- | :---: | :--- |
| **Auth & Tokens** | Enforce JWT token verification on all mutation REST routes (`/save`, `/execute`). | [x] | Unit Tests |
| **Server Authority**| Never accept physical values (`mass_kg`, `power_w`, `score`) from client. | [x] | API Architecture |
| **Input Clamping**  | Clamp orbit altitude ($150\text{--}1.5\times 10^6\text{ km}$), eccentricity ($\le 0.85$), days ($\le 1,825$). | [x] | Pydantic Schemas |
| **Rate Limiting**   | Enforce 10 msgs/sec limit per WebSocket connection to stop flood scripts. | [x] | Connection Manager |
| **SQL Protection**  | Use SQLAlchemy 2.0 ORM expressions exclusively; zero string concatenation. | [x] | Database DDL |
| **Multiplayer RBAC**| Enforce single-writer role permissions (e.g., only Science PI mounts instruments).| [x] | WebSocket Router |
| **CORS Lockdown**   | Restrict CORS origins to localhost (dev) and verified deployment domain. | [x] | FastAPI Config |
| **Dependency Audit**| Run `pip-audit` and `npm audit` to verify zero critical CVEs in dependencies. | [x] | Build Pipeline |
| **Secrets Handling**| Ensure `JWT_SECRET` and database credentials are read from `.env` (never git-committed). | [x] | Pydantic Settings |
