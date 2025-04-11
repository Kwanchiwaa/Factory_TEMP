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
@app.route("/dashboard")
def dashboard():
    html = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Factory Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.5.1/dist/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-image: url('https://lirp.cdn-website.com/4246b69b/dms3rep/multi/opt/311481437_5917190921659614_5496119210462098327_n-640w.jpg');
            background-size: cover;   /* ให้ภาพขยายเต็มหน้าจอ */
            background-position: center center;  /* จัดภาพให้อยู่ตรงกลาง */
        }

        .gauge-container {
            width: 300px;
            display: inline-block;
            margin: 20px;
        }

        #chartContainer {
            width: 70%;
            margin: auto;
        }

        .val-text {
            font-size: 20px;
            margin-top: 10px;
        }

        #uploadBg {
            margin: 20px;
            padding: 5px;
        }
    </style>
</head>
<body>
    <h1>Smart Factory Dashboard</h1>

    <div class="gauge-container">
        <h3>Temperature</h3>
        <div id="tempVal" class="val-text">-- °C</div>
    </div>

    <div class="gauge-container">
        <h3>Humidity</h3>
        <div id="humVal" class="val-text">-- %</div>
    </div>

    <div class="gauge-container">
        <h3>PM2.5</h3>
        <div id="pmVal" class="val-text">-- µg/m³</div>
    </div>

    <div id="chartContainer">
        <canvas id="sensorChart"></canvas>
    </div>

    <!-- ตัวเลือกอัพโหลดภาพพื้นหลัง -->
    <input type="file" id="uploadBg" accept="image/*">

    <script>
        // เชื่อมต่อกับเซิร์ฟเวอร์ผ่าน socket.io
        const socket = io.connect('http://localhost:5000');

        // ตัวแปรสำหรับเก็บข้อมูลล่าสุดที่รับจากเซ็นเซอร์
        let temperatureData = [];
        let humidityData = [];
        let pmData = [];

        // สร้างกราฟด้วย Chart.js
        const ctx = document.getElementById('sensorChart').getContext('2d');
        const sensorChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],  // เวลา หรือช่วงเวลาที่ข้อมูลถูกบันทึก
                datasets: [{
                    label: 'Temperature (°C)',
                    data: temperatureData,
                    borderColor: 'rgb(255, 99, 132)',
                    fill: false
                }, {
                    label: 'Humidity (%)',
                    data: humidityData,
                    borderColor: 'rgb(54, 162, 235)',
                    fill: false
                }, {
                    label: 'PM2.5 (µg/m³)',
                    data: pmData,
                    borderColor: 'rgb(75, 192, 192)',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // เมื่อรับข้อมูลจาก server ผ่าน socket.io
        socket.on('sensor_update', (data) => {
            const temp = data.temperature || 0;
            const hum = data.humidity || 0;
            const pm = data.pm || 0;
            const time = Date.now();

            // แสดงผลข้อมูลในตัวเลข
            document.getElementById("tempVal").innerText = `${temp} °C`;
            document.getElementById("humVal").innerText = `${hum} %`;
            document.getElementById("pmVal").innerText = `${pm} µg/m³`;

            // เพิ่มข้อมูลใหม่ในกราฟ
            sensorChart.data.labels.push(time);  // เพิ่มเวลา
            sensorChart.data.datasets[0].data.push(temp);  // อุณหภูมิ
            sensorChart.data.datasets[1].data.push(hum);  // ความชื้น
            sensorChart.data.datasets[2].data.push(pm);   // PM2.5

            // กำหนดให้กราฟไม่เก็บข้อมูลเกินไป (รักษาขนาดของกราฟให้เหมาะสม)
            if (sensorChart.data.labels.length > 50) {
                sensorChart.data.labels.shift();
                sensorChart.data.datasets.forEach(dataset => dataset.data.shift());
            }

            sensorChart.update();
        });

        // ฟังก์ชันอัพโหลดรูปภาพพื้นหลัง
        document.getElementById('uploadBg').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    document.body.style.backgroundImage = `url(${event.target.result})`;
                };
                reader.readAsDataURL(file);
            }
        });

        // ฟังก์ชันให้กราฟอัพเดตทุกๆ 1 นาที
        setInterval(() => {
            socket.emit('request_sensor_data');  // ส่งคำขอให้เซิร์ฟเวอร์ส่งข้อมูลใหม่
        }, 60000);  // ทุกๆ 60000 มิลลิวินาที (1 นาที)
    </script>
</body>
</html>
