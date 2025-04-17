from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MQTT Config
MQTT_BROKER = "b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "Kwanchiwa"
MQTT_PASS = "Preaw1993"
MQTT_TOPIC = "sensor/#"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"Received: {topic} -> {payload}")

    # ส่งข้อมูลเข้า Socket.IO
    socketio.emit('sensor_data', {'topic': topic, 'value': payload})

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

# SSL แบบไม่เช็ค cert (เฉพาะทดสอบ)
client.tls_set()
client.tls_insecure_set(True)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
