const socket = io();
const players = {};

socket.on('currentPlayers', (serverPlayers) => {
  for (const id in serverPlayers) {
    if (id !== socket.id) {
      players[id] = serverPlayers[id];
      // render other player
    }
  }
});

socket.on('newPlayer', (player) => {
  players[player.id] = player;
  // render new player
});

socket.on('playerMoved', (player) => {
  if (players[player.id]) {
    players[player.id].x = player.x;
    players[player.id].y = player.y;
    // update position
  }
});

socket.on('playerDisconnected', (id) => {
  delete players[id];
  // remove from screen
});

// Send movement to server
document.addEventListener('keydown', (e) => {
  // replace with your own input logic
  let move = { x: 0, y: 0 };
  if (e.key === 'ArrowUp') move.y -= 1;
  if (e.key === 'ArrowDown') move.y += 1;
  if (e.key === 'ArrowLeft') move.x -= 1;
  if (e.key === 'ArrowRight') move.x += 1;

  // update local player movement
  // send to server
  socket.emit('playerMovement', move);
});
