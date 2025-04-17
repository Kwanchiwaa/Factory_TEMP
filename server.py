import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT Setup
mqtt_broker = "b4e111cfdc1c405ba7d73351938d025f.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "Kwanchiwa"
mqtt_pass = "Preaw1993"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_user, mqtt_pass)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

# Callback สำหรับรับข้อมูลจาก MQTT
def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode()}")
    data = {'topic': msg.topic, 'message': msg.payload.decode()}
    socketio.emit('sensor_data', data)  # ส่งข้อมูลไปยัง client ที่เชื่อมต่อ

# Subscribe to topics
mqtt_client.subscribe("sensor/temperature")
mqtt_client.subscribe("sensor/humidity")
mqtt_client.subscribe("sensor/pm25")

mqtt_client.on_message = on_message
mqtt_client.loop_start()  # เริ่มรับข้อมูลจาก MQTT

@app.route('/')
def index():
    return render_template('index.html')  # เรียกใช้หน้า index.html

if __name__ == '__main__':
    # ใช้ PORT ที่ Render กำหนดให้
    port = os.getenv('PORT', 5000)  
    socketio.run(app, host="0.0.0.0", port=port)
