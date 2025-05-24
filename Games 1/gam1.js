const box = document.getElementById('box');
const ground = document.getElementById('ground');

let y = 0;                  // vertical position
let x = 100;                // horizontal position (start)
const gravity = 1.5;
let velocityY = 0;
const jumpStrength = 25;
let isJumping = false;
const moveSpeed = 10;        // pixels per frame for smooth movement

const keysPressed = new Set();

function update() {
  const groundTop = ground.getBoundingClientRect().top;
  const boxHeight = box.offsetHeight;
  const boxWidth = box.offsetWidth;
  const windowWidth = window.innerWidth;

  // Apply gravity for vertical movement
  velocityY += gravity;
  y += velocityY;

  // Prevent box from going below ground
  if (y + boxHeight > groundTop) {
    y = groundTop - boxHeight;
    velocityY = 0;
    isJumping = false;
  }

  // Horizontal movement
  if (keysPressed.has('ArrowRight')) {
    x += moveSpeed;
  }
  if (keysPressed.has('ArrowLeft')) {
    x -= moveSpeed;
  }

  // Prevent box from moving off-screen
  if (x < 0) x = 0;
  if (x + boxWidth > windowWidth) x = windowWidth - boxWidth;

  box.style.top = y + 'px';
  box.style.left = x + 'px';

  requestAnimationFrame(update);
}

function jump() {
  if (!isJumping) {
    velocityY = -jumpStrength;
    isJumping = true;
  }
}

window.addEventListener('keydown', (event) => {
  keysPressed.add(event.key);
  if (event.key === 'ArrowUp') {
    jump();
  }
});

window.addEventListener('keyup', (event) => {
  keysPressed.delete(event.key);
});

// Start the loop
update();
