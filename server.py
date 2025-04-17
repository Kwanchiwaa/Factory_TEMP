from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# MQTT setup
mqtt_broker = "b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "Kwanchiwa"
mqtt_pass = "Preaw1993"
mqtt_topic = "sensor/#"

# Data storage
sensor_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "pm25": 0
}

# Callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global sensor_data
    payload = msg.payload.decode('utf-8')
    if msg.topic == "sensor/temperature":
        sensor_data["temperature"] = float(payload)
    elif msg.topic == "sensor/humidity":
        sensor_data["humidity"] = float(payload)
    elif msg.topic == "sensor/pm25":
        sensor_data["pm25"] = int(payload)

client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_pass)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
