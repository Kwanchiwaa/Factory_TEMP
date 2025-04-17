from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT config
mqtt_broker = "b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "Kwanchiwa"
mqtt_pass = "Preaw1993"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("sensor/#")

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    data = {
        "topic": msg.topic,
        "value": msg.payload.decode()
    }
    socketio.emit("sensor_data", data)

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_user, mqtt_pass)
mqtt_client.tls_set()  # SSL
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)

