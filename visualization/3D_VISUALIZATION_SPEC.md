# 3D SCIENTIFIC VISUALIZATION ARCHITECTURE: ORBITAL ARCHITECT (LUCY)
**Document Version:** 1.0.0  
**Domain:** Scientific Data Visualization, Three.js, React Three Fiber (R3F), WebGL Shaders  
**Target Repository:** `/Users/subham/code/Lucy/visualization`  
**Core Standard:** *Scientifically Grounded Dynamics + Deterministic State Synchronization + 60 FPS Mobile/Desktop Performance*

---

## 1. VISUALIZATION PHILOSOPHY & BOUNDARY DEFINITION

In `Orbital Architect`, the 3D scene is **never a disconnected artistic cutscene**. It is a **real-time visual readout of the discrete-event simulation state**:
1. When the player adjusts inclination $i$, the nodal line precesses and the 3D Keplerian ellipse tilts dynamically.
2. When the spacecraft passes into Earth's umbra shadow cone, the directional solar vector cuts off, solar array glow turns off, and Earth's night lights illuminate beneath the ground-track.
3. When the player mounts an articulated GaAs solar wing or Ka-band dish, the procedural GLTF assembly hierarchy mounts, pivots, and tracks the sun/Earth vectors in real time.

### Distinction: Scientifically Meaningful vs. Decorative Elements
| Visual Feature | Scientifically Meaningful (Simulation-Driven) | Decorative / Stylistic Layer (Restrained) |
| :--- | :--- | :--- |
| **Orbit Ellipse** | Exact true anomaly $\nu(t)$, semi-major axis $a$, inclination $i$, and eccentricity $e$. | Subtle glow shader on the trajectory ribbon. |
| **Spacecraft Lighting** | Directional sunlight vector $\mathbf{s}_{\odot}$, penumbra/umbra shadow transitions, planetary albedo flux. | Mild bloom on engine exhaust nozzle during burns. |
| **Solar Array Orientation** | Calculated $\cos(\theta)$ incidence angle, 1-axis/2-axis articulation toward Sun vector. | Micro-vibrational motor ripple. |
| **Ground Station Cone** | True $5^\circ$ elevation angle mask volume intercepting the orbital swath. | Translucent cyan wireframe surface. |
| **Planetary Atmosphere** | Physical Rayleigh/Mie scattering shader matching atmospheric scale height ($H \approx 8.5\text{ km}$). | Distant stars background skybox. |

---

## 2. SCENE ARCHITECTURE & COMPONENT HIERARCHY

The 3D engine is built on **React Three Fiber (R3F)** and `@react-three/drei`, leveraging a dual-scene hierarchy to avoid floating-point depth-buffer z-fighting across astronomical scales.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       R3F CANVAS (Fiber Root Context)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Viewport Manager] -> Dynamic Scale & Aspect Controller                    │
│  [Camera Rig]       -> CameraDirector (OrbitControls / FlyTo / Inertia)     │
│  [Lighting Engine]  -> Dynamic Sun Light + Body Albedo + Ambient Occlusion  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐          ┌──────────────────────────────────┐  │
│  │   SCENE 1: CELESTIAL    │          │     SCENE 2: SPACECRAFT LOCAL    │  │
│  │     MACRO-UNIVERSE      │          │            MICRO-CAD             │  │
│  ├─────────────────────────┤          ├──────────────────────────────────┤  │
│  │ - CelestialBody (Earth) │          │ - SpacecraftRig (Pivot Node)     │  │
│  │   • Surface Mesh + Bump │          │ - ModularSubsystemMounts         │  │
│  │   • Atmosphere GLSL     │          │   • Bus Core (CFRP/Alu)          │  │
│  │   • Night Lights Mask   │          │   • Deployable Wings (IK Anim)   │  │
│  │ - OrbitRibbon (GPU Inst)│          │   • Articulated Gimbals (Tracking│  │
│  │ - GroundStationCones    │          │   • Instrument Boresight Rays    │  │
│  │ - EclipseShadowCylinder │          │ - ThrusterPlumeFX (Instanced)    │  │
│  │ - GroundTrackPolyline   │          │ - ThermalHeatmapShader (Vertex)  │  │
│  └─────────────────────────┘          └──────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Post-Processing Pipeline] -> SMAA (Anti-Aliasing) + Selective UnrealBloom │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. COORDINATE SYSTEMS & SCALE MANAGEMENT

### 3.1 The Two-Scale Problem in Space Games
In real space, Earth has a radius of $6,378,137\text{ m}$, while a CubeSat is $0.3\text{ m}$. Rendering both in a single WebGL scene causes severe IEEE 754 32-bit floating-point depth buffer truncation (z-fighting and jitter).

### 3.2 Implemented Normalization Solution: "The Dual Scaling Model"
1. **Celestial Macro-World Scale:**
   * $1.0\text{ Scene Unit} = 1,000\text{ km}$ ($1\times 10^6\text{ m}$).
   * Earth Radius $R_E = 6.378137\text{ units}$.
   * LEO Orbit at $500\text{ km} = 6.878137\text{ units}$.
   * Moon Orbit at $384,400\text{ km} = 384.4\text{ units}$.
   * Near Camera Plane: $0.1$, Far Camera Plane: $10,000.0$ (logarithmic depth buffer enabled).
2. **Spacecraft Micro-CAD Scale (When zoomed into the satellite):**
   * $1.0\text{ CAD Unit} = 1.0\text{ meter}$.
   * When the camera switches from "Macro Orbit View" to "Spacecraft Tracking View," the spacecraft is rendered in an isolated local coordinate frame centered at origin $(0, 0, 0)$ with Earth positioned as a large textured sphere in the background along the negative nadir vector $-\hat{\mathbf{r}}$.

### 3.3 Reference Frames
* **ECI (Earth-Centered Inertial - J2000):** Primary inertial frame. $+X$ points to Vernal Equinox $\Upsilon$, $+Z$ points to Earth's rotational north pole, $+Y = +Z \times +X$. Orbits propagate in this frame.
* **ECEF (Earth-Centered Earth-Fixed):** Rotates with Earth at $\omega_{\oplus} = 7.292115\times 10^{-5}\text{ rad/s}$. Ground stations and terrain textures are bound to this frame.
* **RIC (Radial-Intrack-Crosstrack / Spacecraft LVLH):** Local orbital frame. $+\hat{\mathbf{R}}$ points nadir, $+\hat{\mathbf{I}}$ along velocity vector, $+\hat{\mathbf{C}}$ orbit normal. Payloads point along $+\hat{\mathbf{R}}$.

---

## 4. CAMERA CONTROLS & CINEMATIC MODES

The Camera Director (`CameraDirector.tsx`) manages 4 mutually exclusive observation modes with smooth spring transitions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAMERA DIRECTOR OPERATIONAL MODES                       │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ Mode Name         │ Target, Framing & Interaction Behavior                  │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 1. CAD_INSPECTOR  │ Spacecraft centered at origin. 360° orbit/pan/zoom.     │
│                   │ Used during Phase B/C spacecraft assembly.              │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 2. ORBIT_TRACKER  │ Camera locks onto spacecraft in orbit. As satellite     │
│                   │ moves around Earth, camera smoothly tracks position     │
│                   │ while maintaining Earth in the background.              │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 3. GLOBAL_SYNOPTIC│ Earth centered. Satellite and orbit trail seen as a     │
│                   │ thin glowing ribbon. 360° planetary overview.           │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 4. LAUNCH_CHASE   │ Locks onto rocket stage during ascent; tracks dynamic   │
│                   │ pressure shake and stage separation sequence.           │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

* **Smooth Transitions:** Interpolation using Hermite cubic polynomials (`gl-matrix` or Three.js `Vector3.lerp`) prevents disorienting camera snapping.
* **Auto-Framing Bounds:** The camera clamps zoom distance to avoid clipping inside the planetary surface or spacecraft hull.

---

## 5. LIGHTING & CUSTOM SHADER MATERIALS

### 5.1 Directional Solar Illumination & Eclipse Shadow Logic
* **Solar Directional Light:** A single intense directional light representing the Sun positioned along the solar ephemeris vector $\hat{\mathbf{s}}_{\odot}$.
* **Real-time Eclipse Raycast / Cylinder Check:**
  The shader evaluates the cylindrical shadow model in the vertex/fragment pipeline:
  $$\text{IsEclipse} = \left( \mathbf{r} \cdot \hat{\mathbf{s}}_{\odot} < 0 \right) \;\land\; \left( \|\mathbf{r} - (\mathbf{r} \cdot \hat{\mathbf{s}}_{\odot})\hat{\mathbf{s}}_{\odot}\| < R_{\oplus} \right)$$
  When true:
  1. Directional light intensity on spacecraft drops to zero.
  2. Earth night lights texture (`earth_lights_2048.webp`) blends in on the night hemisphere.

### 5.2 Earth Atmosphere Shader (Rayleigh & Mie Scattering Approximation)
A custom GLSL atmosphere rim shader creates an authentic blue halo around the planetary limb:
```glsl
// Custom Atmospheric Rim Fragment Shader
varying vec3 vNormal;
varying vec3 vViewPosition;
uniform vec3 uSunDirection;

void main() {
    float sunDot = max(0.0, dot(vNormal, uSunDirection));
    float viewDot = 1.0 - max(0.0, dot(vNormal, normalize(vViewPosition)));
    float atmosphereFactor = pow(viewDot, 3.5) * (0.3 + 0.7 * sunDot);
    vec3 atmosphereColor = vec3(0.2, 0.55, 0.95) * atmosphereFactor * 1.8;
    gl_FragColor = vec4(atmosphereColor, atmosphereFactor);
}
```

### 5.3 Spacecraft Thermal Heatmap Shader
Allows toggling a thermal diagnostic view where component vertex colors visualize heat dissipation:
* Deep blue: Cold zones ($< 0^\circ C$).
* Emerald: Nominal operational electronics ($15^\circ C\text{--}25^\circ C$).
* Crimson/White glow: Saturated high-power SAR radar or battery thermal runaway ($> 55^\circ C$).

---

## 6. ORBIT & TRAJECTORY RENDERING PIPELINE

### 6.1 Closed-Form Keplerian Orbit Ribbon (GPU Instanced)
Instead of plotting hundreds of dynamic mesh spheres, the orbit path is rendered as a continuous, high-performance GPU line ribbon:
* **Geometry:** `InstancedBufferGeometry` or `Line2` (from Three.js `LineGeometry`) with 256 discrete points.
* **Point Generation:**
  $$r(\nu) = \frac{a(1 - e^2)}{1 + e \cos(\nu)}$$
  Points are evaluated across true anomaly $\nu \in [0, 2\pi]$ and transformed via the orbital rotation matrix $R_z(-\Omega) R_x(-i) R_z(-\omega)$.
* **Dynamic Update:** When the user modifies altitude $h$ or inclination $i$ in the UI, the line buffer geometry updates in a single frame via `geometry.attributes.position.needsUpdate = true`.

### 6.2 Ground Track Mercator Projection
* The 3D position vector in ECEF coordinates is converted to geodetic latitude and longitude:
  $$\text{lat} = \arcsin\left(\frac{z}{r}\right), \quad \text{lon} = \arctan2(y, x)$$
* Projected onto both the 3D rotating globe as an equatorial swath ribbon and the 2D mission control map.

---

## 7. ANIMATION ARCHITECTURE & TELEMETRY SYNCHRONIZATION

The animation system operates on a **Deterministic Simulation Clock (MET - Mission Elapsed Time)**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SIMULATION STATE (Zustand Store)                   │
│   - Mission Elapsed Time (t)      - Solar Array Deploy Pct (0.0 - 1.0)      │
│   - Time Warp Multiplier (1x-1000x)- Thruster Firing State (Active/Off)      │
│   - Spacecraft State Vector (r, v) - Battery SoC % / Temperature (°C)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          R3F useFrame RENDER LOOP                           │
│  1. Ingest simulation state vector at current delta-time.                   │
│  2. Interpolate spacecraft true anomaly: nu(t + dt) via mean motion.        │
│  3. Rotate Earth at sidereal rate: Earth.rotation.y = omega * t.            │
│  4. Update Spacecraft Rig position: Spacecraft.position.set(x, y, z).       │
│  5. Articulate Solar Wings: WingPivot.rotation.z = slerp(SunDirection).    │
│  6. Trigger Thruster Particles if Propulsion.isFiring == true.              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Deployment Inverse Kinematics (IK)
* Solar wings have 3 deployment stages: Stowed ($0\%$) $\to$ Root Hinge Deployment ($50\%$) $\to$ Panel Accordion Unfurl ($100\%$).
* Controlled via React Spring / GSAP driven by simulation events, preventing jerky animation snaps.

---

## 8. REALISTIC MISSION SEQUENCE VISUALIZATIONS

1. **Launch Sequence:**
   * Ground pad view at Cape Canaveral / Kourou.
   * Vertical liftoff with trailing particle exhaust plume.
   * Transonic Max-Q shockwave ring effect.
   * Stage 1 MECO and interstage separation mesh jettison.
   * Fairing halving separation showing stowed spacecraft inside.
2. **Planetary Approach & Insertion:**
   * Hyperbolic approach trajectory vector glowing amber.
   * Spacecraft slews to retrograde attitude.
   * Thruster burn plume lights up for the exact duration of the insertion $\Delta v$ burn.
   * Trajectory dynamically collapses from open hyperbola into closed stable ellipse in real time!

---

## 9. PERFORMANCE & MOBILE OPTIMIZATION MATRIX

To ensure fluid 60 FPS performance on laptops and mobile devices:

| Optimization Layer | Implementation Strategy |
| :--- | :--- |
| **Draw Call Reduction** | Batch all static spacecraft structural components into a single merged geometry (`BufferGeometryUtils.mergeGeometries`). |
| **Texture Compression** | Earth surface maps converted to KTX2 / Basis Universal GPU textures (80% VRAM reduction compared to PNG). |
| **LOD (Level of Detail)** | High-poly 4K Earth mesh switches to 1K low-poly sphere when camera zooms in close to the spacecraft. |
| **Mobile DPR Clamping** | Clamp device pixel ratio to `Math.min(window.devicePixelRatio, 1.5)` to eliminate GPU fill-rate throttling on high-DPI phones. |
| **Garbage Collection (GC)** | Zero allocations inside the `useFrame` render loop. All scratch `Vector3`, `Matrix4`, and `Quaternion` variables are pre-allocated outside the loop. |

---

## 10. RECOMMENDED OPEN-SOURCE ASSETS & LIBRARIES

All recommended assets utilize **MIT, Apache 2.0, or NASA Public Domain** licenses:

### 10.1 Libraries & Packages
* `@react-three/fiber` (MIT): React reconciler for Three.js.
* `@react-three/drei` (MIT): High-performance camera rigs, line ribbons, and shaders.
* `three-stdlib` (MIT): Optimized post-processing, Line2, and GLTF loaders.
* `gl-matrix` (MIT): High-performance vector/matrix math.

### 10.2 Textures & Planetary Models
* **Earth Texture Maps (NASA Visible Earth / Blue Marble):** Public Domain.
  * Day Surface: *NASA Blue Marble Next Generation (2K/4K WebP)*.
  * Night City Lights: *NASA Black Marble (2K WebP)*.
  * Cloud Layer: *NASA GOES Composite (Translucent sphere)*.
* **Moon & Mars Surface Maps (NASA SVS / USGS Astrogeology):** Public Domain.
  * Lunar LRO/LOLA Elevation & Albedo Maps.
  * Mars MOLA High-Resolution Surface Textures.

### 10.3 Spacecraft 3D Models
* **Modular Procedural Bus Assembly:** Clean, low-poly procedural geometries generated directly via Three.js primitives (`BoxGeometry`, `CylinderGeometry`, `RingGeometry`) styled with carbon-fiber and gold MLI PBR materials, supplemented by verified NASA 3D Resources (e.g., *NASA 3D Resources CubeSat & Deep Space probe models - Public Domain*).
