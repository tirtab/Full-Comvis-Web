import cv2
import ultralytics
from ultralytics import YOLO
from flask import Flask, jsonify
from flask_mqtt import Mqtt
import time
import json
import base64
import threading

# Inisialisasi YOLOv8
model = YOLO("yolov8n.pt")  # Gunakan model YOLOv8 pre-trained

# Setup Flask dan Flask-MQTT
app = Flask(__name__)
app.config["MQTT_BROKER_URL"] = "localhost"  # Broker MQTT publik
app.config["MQTT_BROKER_PORT"] = 1883
app.config["MQTT_KEEP_ALIVE"] = 60
app.config["MQTT_TLS_ENABLED"] = False
mqtt = Mqtt(app)

# Variabel untuk menyimpan objek deteksi dan frame
detected_objects = []
frame_base64 = None


# Fungsi untuk meng-handle pesan MQTT yang diterima
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global detected_objects, frame_base64
    payload = json.loads(message.payload.decode())
    detected_objects = payload["objects"]
    frame_base64 = payload["frame"]
    print(f"Received message: {payload}")


# Fungsi untuk memulai loop MQTT
def mqtt_loop():
    mqtt.client.loop_forever()


# Endpoint untuk mendapatkan deteksi objek
@app.route("/api/detections", methods=["GET"])
def get_detections():
    return jsonify({"objects": detected_objects, "frame": frame_base64})


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")


def detect_objects():
    cap = cv2.VideoCapture(1)  # Ambil feed kamera

    if not cap.isOpened():
        print("Error: Kamera tidak terdeteksi!")
    else:
        print("Kamera terdeteksi.")

    # Inisialisasi variabel waktu untuk FPS
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Tidak bisa membaca frame!")
            break
        
        # Waktu saat ini
        current_time = time.time()
        elapsed_time = current_time - prev_time
        prev_time = current_time

        # Hitung FPS
        fps = 1 / elapsed_time if elapsed_time > 0 else 0
            
        # Lakukan deteksi menggunakan YOLO
        results = model(frame)
        detected_objects = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detected_objects.append(
                    {
                        "class": model.names[cls],
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                    }
                )
                
                 # Gambar bounding box
                label = f"{model.names[cls]} ({conf:.2f})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                

        print("Detected objects:", detected_objects)
        # Tambahkan FPS ke frame
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Resize frame sebelum encode
        frame = cv2.resize(frame, (640, 480))  # Sesuaikan resolusi sesuai kebutuhan

        # Konversi frame ke format base64
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        frame_base64 = base64.b64encode(buffer).decode("utf-8")

        # Log base64 frame
        print(
            "Frame base64 encoded:", frame_base64[:100]
        )  # Hanya tampilkan sebagian pertama base64

        # Data yang dikirim melalui MQTT
        payload = {"objects": detected_objects, "frame": frame_base64}

        # Kirim data ke MQTT
        mqtt.publish("object-detection/results", json.dumps(payload).encode("utf-8"))
        print(f"Data sent to MQTT: {json.dumps(payload)}")

        # # Tampilkan frame secara lokal
        # for obj in detected_objects:
        #     x1, y1, x2, y2 = obj["bbox"]
        #     label = f"{obj['class']} ({obj['confidence']:.2f})"
        #     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #     cv2.putText(
        #         frame,
        #         label,
        #         (x1, y1 - 10),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         0.5,
        #         (0, 255, 0),
        #         2,
        #     )

        # Delay untuk mengurangi beban CPU
        # time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# Fungsi utama untuk menjalankan aplikasi Flask dan MQTT
if __name__ == "__main__":
    # Mulai MQTT loop di thread terpisah
    mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
    mqtt_thread.start()

    # Jalankan deteksi objek di thread terpisah
    detect_thread = threading.Thread(target=detect_objects, daemon=True)
    detect_thread.start()

    # Jalankan aplikasi Flask di thread utama
    app.run(
        port=5000, debug=True, use_reloader=False
    )  # Gunakan `use_reloader=False` untuk mencegah Flask menjalankan dua thread
