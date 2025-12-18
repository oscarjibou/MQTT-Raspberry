import os
import json
import time
import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --------- Configuración desde ENV ---------
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "Tfg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "TFG")

MQTT_BROKER = os.getenv("MQTT_HOST", "192.168.2.50")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "test/ejemplo/json")

if not INFLUXDB_TOKEN:
    raise SystemExit("Falta INFLUXDB_TOKEN en variables de entorno")

# --------- Inicializar InfluxDB ---------
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[MQTT] Conectado rc={rc} a {MQTT_BROKER}:{MQTT_PORT}")
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Suscrito a topic: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8", errors="replace")

    try:
        data = json.loads(payload_str)

        src = data.get("src")
        seq = data.get("seq")
        ttl = data.get("ttl")
        lat = data.get("lat")
        lon = data.get("lon")
        state = data.get("state")
        rssi = data.get("rssi")

        node_id = "unknown" if src is None else str(src)

        points = []

        # Measurement: gps
        gps = Point("gps").tag("node_id", node_id).tag("topic", msg.topic)
        if lat is not None:   gps = gps.field("lat", float(lat))
        if lon is not None:   gps = gps.field("lon", float(lon))
        if seq is not None:   gps = gps.field("seq", int(seq))
        if ttl is not None:   gps = gps.field("ttl", int(ttl))
        if rssi is not None: gps = gps.field("rssi", int(rssi))
        points.append(gps)

        # Measurement: eventos (solo si hay rssi)
        if state is not None:
            eventos = Point("eventos").tag("node_id", node_id).field("state", float(state))
            points.append(eventos)

        write_api.write(bucket=INFLUXDB_BUCKET, record=points)
        print(data)

    except json.JSONDecodeError:
        print(f"[WARN] No JSON válido: {payload_str}")
    except Exception as e:
        print(f"[ERROR] {e} payload={payload_str}")

def main():
    # Esperar a que InfluxDB responda (primer arranque puede tardar)
    for _ in range(60):
        try:
            influx_client.ping()
            print("[InfluxDB] OK (ping)")
            break
        except Exception:
            time.sleep(1)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()

