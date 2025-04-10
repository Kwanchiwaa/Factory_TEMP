import time
import dht
import ujson
from machine import Pin, UART
from umqtt.simple import MQTTClient
import network

# เชื่อมต่อ WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('P', 'PPPPPPPP')
while not wifi.isconnected():
    time.sleep(1)

# MQTT setup
mqtt_server = "1883"
mqtt_topic = "factory/sensor"
client_id = "esp32_pub"

client = MQTTClient(client_id, mqtt_server)
client.connect()

# Sensor setup
dht_sensor = dht.DHT11(Pin(4))
uart = UART(2, baudrate=9600, tx=17, rx=16)

def read_pm25():
    if uart.any():
        data = uart.read()
        if data and len(data) > 10:
            return int.from_bytes(data[2:4], 'big')  # ค่า PM2.5
    return None

while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        pm25 = read_pm25() or 0

        payload = ujson.dumps({
            "temperature": temp,
            "humidity": hum,
            "pm25": pm25
        })

        client.publish(mqtt_topic, payload)
        print("Published:", payload)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)