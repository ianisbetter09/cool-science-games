const socket = io();

let scene, camera, renderer;
let localPlayer;
let players = {};

init();

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb); // Sky blue

  camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.y = 1.6;

  renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0x404040);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(10, 20, 10);
  scene.add(ambientLight, directionalLight);

  // Ground
  const groundGeo = new THREE.PlaneGeometry(100, 100);
  const groundMat = new THREE.MeshStandardMaterial({ color: 0x228B22 }); // Forest green
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // Add some "buildings"
  for (let i = 0; i < 5; i++) {
    const box = new THREE.Mesh(
      new THREE.BoxGeometry(4, 6, 4),
      new THREE.MeshStandardMaterial({ color: 0x8B0000 }) // Dark red
    );
    box.position.set(
      (Math.random() - 0.5) * 80,
      3,
      (Math.random() - 0.5) * 80
    );
    scene.add(box);
  }

  // Local player
  localPlayer = { mesh: createPlayerMesh(), id: null };
  scene.add(localPlayer.mesh);

  animate();
}


function createPlayerMesh(color = 0x00ff00) {
  const geometry = new THREE.BoxGeometry(1, 2, 1);
  const material = new THREE.MeshStandardMaterial({ color });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.y = 1;
  return mesh;
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);

  // Send position
  if (localPlayer.id) {
    socket.emit('move', {
      x: localPlayer.mesh.position.x,
      y: localPlayer.mesh.position.y,
      z: localPlayer.mesh.position.z,
      rotation: localPlayer.mesh.rotation
    });
  }

  // WASD movement
  const speed = 0.1;
  if (keys['w']) localPlayer.mesh.position.z -= speed;
  if (keys['s']) localPlayer.mesh.position.z += speed;
  if (keys['a']) localPlayer.mesh.position.x -= speed;
  if (keys['d']) localPlayer.mesh.position.x += speed;
}

const keys = {};
window.addEventListener('keydown', (e) => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false);

// Handle Socket Events
socket.on('currentPlayers', (data) => {
  for (let id in data) {
    if (id !== socket.id) {
      const other = createPlayerMesh(0xff0000);
      players[id] = { mesh: other };
      scene.add(other);
    } else {
      localPlayer.id = id;
    }
  }
});

socket.on('newPlayer', (data) => {
  const newMesh = createPlayerMesh(0xff0000);
  players[data.id] = { mesh: newMesh };
  scene.add(newMesh);
});

socket.on('playerMoved', (data) => {
  const player = players[data.id];
  if (player) {
    player.mesh.position.set(data.x, data.y, data.z);
    player.mesh.rotation.copy(data.rotation);
  }
});

socket.on('playerDisconnected', (id) => {
  if (players[id]) {
    scene.remove(players[id].mesh);
    delete players[id];
  }
});
