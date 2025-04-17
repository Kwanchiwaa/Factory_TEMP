from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # เปิดให้ MQTT หรือ client อื่นเชื่อมได้

@app.route('/')
def index():
    return render_template('index.html')

# endpoint รับ MQTT หรือ sensor ส่งข้อมูลมา
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    print("Received data:", data)
    # broadcast ไปให้ทุก client ที่เปิดหน้าเว็บอยู่
    socketio.emit('sensor_data', data)
    return {"status": "ok"}

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
