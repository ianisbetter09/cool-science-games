const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

app.use(express.static('public'));

const players = {};

io.on('connection', (socket) => {
  console.log(`Player connected: ${socket.id}`);

  // Add new player
  players[socket.id] = {
    x: 0,
    y: 0,
    id: socket.id
  };

  // Send existing players to the new player
  socket.emit('currentPlayers', players);

  // Notify others about the new player
  socket.broadcast.emit('newPlayer', players[socket.id]);

  // Listen for movement
  socket.on('playerMovement', (data) => {
    if (players[socket.id]) {
      players[socket.id].x = data.x;
      players[socket.id].y = data.y;
      socket.broadcast.emit('playerMoved', players[socket.id]);
    }
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log(`Player disconnected: ${socket.id}`);
    delete players[socket.id];
    io.emit('playerDisconnected', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
http.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
