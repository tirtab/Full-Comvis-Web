const express = require("express");
const mqtt = require("mqtt");
const cors = require("cors");

const app = express();
app.use(cors());

const PORT = 5000;

// Koneksi ke MQTT Broker
const mqttClient = mqtt.connect("ws://localhost:9001"); // WebSocket Mosquitto

mqttClient.on("connect", () => {
  console.log("Connected to MQTT Broker!");
  mqttClient.subscribe("object-detection/results", (err) => {
    if (!err) {
      console.log("Subscribed to topic: object-detection/results");
    }
  });
});

let detectionData = {};

mqttClient.on("message", (topic, message) => {
  if (topic === "object-detection/results") {
    detectionData = JSON.parse(message.toString());
  }
});

// Endpoint untuk data deteksi
app.get("/api/detections", (req, res) => {
  res.json(detectionData);
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
