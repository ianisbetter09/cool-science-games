// Establish connection with the server
const socket = io();

// Store other players
const otherPlayers = {};

// Initialize Three.js scene, camera, and renderer
let scene, camera, renderer;
let playerMesh;
let yaw = 0, pitch = 0;
const move = { forward: false, backward: false, left: false, right: false };
let velocity = new THREE.Vector3();
let direction = new THREE.Vector3();
const gravity = -0.3;
const jumpStrength = 0.03;
let canJump = false;
let isThirdPerson = false;
let collidables = [];

init();
animate();

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 100, 500);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  document.body.appendChild(renderer.domElement);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0x404040, 2);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 1);
  dirLight.position.set(10, 20, 10);
  dirLight.castShadow = true;
  scene.add(dirLight);

  // Ground
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(1000, 1000),
    new THREE.MeshStandardMaterial({ color: 0x228B22 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  ground.name = "ground";
  scene.add(ground);
  collidables.push(ground);

  // Player (green box)
  playerMesh = new THREE.Mesh(
    new THREE.BoxGeometry(1, 2, 1),
    new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  );
  playerMesh.position.set(0, 5, 0);
  playerMesh.castShadow = true;
  playerMesh.receiveShadow = true;
  scene.add(playerMesh);

  // Build a simple house
  const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });

  function createWall(x, y, z, w, h, d) {
    const wall = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      wallMaterial
    );
    wall.position.set(x, y, z);
    wall.castShadow = true;
    wall.receiveShadow = true;
    scene.add(wall);
    collidables.push(wall);
  }

  // Floor and roof
  createWall(0, 0.1, 0, 20, 0.2, 20); // floor
  createWall(0, 5, 0, 20, 0.2, 20); // roof

  // Walls
  createWall(-10, 2.5, 0, 0.2, 5, 20); // left
  createWall(10, 2.5, 0, 0.2, 5,
::contentReference[oaicite:14]{index=14}
 
