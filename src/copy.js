import mqtt from "mqtt";

// Konfigurasi MQTT
const MQTT_BROKER_URL = "ws://localhost:9001";
const TOPIC = "object-detection/results";

// Fungsi untuk mengatur koneksi MQTT
export const connectToMQTT = (onMessageCallback) => {
  const client = mqtt.connect(MQTT_BROKER_URL);

  // Event ketika koneksi berhasil
  client.on("connect", () => {
    console.log("Connected to MQTT Broker!");

    // Lakukan subscribe setelah koneksi berhasil
    client.subscribe(TOPIC, (err) => {
      if (!err) {
        console.log(`Subscribed to topic: ${TOPIC}`);
      } else {
        console.error("Failed to subscribe:", err);
      }
    });
  });

  // Event ketika menerima pesan dari MQTT
  client.on("message", (topic, message) => {
    if (topic === TOPIC) {
      const data = JSON.parse(message.toString());
      onMessageCallback(data); // Kirim data ke callback
    }
  });

  client.on("error", (err) => {
    console.error("MQTT Connection Error:", err);
  });

  client.on("close", () => {
    console.log("MQTT connection closed.");
  });

  return client;
};
