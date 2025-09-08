let y = 0;
let x = 100;
const gravity = 1.5;
let velocityY = 0;
const jumpStrength = 25;
let isJumping = false;
const moveSpeed = 10;

let level = 1;
let ground, levelBox;
let grass, dirt, platform;
let updateRunning = false;
const keysPressed = new Set();

const box = document.getElementById('player');

function startLevel(n) {
  console.log(`Starting Level ${n}`);

  // Deactivate all levels
  const allLevels = document.querySelectorAll('[id^="level"]');
  allLevels.forEach((level) => {
    level.style.display = 'none';
  });

  // Get current level by ID
  const currentLevel = document.getElementById(`level${n}`);
  if (!currentLevel) {
    console.log('No more levels.');
    updateRunning = false;
    return;
  }

  // Activate this level
  currentLevel.style.display = 'block';

  // Get ground/platforms/target
  ground = currentLevel.querySelector('.grass');
  levelBox = currentLevel.querySelector('.levelBox');
  platform = currentLevel.querySelector('.platform');

  // Reset position
  x = 100;
  y = ground.offsetTop - box.offsetHeight;
  velocityY = 0;
  isJumping = false;

  // Set initial position
  box.style.top = y + 'px';
  box.style.left = x + 'px';

    if (!updateRunning) {
    updateRunning = true;
    requestAnimationFrame(update);
  }


  console.log('Level Loaded!');
}

function completeLevel() {
  level++;
  startLevel(level);
  update();
}


function update() {
  if (level == 2 || level == 3){
    if (!box || !levelBox || !ground || !platform) {
      updateRunning = false;
      return;
    }

    // Apply gravity
    velocityY += gravity;
    y += velocityY;

    // Rects and positions
    const groundRect = ground.getBoundingClientRect();
    const platformRect = platform.getBoundingClientRect();
    const containerRect = box.offsetParent.getBoundingClientRect();

    const groundTop = groundRect.top - containerRect.top + 10;
    const platformTop = platformRect.top - containerRect.top + 10;
    const platformBottom = platformRect.bottom - containerRect.top + 10;
    const platformLeft = platformRect.left - containerRect.left + 8;
    const platformRight = platformRect.right - containerRect.left + 8;

    const boxHeight = box.offsetHeight;
    const boxWidth = box.offsetWidth;
    const boxBottom = y + boxHeight;
    const boxRight = x + boxWidth;
    const boxLeft = x

    // ==== PLATFORM TOP COLLISION ====
    if (
      velocityY >= 0 && // falling down
      boxBottom <= platformTop + 5 && // not inside platform already
      boxBottom + velocityY >= platformTop && // will intersect from above
      boxRight > platformLeft &&
      x < platformRight
    ) {
      y = platformTop - boxHeight;
      velocityY = 0;
      isJumping = false;
    }

    // ==== PLATFORM SIDE COLLISION ====
    // Only block from sides if not on top or falling onto it
    const isAbovePlatform = boxBottom <= platformTop;
    if (
      velocityY >= 0 && // falling down
      boxBottom <= platformTop + 5 && // not inside platform already
      boxBottom + velocityY >= platformTop && // will intersect from above
      boxRight > platformLeft &&
      x < platformRight
    ) {
      y = platformTop - boxHeight;
      velocityY = 0;
      isJumping = false;
    }


    // ==== GROUND COLLISION ====
    if (y + boxHeight > groundTop) {
      y = groundTop - boxHeight;
      velocityY = 0;
      isJumping = false;
    }

    // Horizontal movement
    if (keysPressed.has('ArrowRight')) x += moveSpeed;
    if (keysPressed.has('ArrowLeft')) x -= moveSpeed;

    // Prevent off-screen
    const containerWidth = box.offsetParent.clientWidth;
    if (x < 0) x = 0;
    if (x + boxWidth > containerWidth) x = containerWidth - boxWidth;

    // Apply positions
    box.style.top = y + 'px';
    box.style.left = x + 'px';

    // Level complete check
    const boxRect = box.getBoundingClientRect();
    const targetRect = levelBox.getBoundingClientRect();
    if (
      boxRect.right > targetRect.left &&
      boxRect.left < targetRect.right &&
      boxRect.bottom > targetRect.top &&
      boxRect.top < targetRect.bottom
    ) {
      console.log('Level complete!');
      completeLevel();
      return;
    }

    requestAnimationFrame(update);
    console.log("Updating frame", level);


  } else {
    if (!box || !levelBox || !ground) {
      updateRunning = false;
      return;
    }

    // Apply gravity
    velocityY += gravity;
    y += velocityY;

    // Collision with ground
    const groundRect = ground.getBoundingClientRect();
    const boxRect = box.getBoundingClientRect();
    const containerRect = box.offsetParent.getBoundingClientRect();

    const groundTop = groundRect.top - containerRect.top;
    const boxHeight = box.offsetHeight;

    if (y + boxHeight > groundTop) {
      y = groundTop - boxHeight + 10;
      velocityY = 0;
      isJumping = false;
    }

    // Horizontal movement
    if (keysPressed.has('ArrowRight')) x += moveSpeed;
    if (keysPressed.has('ArrowLeft')) x -= moveSpeed;

    // Prevent off-screen inside container width
    const containerWidth = box.offsetParent.clientWidth;
    const boxWidth = box.offsetWidth;
    if (x < 0) x = 0;
    if (x + boxWidth > containerWidth) x = containerWidth - boxWidth;

    // Apply positions
    box.style.top = y + 'px';
    box.style.left = x + 'px';

    // Check next level collision
    const targetRect = levelBox.getBoundingClientRect();
    if (
      boxRect.right > targetRect.left &&
      boxRect.left < targetRect.right &&
      boxRect.bottom > targetRect.top &&
      boxRect.top < targetRect.bottom
    ) {
      console.log('Level complete!');
      completeLevel();
      return;
    }

    requestAnimationFrame(update);
    console.log("Updating frame", level);

  }
}


function jump() {
  if (!isJumping) {
    velocityY = -jumpStrength;
    isJumping = true;
  }
}

window.addEventListener('keydown', (event) => {
  keysPressed.add(event.key);
  if (event.key === 'ArrowUp') jump();
});
window.addEventListener('keyup', (event) => {
  keysPressed.delete(event.key);
});

window.onload = function () {
  startLevel(level);

}



