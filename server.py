from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
mqtt_data = {"temperature": 0, "humidity": 0, "pm25": 0}

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code", rc)
    client.subscribe("factory/sensor")

def on_message(client, userdata, msg):
    global mqtt_data
    mqtt_data = json.loads(msg.payload.decode())
    print("Received:", mqtt_data)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("broker.hivemq.com", 1883)
mqtt_client.loop_start()

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(mqtt_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)