import React, { useEffect, useRef, useState } from "react";
import { connectToMQTT } from "../mqttConfig";

const ObjectDetectionViewer = () => {
  const canvasRef = useRef(null);
  const [frame, setFrame] = useState(null);

  useEffect(() => {
    // Koneksi ke MQTT dan terima frame dari backend
    const mqttClient = connectToMQTT((data) => {
      setFrame(data.frame); // Simpan frame yang sudah diolah dari backend
    });

    return () => mqttClient.end(); // Tutup koneksi MQTT saat komponen di-unmount
  }, []);

  useEffect(() => {
    if (frame) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      const img = new Image();

      img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Bersihkan canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // Tampilkan frame
      };

      img.src = `data:image/jpeg;base64,${frame}`; // Atur source dari base64 image
    }
  }, [frame]);

  return (
    <div>
      <h2>Object Detection Viewer</h2>
      <canvas ref={canvasRef} width="640" height="480" />
    </div>
  );
};

export default ObjectDetectionViewer;
