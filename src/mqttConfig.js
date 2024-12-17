import mqtt from "mqtt";

const MQTT_BROKER_URL = "ws://localhost:9001";
const TOPIC = "object-detection/results";

let isSubscribed = false; // Flag untuk mencegah duplikasi subscribe
let client; // MQTT Client variable

export const connectToMQTT = (onMessageCallback) => {
  client = mqtt.connect(MQTT_BROKER_URL, {
    clean: true, // Pastikan sesi clean, tidak ada pesan yang tertunda
  });

  // Event ketika koneksi berhasil
  client.on("connect", () => {
    console.log("Connected to MQTT Broker!");

    // Pastikan hanya sekali melakukan subscribe
    if (!isSubscribed) {
      client.subscribe(TOPIC, (err) => {
        if (!err) {
          console.log(`Subscribed to topic: ${TOPIC}`);
          isSubscribed = true; // Tandai subscribe berhasil
        } else {
          console.error("Failed to subscribe, retrying in 2 seconds...", err);
          setTimeout(() => client.emit("connect"), 2000); // Retry connect
        }
      });
    }
  });

  // Event ketika menerima pesan dari MQTT
  client.on("message", (topic, message) => {
    if (topic === TOPIC) {
      const data = JSON.parse(message.toString());
      onMessageCallback(data); // Kirim data ke callback
    }
  });

  // Event jika ada error koneksi
  client.on("error", (err) => {
    console.error("MQTT Connection Error:", err);
  });

  // Event ketika koneksi terputus
  client.on("close", () => {
    console.warn("MQTT connection closed. Reconnecting...");
    isSubscribed = false; // Reset flag jika koneksi putus
    setTimeout(() => {
      connectToMQTT(onMessageCallback); // Coba connect ulang
    }, 2000);
  });

  return client;
};
