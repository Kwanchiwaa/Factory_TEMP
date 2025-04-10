from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import ssl
import json

app = Flask(__name__)
mqtt_data = {"temperature": 0, "humidity": 0, "pm25": 0}

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code", rc)
    client.subscribe("factory/sensor")  # เปลี่ยน topic ตามที่ ESP32 publish

def on_message(client, userdata, msg):
    global mqtt_data
    try:
        mqtt_data = json.loads(msg.payload.decode())
        print("Received:", mqtt_data)
    except Exception as e:
        print("Failed to decode MQTT message:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# ตั้งค่า TLS สำหรับเชื่อมต่อแบบปลอดภัย
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
mqtt_client.tls_insecure_set(True)  # ไม่ตรวจสอบใบรับรอง (เฉพาะตอนทดสอบเท่านั้น)

# เชื่อมต่อ MQTT Broker (HiveMQ Cloud)
mqtt_client.connect("b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud", 8883, 60)
mqtt_client.loop_start()

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(mqtt_data)

# ไม่ต้องใช้ app.run() เมื่อใช้ Gunicorn
if __name__ == "__main__":
    pass
