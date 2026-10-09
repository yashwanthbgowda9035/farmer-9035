/**
 * KrishiMitra AI — 3D Digital Twin WebGL Plant Visualizer
 * Powered by Three.js (Hardware Accelerated, Interactive Orbit & Hotspots)
 */

window.initDigitalTwin = function(containerId) {
  const container = document.getElementById(containerId);
  if (!container || typeof THREE === "undefined") return;

  const width = container.clientWidth;
  const height = container.clientHeight || 380;

  // 1. Scene, Camera, Renderer
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4f7f4);

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 4.5, 9);
  camera.lookAt(0, 1.8, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // 2. Lighting Setup
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
  scene.add(ambientLight);

  const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.2);
  sunLight.position.set(5, 12, 7);
  sunLight.castShadow = true;
  scene.add(sunLight);

  const greenFill = new THREE.DirectionalLight(0x81c995, 0.4);
  greenFill.position.set(-5, 3, -5);
  scene.add(greenFill);

  // 3. Plant Base & Soil Pot
  const plantGroup = new THREE.Group();
  scene.add(plantGroup);

  // Terracotta / Soil Pot
  const potGeo = new THREE.CylinderGeometry(1.6, 1.2, 1.4, 24);
  const potMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.8 });
  const pot = new THREE.Mesh(potGeo, potMat);
  pot.position.y = 0.7;
  pot.receiveShadow = true;
  plantGroup.add(pot);

  // Soil Layer
  const soilGeo = new THREE.CylinderGeometry(1.55, 1.55, 0.15, 24);
  const soilMat = new THREE.MeshStandardMaterial({ color: 0x3f2e18, roughness: 0.95 });
  const soil = new THREE.Mesh(soilGeo, soilMat);
  soil.position.y = 1.35;
  plantGroup.add(soil);

  // 4. Plant Stem & Foliage
  const stemMat = new THREE.MeshStandardMaterial({ color: 0x2d6a4f, roughness: 0.6 });
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x40916c, roughness: 0.4, side: THREE.DoubleSide });
  const healthyLeafMat = new THREE.MeshStandardMaterial({ color: 0x52b788, roughness: 0.3, side: THREE.DoubleSide });

  // Main Stem
  const stemGeo = new THREE.CylinderGeometry(0.12, 0.18, 3.2, 16);
  const stem = new THREE.Mesh(stemGeo, stemMat);
  stem.position.y = 2.9;
  stem.castShadow = true;
  plantGroup.add(stem);

  // Leaves & Branches Generator
  function createLeaf(x, y, z, rotX, rotY, rotZ, scale = 1, isTarget = false) {
    const leafShape = new THREE.Shape();
    leafShape.moveTo(0, 0);
    leafShape.bezierCurveTo(0.4, 0.4, 0.6, 1.0, 0, 1.8);
    leafShape.bezierCurveTo(-0.6, 1.0, -0.4, 0.4, 0, 0);

    const leafGeo = new THREE.ShapeGeometry(leafShape);
    const mesh = new THREE.Mesh(leafGeo, isTarget ? leafMat : healthyLeafMat);
    mesh.position.set(x, y, z);
    mesh.rotation.set(rotX, rotY, rotZ);
    mesh.scale.set(scale, scale, scale);
    mesh.castShadow = true;
    plantGroup.add(mesh);
    return mesh;
  }

  // Tier 1 Leaves
  createLeaf(0, 2.2, 0.1, 0.6, 0.4, -0.7, 0.9);
  createLeaf(0, 2.3, -0.1, -0.5, 2.4, 0.6, 0.85);

  // Tier 2 Leaves
  createLeaf(0, 3.1, 0.1, 0.4, -1.2, -0.5, 1.1, true);
  createLeaf(0, 3.2, -0.1, -0.3, 1.0, 0.5, 1.05);

  // Top Canopy
  createLeaf(0, 4.1, 0, 0.2, 0, -0.3, 0.75);
  createLeaf(0, 4.2, 0, -0.2, Math.PI, 0.3, 0.7);

  // Diagnostic Pulse Hotspot (Target Leaf)
  const hotspotGeo = new THREE.SphereGeometry(0.2, 16, 16);
  const hotspotMat = new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.85 });
  const hotspot = new THREE.Mesh(hotspotGeo, hotspotMat);
  hotspot.position.set(0.7, 3.4, 0.6);
  plantGroup.add(hotspot);

  // 5. Interactive Mouse Orbit Controls
  let isDragging = false;
  let previousMousePosition = { x: 0, y: 0 };

  container.addEventListener("mousedown", (e) => {
    isDragging = true;
    previousMousePosition = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener("mouseup", () => { isDragging = false; });

  container.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - previousMousePosition.x;
    plantGroup.rotation.y += deltaX * 0.008;
    previousMousePosition = { x: e.clientX, y: e.clientY };
  });

  // Touch Support for Mobile
  container.addEventListener("touchmove", (e) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      const deltaX = touch.clientX - (previousMousePosition.x || touch.clientX);
      plantGroup.rotation.y += deltaX * 0.008;
      previousMousePosition = { x: touch.clientX, y: touch.clientY };
    }
  }, { passive: true });

  // 6. Animation Loop
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    // Subtle natural wind sway
    if (!isDragging) {
      plantGroup.rotation.y += 0.003;
    }
    stem.rotation.z = Math.sin(elapsedTime * 1.5) * 0.02;

    // Pulse Hotspot
    const pulse = 1.0 + Math.sin(elapsedTime * 4.0) * 0.25;
    hotspot.scale.set(pulse, pulse, pulse);

    renderer.render(scene, camera);
  }

  animate();

  // Responsive Resize
  window.addEventListener("resize", () => {
    const newWidth = container.clientWidth;
    const newHeight = container.clientHeight || 380;
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);
  });
};
