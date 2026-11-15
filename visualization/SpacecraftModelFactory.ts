import * as THREE from 'three';

/**
 * Procedural Spacecraft Mesh Generator
 * Generates lightweight, high-performance PBR spacecraft models based on component selections.
 * MIT License compatible.
 */

export interface SpacecraftConfig {
  chassisClass: 'CUBESAT_12U' | 'SMALLSAT_LEO' | 'MEDIUM_BUS' | 'HEAVY_PROBE';
  solarWingType: 'FIXED_BODY' | 'DEPLOYABLE_FIXED' | 'ACTIVE_1_AXIS_TRACKING';
  antennaType: 'OMNI_PATCH' | 'HORN' | 'PARABOLIC_DISH';
  propulsionType: 'COLD_GAS' | 'HYDRAZINE' | 'ION_THRUSTER';
  hasDeployableBoom: boolean;
  solarDeployPct: number; // 0.0 to 1.0
}

export class SpacecraftModelFactory {
  // PBR Material Palette
  private static materials = {
    aluminumStructure: new THREE.MeshStandardMaterial({
      color: 0x8a95a5,
      metalness: 0.85,
      roughness: 0.25,
    }),
    goldMLIBus: new THREE.MeshStandardMaterial({
      color: 0xd4af37,
      metalness: 0.95,
      roughness: 0.35,
    }),
    carbonFiberCFRP: new THREE.MeshStandardMaterial({
      color: 0x1f242d,
      metalness: 0.3,
      roughness: 0.6,
    }),
    solarCellSurface: new THREE.MeshStandardMaterial({
      color: 0x1a2e5a,
      metalness: 0.8,
      roughness: 0.2,
      emissive: 0x051025,
    }),
    thrusterNozzle: new THREE.MeshStandardMaterial({
      color: 0x333333,
      metalness: 0.9,
      roughness: 0.4,
    }),
  };

  /**
   * Builds an optimized modular spacecraft Group representing the design configuration.
   */
  public static createSpacecraftGroup(config: SpacecraftConfig): THREE.Group {
    const root = new THREE.Group();
    root.name = 'SpacecraftRig';

    // 1. Primary Bus Structure
    let busMesh: THREE.Mesh;
    if (config.chassisClass === 'CUBESAT_12U') {
      const geo = new THREE.BoxGeometry(0.24, 0.36, 0.24);
      busMesh = new THREE.Mesh(geo, this.materials.aluminumStructure);
    } else if (config.chassisClass === 'SMALLSAT_LEO') {
      const geo = new THREE.CylinderGeometry(0.5, 0.5, 0.8, 6);
      busMesh = new THREE.Mesh(geo, this.materials.carbonFiberCFRP);
    } else {
      const geo = new THREE.BoxGeometry(0.9, 1.2, 0.9);
      busMesh = new THREE.Mesh(geo, this.materials.goldMLIBus);
    }
    busMesh.name = 'BusCore';
    root.add(busMesh);

    // 2. Solar Arrays (Left & Right Wings with deployment pivoting)
    if (config.solarWingType === 'DEPLOYABLE_FIXED' || config.solarWingType === 'ACTIVE_1_AXIS_TRACKING') {
      const wingSpan = config.chassisClass === 'HEAVY_PROBE' ? 1.8 : 0.8;
      const wingWidth = 0.45;
      const panelGeo = new THREE.BoxGeometry(wingSpan, 0.02, wingWidth);

      // Left Wing Pivot
      const leftPivot = new THREE.Group();
      leftPivot.name = 'LeftSolarPivot';
      leftPivot.position.set(-0.5, 0, 0);

      const leftPanel = new THREE.Mesh(panelGeo, this.materials.solarCellSurface);
      leftPanel.position.set(-wingSpan / 2, 0, 0);
      leftPivot.add(leftPanel);

      // Deployment rotation (interpolates from stowed 90 deg fold to 0 deg flat)
      leftPivot.rotation.z = (1.0 - config.solarDeployPct) * (Math.PI / 2);
      root.add(leftPivot);

      // Right Wing Pivot
      const rightPivot = new THREE.Group();
      rightPivot.name = 'RightSolarPivot';
      rightPivot.position.set(0.5, 0, 0);

      const rightPanel = new THREE.Mesh(panelGeo, this.materials.solarCellSurface);
      rightPanel.position.set(wingSpan / 2, 0, 0);
      rightPivot.add(rightPanel);

      rightPivot.rotation.z = -(1.0 - config.solarDeployPct) * (Math.PI / 2);
      root.add(rightPivot);
    }

    // 3. Communication Antenna
    if (config.antennaType === 'PARABOLIC_DISH') {
      const dishGroup = new THREE.Group();
      dishGroup.name = 'KaDishGimbal';
      dishGroup.position.set(0, 0.65, 0.2);

      const dishGeo = new THREE.SphereGeometry(0.35, 24, 12, 0, Math.PI * 2, 0, Math.PI / 3);
      const dishMesh = new THREE.Mesh(dishGeo, this.materials.aluminumStructure);
      dishMesh.rotation.x = Math.PI; // Face outwards
      dishGroup.add(dishMesh);
      root.add(dishGroup);
    }

    // 4. Propulsion Nozzle
    const nozzleGeo = new THREE.ConeGeometry(0.12, 0.25, 16, 1, true);
    const nozzleMesh = new THREE.Mesh(nozzleGeo, this.materials.thrusterNozzle);
    nozzleMesh.name = 'MainEngineNozzle';
    nozzleMesh.position.set(0, -0.65, 0);
    nozzleMesh.rotation.x = Math.PI;
    root.add(nozzleMesh);

    return root;
  }
}
