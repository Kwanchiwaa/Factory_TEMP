from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import ssl
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # รองรับ cross-origin

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code", rc)
    client.subscribe("factory/sensor")  # ใช้ topic เดิม

def on_message(client, userdata, msg):
    try:
        mqtt_data = json.loads(msg.payload.decode())
        print("Received:", mqtt_data)
        socketio.emit('sensor_update', mqtt_data)  # ส่ง real-time ไปหน้าเว็บ
    except Exception as e:
        print("Failed to decode MQTT message:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
mqtt_client.tls_insecure_set(True)

mqtt_client.connect("b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud", 8883, 60)
mqtt_client.loop_start()

@app.route("/")
def dashboard():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
