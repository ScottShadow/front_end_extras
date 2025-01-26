const express = require("express");
const WebSocket = require("ws");

const app = express();
const server = require("http").createServer(app);
const wss = new WebSocket.Server({ server });

// Store connected users
let users = {};

// Handle WebSocket connections
wss.on("connection", (ws) => {
  ws.on("message", (message) => {
    const data = JSON.parse(message);

    if (data.type === "register") {
      // Register a new user
      users[data.username] = ws;
      console.log(`${data.username} connected`);
    } else if (data.type === "tag") {
      // Send a notification to the tagged user
      const target = users[data.target];
      if (target) {
        target.send(JSON.stringify({
          type: "notification",
          message: `${data.username} tagged you!`
        }));
      }
    }
  });

  ws.on("close", () => {
    // Clean up users on disconnect
    Object.keys(users).forEach((username) => {
      if (users[username] === ws) delete users[username];
    });
  });
});

server.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
