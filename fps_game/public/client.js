const socket = io();

let scene, camera, renderer;
let localPlayer;
let players = {};

init();

function init() {
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.y = 1.6;

  renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(1, 1, 1).normalize();
  scene.add(light);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(100, 100),
    new THREE.MeshStandardMaterial({ color: 0x222222 })
  );
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

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
